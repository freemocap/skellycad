"""Retain the scan surface and add a smooth internal core and orbital backing.

Source: [@marmosetCtFemale100; @zimmermannRollin2025Apparatus].
Geometry choices are local print modifications, not anatomical reconstructions.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
import manifold3d as mf
from scipy import sparse
from scipy import ndimage
from skimage.measure import marching_cubes
from check_defects import ROOT, OUT, SOURCE, source

HASH='a77680b8dad5041ad0b0fd95f0a491abe6109adc3fc2ee702ca1a2202b081f6f'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def solid(mesh):
    result=mf.Manifold(mf.Mesh(np.array(mesh.vertices,dtype=np.float32),np.array(mesh.faces,dtype=np.uint32)))
    assert result.status()==mf.Error.NoError,result.status()
    return result

def mesh(s):
    assert s.status()==mf.Error.NoError,s.status()
    data=s.to_mesh()
    return trimesh.Trimesh(data.vert_properties[:,:3],data.tri_verts,process=True)

def ellipsoid(center,radii,subdivisions=5):
    obj=trimesh.creation.icosphere(subdivisions=subdivisions)
    obj.vertices=obj.vertices*np.array(radii)+center
    return obj

def cap_source(src):
    # The only open boundaries are at the scan's truncated neck end. Temporary
    # caps lie wholly inside the neck cutter and cannot survive in the result.
    edges=src.edges_unique[np.bincount(src.edges_unique_inverse)==1]
    assert np.allclose(src.vertices[edges][:,:,2],src.bounds[0,2])
    graph={}
    for a,b in edges:
        graph.setdefault(int(a),[]).append(int(b));graph.setdefault(int(b),[]).append(int(a))
    vertices=src.vertices.tolist(); faces=src.faces.tolist();seen=set();caps=[]
    boundary={tuple(sorted(e)) for e in edges}
    directed=[e for e in src.edges if tuple(sorted(e)) in boundary]
    directed_by_vertex={int(a):int(b) for a,b in directed}
    for start in graph:
        if start in seen:continue
        loop=[];v=start
        while v not in seen:
            seen.add(v);loop.append(v);v=directed_by_vertex[v]
        center=src.vertices[loop].mean(axis=0);idx=len(vertices);vertices.append(center.tolist());caps.extend(src.vertices[loop]);caps.append(center)
        for a in loop:faces.append([directed_by_vertex[a],a,idx])
    return trimesh.Trimesh(vertices,faces,process=True),np.array(caps)

def brain_core(src):
    center=np.array([0.,25.,12.])
    sphere=trimesh.creation.icosphere(subdivisions=4)
    directions=sphere.vertices
    locations,rays,_=src.ray.intersects_location(np.tile(center,(len(directions),1)),directions,multiple_hits=True)
    distances=np.linalg.norm(locations-center,axis=1)
    expected=1/np.sqrt(((directions/np.array([12.,8.,18.]))**2).sum(axis=1))
    inner=np.full(len(directions),np.nan);outer=inner.copy()
    for i in range(len(directions)):
        ds=np.sort(distances[rays==i]);ds=ds[ds>expected[i]*.45]
        if len(ds) and ds[0]<expected[i]*1.35:
            inner[i]=ds[0]
            if len(ds)>1 and ds[1]-ds[0]>.25:outer[i]=ds[1]
    missing=np.isnan(inner)
    radius=np.where(missing,expected,inner)
    adjacency=sparse.coo_matrix((np.ones(len(sphere.edges)),(sphere.edges[:,0],sphere.edges[:,1])),shape=(len(directions),)*2).tocsr()
    adjacency=adjacency+adjacency.T
    adjacency=sparse.diags(1/np.asarray(adjacency.sum(axis=1)).ravel())@adjacency
    # Interpolate openings through neighbouring directions, avoiding axis planes.
    for _ in range(30):radius[missing]=(adjacency@radius)[missing]
    for _ in range(5):radius=.65*radius+.35*(adjacency@radius)
    radius+=.45
    # Where both inner and outer cortex were hit, keep the core within the wall.
    valid=np.isfinite(outer)&(outer>inner+.4)
    radius[valid]=np.minimum(radius[valid],outer[valid]-.15)
    sphere.vertices=center+directions*radius[:,None]
    sphere.fix_normals()
    return sphere,dict(center_mm=center.tolist(),directions=len(directions),interpolated_opening_rays=int(missing.sum()),radial_overlap_mm=.45)

def stats(m):return dict(triangles=len(m.faces),vertices=len(m.vertices),components=len(m.split(only_watertight=False)),euler=int(m.euler_number),watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),volume_mm3=float(m.volume),bounds_mm=m.bounds.tolist())

def orbital_fill(base):
    """Close small orbital-wall holes additively; never cut the original rim."""
    pitch=.18;radius=1.2
    print('Constructing local additive orbital repair',flush=True)
    vox=base.voxelized(pitch).fill()
    a=np.pad(vox.matrix,12);origin=vox.transform[:3,3]-12*pitch
    dilated=ndimage.distance_transform_edt(~a)*pitch<=radius
    closed=ndimage.distance_transform_edt(dilated)*pitch>radius
    closed=ndimage.binary_fill_holes(closed)
    field=ndimage.gaussian_filter(closed.astype(np.float32),sigma=.65)
    v,f,_,_=marching_cubes(field,.65,spacing=(pitch,)*3)
    envelope=trimesh.Trimesh(v+origin,f,process=True);envelope.fix_normals()
    envelope=max(envelope.split(only_watertight=False),key=lambda m:abs(m.volume))
    envelope_solid=solid(envelope)
    masks=[dict(center_mm=[side*7.,23.,21.],radii_mm=[7.,7.,8.]) for side in [-1,1]]
    addition=None
    for spec in masks:
        local=envelope_solid^solid(ellipsoid(spec['center_mm'],spec['radii_mm']))
        addition=local if addition is None else addition+local
    mesh(addition).export(OUT/'orbital-fill.stl')
    return addition,dict(voxel_pitch_mm=pitch,closing_radius_mm=radius,gaussian_sigma_voxels=.65,isosurface_level=.65,masks=masks,operation='Union only; no subtraction from the orbital rims or socket walls')

def main():
    assert sha(SOURCE)==HASH
    OUT.mkdir(parents=True,exist_ok=True)
    src=source();closed,caps=cap_source(src)
    neck_center=np.array([0.,6.,-8.]);neck_radii=np.array([11.,12.,13.])
    assert ((((caps-neck_center)/neck_radii)**2).sum(axis=1)<1).all(), 'Temporary caps must be removed completely'
    print('Source closed',stats(closed),flush=True)
    skull=solid(closed)-solid(ellipsoid(neck_center,neck_radii))
    preserved=mesh(skull);preserved.export(OUT/'source-neck-removed.stl')
    print('Constructing radial braincase fill',flush=True)
    core,core_info=brain_core(src);core.export(OUT/'internal-core.stl')
    result=skull+solid(core)
    base=mesh(result)
    base=max(base.split(only_watertight=False),key=lambda m:abs(m.volume))
    eye_fill,eye_info=orbital_fill(base)
    result=solid(base)+eye_fill
    detailed=mesh(result)
    # Remove enclosed cavity shells and small disconnected source remnants.
    parts=detailed.split(only_watertight=False)
    detailed=max(parts,key=lambda m:abs(m.volume));detailed.fix_normals()
    detailed.export(OUT/'marmoset-skull-detailed-r02.stl')
    assert detailed.is_watertight and detailed.is_winding_consistent
    print('Detailed',stats(detailed),flush=True)
    # A geometric tolerance, not a hard face budget. Keep the original surface
    # except where it can be simplified within 0.025 mm by Manifold.
    simplification_attempts=[]
    for tolerance in [.025,.015,.008,0.]:
        reduced=mesh(solid(detailed).simplify(tolerance)) if tolerance else detailed
        reduced.export(OUT/'marmoset-skull-print-r02.stl')
        saved=trimesh.load(OUT/'marmoset-skull-print-r02.stl')
        info=stats(saved);simplification_attempts.append(dict(tolerance_mm=tolerance,**info))
        if info['watertight'] and info['winding_consistent'] and info['components']==1 and info['euler']==detailed.euler_number:break
    else:raise AssertionError('No topology-preserving export')
    print('Print',stats(saved),flush=True)
    report=dict(revision='ET-MARMOSET-SKULL-PRINT-R02',source_sha256=HASH,units='mm assumed; source coordinates unchanged',core=core_info,neck=dict(center_mm=neck_center.tolist(),radii_mm=neck_radii.tolist()),orbital_fill=eye_info,simplification_tolerance_mm=tolerance,simplification_attempts=simplification_attempts,discarded_shells=len(parts)-1,outputs={})
    for name in ['marmoset-skull-detailed-r02.stl','marmoset-skull-print-r02.stl']:
        path=OUT/name;obj=trimesh.load(path)
        report['outputs'][name]=dict(sha256=sha(path),bytes=path.stat().st_size,**stats(obj))
    (OUT/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
