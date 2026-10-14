"""Recover the user's rigid frame from corresponding low-poly STL triangles.

No remeshing, scaling, repair or ICP. Fail if ordered correspondence no longer
supports a rigid transform. Method: [@lawrenceBernalWitzgall2019].
"""
from pathlib import Path
import hashlib
import json
import struct
import numpy as np
import trimesh
from scipy.spatial import cKDTree

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
OUT=ROOT/'generated/eye-tracker/rat/skull-aligned-r01'
DTYPE=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(path):
    raw=path.read_bytes()
    count=struct.unpack('<I',raw[80:84])[0]
    if len(raw)!=84+50*count:
        raise ValueError('Expected a binary STL: '+str(path))
    return np.frombuffer(raw,dtype=DTYPE,offset=84).copy()


def rigid_fit(a,b):
    if a.shape!=b.shape:
        raise ValueError('Ordered correspondences require equal shapes')
    x,y=a-a.mean(axis=0),b-b.mean(axis=0)
    u,s,vt=np.linalg.svd(x.T@y)
    if s[-1]/s[0]<1e-8:
        raise ValueError('Correspondences do not constrain a 3D rotation')
    r=vt.T@np.diag([1,1,np.linalg.det(vt.T@u.T)])@u.T
    t=b.mean(axis=0)-r@a.mean(axis=0)
    residual=np.linalg.norm(a@r.T+t-b,axis=1)
    if residual.max()>1e-4:
        raise ValueError('Not the same ordered mesh under a rigid transform')
    assert np.allclose(r.T@r,np.eye(3),atol=1e-12) and abs(np.linalg.det(r)-1)<1e-12
    return r,t,residual,float(np.sum((x@r.T)*y)/np.sum(x*x))


def surface_distances(query_mesh,reference_mesh,seed):
    """Area-weighted sample to exact reference triangles; diagnostic, not a fit."""
    rng=np.random.default_rng(seed)
    indices=rng.choice(len(query_mesh.faces),size=512,p=query_mesh.area_faces/query_mesh.area)
    uv=rng.random((512,2))
    uv[uv.sum(axis=1)>1]=1-uv[uv.sum(axis=1)>1]
    tri=query_mesh.triangles[indices]
    points=tri[:,0]+uv[:,0,None]*(tri[:,1]-tri[:,0])+uv[:,1,None]*(tri[:,2]-tri[:,0])
    triangles=reference_mesh.triangles
    centers=triangles.mean(axis=1)
    max_radius=np.linalg.norm(triangles-centers[:,None,:],axis=2).max()
    center_tree=cKDTree(centers)
    upper=cKDTree(reference_mesh.vertices).query(points)[0]
    distances=[]
    for point,bound in zip(points,upper):
        candidates=center_tree.query_ball_point(point,bound+max_radius+1e-9)
        closest=trimesh.triangles.closest_point(triangles[candidates],np.tile(point,(len(candidates),1)))
        distances.append(np.linalg.norm(closest-point,axis=1).min())
    return dict(samples=512,median_mm=float(np.median(distances)),
                p95_mm=float(np.percentile(distances,95)),max_sample_mm=float(np.max(distances)))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    prov=json.loads((HERE/'provenance.json').read_text())
    source_dir=HERE/'thingiverse-469391/files'
    low=source_dir/'9_19_14_rat_skull-simplified-2.stl'
    target=HERE/'rat-skull-low-poly-aligned.stl'
    a=records(low)['vertices'].reshape(-1,3).astype(float)
    b=records(target)['vertices'].reshape(-1,3).astype(float)
    # Solve on alternating faces; test the untouched half before final all-point fit.
    train=np.repeat(np.arange(len(a)//3)%2==0,3)
    r0,t0,_,_=rigid_fit(a[train],b[train])
    holdout=np.linalg.norm(a[~train]@r0.T+t0-b[~train],axis=1)
    assert holdout.max()<1e-4
    r,t,residual,scale=rigid_fit(a,b)
    transform=np.eye(4);transform[:3,:3]=r;transform[:3,3]=t
    old=np.array([[1,0,0,12],[0,0,-1,-2],[0,1,0,0],[0,0,0,1]],float)
    files=[('low-poly','9_19_14_rat_skull-simplified-2.stl'),
           ('standard','9_19_14_rat_skull.stl'),('high-res','Rat_skull+mandible_high_res.stl')]
    reports={}
    for name,filename in files:
        source=source_dir/filename
        expected=next(v['sha256'] for v in prov['unmodified_files'] if v['path'].endswith('/'+filename))
        assert sha(source)==expected
        data=records(source)
        original=data['vertices'].astype(float)
        data['vertices']=original@r.T+t
        data['normal']=data['normal'].astype(float)@r.T
        output=OUT/f'rat-skull-{name}-aligned-r01.stl'
        header=b'SkellyCAD rigid aligned-r01; see alignment.json'.ljust(80,b' ')
        output.write_bytes(header+struct.pack('<I',len(data))+data.tobytes())
        check=records(output)
        reconstructed=(check['vertices'].astype(float)-t)@r
        roundtrip=np.linalg.norm(reconstructed-original,axis=2).max()
        edge_before=np.linalg.norm(original-np.roll(original,1,axis=1),axis=2)
        edge_after=np.linalg.norm(check['vertices'].astype(float)-np.roll(check['vertices'].astype(float),1,axis=1),axis=2)
        assert roundtrip<5e-6 and np.max(np.abs(edge_before-edge_after))<5e-6
        assert len(check)==len(data) and np.array_equal(check['attribute'],records(source)['attribute'])
        mesh=trimesh.load_mesh(source,process=True)
        dest=trimesh.load_mesh(output,process=True)
        assert mesh.is_watertight==dest.is_watertight
        assert mesh.euler_number==dest.euler_number
        reports[name]=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),
            output=output.name,output_sha256=sha(output),triangles=len(data),
            watertight=bool(dest.is_watertight),euler_number=int(dest.euler_number),
            max_inverse_error_mm=float(roundtrip),max_edge_length_change_mm=float(np.max(np.abs(edge_before-edge_after))),
            bounds_mm=dest.bounds.tolist())
    low_mesh=trimesh.load_mesh(low,process=True)
    for name,filename in files[1:]:
        other=trimesh.load_mesh(source_dir/filename,process=True)
        reports[name]['source_frame_surface_comparison']={
            'dense_to_low':surface_distances(other,low_mesh,12),
            'low_to_dense':surface_distances(low_mesh,other,13),
            'meaning':'Pre-existing surface differences in source coordinates; rigidly invariant, not alignment-fit error. Sampled maxima are not Hausdorff distances.'}
    report=dict(revision='skull-aligned-r01',units='mm',
        frame={'x': 'rostral: toward nose','y':'animal left','z':'dorsal: through skull roof',
               'origin':'User-chosen approximate midpoint between eyeballs; preserved without recentering'},
        anchor=str(target.relative_to(ROOT)),anchor_sha256=sha(target),
        correspondence='Same ordered triangle corners; 24550 triangles, 73650 point pairs',
        method='Kabsch proper rigid fit; no scaling or reflection [@lawrenceBernalWitzgall2019]',
        mapping='column vectors: p_aligned = T_source_to_aligned @ [p_source,1]',
        source_to_aligned=transform.tolist(),aligned_to_source=np.linalg.inv(transform).tolist(),
        old_assembly_to_aligned=(transform@np.linalg.inv(old)).tolist(),
        scale_applied=1.0,diagnostic_best_scale=scale,rotation_determinant=float(np.linalg.det(r)),
        rms_fit_error_mm=float(np.sqrt(np.mean(residual**2))),max_fit_error_mm=float(residual.max()),
        holdout_max_error_mm=float(holdout.max()),
        source_license=prov['license_as_supplied'],source_attribution=prov['creator']+'; '+prov['source_url'],
        variants=reports)
    (OUT/'alignment.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
