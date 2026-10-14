"""Optional rigid overlap refinement; retain the exact common-transform export.

The high_res source has an apparent offset relative to the standard source.
This separate candidate minimizes trimmed closest-sample distances. It does not
alter surfaces or replace the known low-poly-to-user transform.
"""
from pathlib import Path
import json
import struct
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from align_to_user_frame import HERE,ROOT,OUT,records,sha,surface_distances


def sample(mesh,count,seed):
    rng=np.random.default_rng(seed)
    tri=mesh.triangles[rng.choice(len(mesh.faces),count,p=mesh.area_faces/mesh.area)]
    uv=rng.random((count,2))
    mask=uv.sum(axis=1)>1
    uv[mask]=1-uv[mask]
    return tri[:,0]+uv[:,0,None]*(tri[:,1]-tri[:,0])+uv[:,1,None]*(tri[:,2]-tri[:,0])


def main():
    alignment=json.loads((OUT/'alignment.json').read_text())
    high_path=ROOT/alignment['variants']['high-res']['source']
    standard_path=ROOT/alignment['variants']['standard']['source']
    assert sha(high_path)==alignment['variants']['high-res']['source_sha256']
    assert sha(standard_path)==alignment['variants']['standard']['source_sha256']
    high=trimesh.load_mesh(high_path,process=True)
    standard=trimesh.load_mesh(standard_path,process=True)
    a=sample(high,12000,11)
    b=sample(standard,150000,10)
    tree=cKDTree(b)
    correction=np.eye(4)
    converged=False
    for iteration in range(100):
        distances,indices=tree.query(a)
        keep=distances<np.percentile(distances,85)
        aa,bb=a[keep],b[indices[keep]]
        u,s,vt=np.linalg.svd((aa-aa.mean(axis=0)).T@(bb-bb.mean(axis=0)))
        rotation=vt.T@np.diag([1,1,np.linalg.det(vt.T@u.T)])@u.T
        translation=bb.mean(axis=0)-rotation@aa.mean(axis=0)
        step=np.eye(4);step[:3,:3]=rotation;step[:3,3]=translation
        a=a@rotation.T+translation
        correction=step@correction
        change=float(np.max(np.linalg.norm(a-(a-translation)@rotation,axis=1)))
        if change<1e-7:
            converged=True
            break
    before=surface_distances(high,standard,91)
    before_reverse=surface_distances(standard,high,92)
    adjusted=high.copy();adjusted.apply_transform(correction)
    after=surface_distances(adjusted,standard,91)
    after_reverse=surface_distances(standard,adjusted,92)
    assert after['median_mm']<before['median_mm'] and after['p95_mm']<before['p95_mm']
    total=np.array(alignment['source_to_aligned'])@correction
    r,t=total[:3,:3],total[:3,3]
    data=records(high_path)
    original=data['vertices'].astype(float)
    data['vertices']=original@r.T+t
    data['normal']=data['normal'].astype(float)@r.T
    path=OUT/'rat-skull-high-res-refined-aligned-r01.stl'
    path.write_bytes(b'SkellyCAD optional rigid refinement; see high-res-refinement.json'.ljust(80,b' ')+struct.pack('<I',len(data))+data.tobytes())
    saved=records(path)
    error=float(np.linalg.norm((saved['vertices'].astype(float)-t)@r-original,axis=2).max())
    assert error<5e-6 and abs(np.linalg.det(r)-1)<1e-10
    assert np.array_equal(saved['attribute'],records(high_path)['attribute'])
    report=dict(status='Optional overlap-refined candidate; exact common-transform version retained separately',
                method='Deterministic area sampling, nearest-sample matching, 85% trimmed proper rigid SVD updates; no scale',
                source_sha256=sha(high_path),reference_sha256=sha(standard_path),
                source_to_standard_correction=correction.tolist(),source_to_aligned=total.tolist(),
                iterations=iteration+1,converged=converged,last_max_step_mm=change,
                held_out_surface_distances={'high_to_standard_before':before,'high_to_standard_after':after,
                    'standard_to_high_before':before_reverse,'standard_to_high_after':after_reverse},
                caveat='Distances use independent 512-point surface samples. Surfaces differ; maxima are not Hausdorff distances. No anatomical landmark validation.',
                triangles=len(data),scale_applied=1.,max_inverse_error_mm=error,
                output=path.name,output_sha256=sha(path))
    (OUT/'high-res-refinement.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
