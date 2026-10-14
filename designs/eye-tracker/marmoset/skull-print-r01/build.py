"""Build a separate skull print derivative in the unchanged source frame.

Source provenance: [@marmosetCtFemale100; @zimmermannRollin2025Apparatus].
All millimetre dimensions are provisional: STL has no unit metadata.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import numpy as np
import trimesh
import manifold3d as mf
import fast_simplification
from scipy import ndimage
from scipy.spatial import ConvexHull
from skimage.measure import marching_cubes
from matplotlib.path import Path as Polygon

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT/'designs/eye-tracker/marmoset/references/skull/female_100months_403g.stl'
OUT = ROOT/'generated/eye-tracker/marmoset/skull-print-r01'
SOURCE_SHA = 'a77680b8dad5041ad0b0fd95f0a491abe6109adc3fc2ee702ca1a2202b081f6f'
PITCH = .15

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stats(mesh):
    return dict(triangles=len(mesh.faces), vertices=len(mesh.vertices),
                components=len(mesh.split(only_watertight=False)),
                watertight=bool(mesh.is_watertight),
                winding_consistent=bool(mesh.is_winding_consistent),
                volume_mm3=float(mesh.volume), bounds_mm=mesh.bounds.tolist())

def sphere(radius):
    grid=np.indices((radius*2+1,)*3)-radius
    return (grid*grid).sum(axis=0)<=radius*radius

def solid(mesh):
    result=mf.Manifold(mf.Mesh(np.float32(mesh.vertices), np.uint32(mesh.faces)))
    assert result.status()==mf.Error.NoError, result.status()
    return result

def main():
    assert sha(SOURCE)==SOURCE_SHA, 'Source hash mismatch; stop and review lineage.'
    OUT.mkdir(parents=True,exist_ok=True)
    original=trimesh.load(SOURCE)
    parts=sorted(original.split(only_watertight=False),key=lambda m:len(m.faces),reverse=True)
    skull=parts[0]
    print('Voxelizing main component at', PITCH, flush=True)
    vox=skull.voxelized(PITCH)
    occupied=np.pad(vox.matrix,6)
    origin=vox.transform[:3,3]-6*PITCH
    xs=origin[0]+np.arange(occupied.shape[0])*PITCH
    ys=origin[1]+np.arange(occupied.shape[1])*PITCH
    zs=origin[2]+np.arange(occupied.shape[2])*PITCH
    # User-requested neck removal. This local cut leaves the posterior skull
    # (higher Y) intact; it is an artificial print boundary, not a landmark.
    neck=(ys[None,:,None]<18)&(zs[None,None,:]<0)
    occupied &= ~neck
    print('Closing small gaps and filling posterior braincase',flush=True)
    occupied=ndimage.binary_closing(occupied,structure=sphere(2))
    occupied=ndimage.binary_fill_holes(occupied)
    before=occupied.copy()
    # Local section envelopes were chosen from this specimen, not population
    # anatomy. Protect the anterior face/orbits by raising the floor towards +Z.
    levels=[-8,-4,0,10,18,22,26,30,32]
    floors=[27,21,16,16,18,22,26,29,32]
    for iz,z in enumerate(zs):
        if not levels[0]<=z<=levels[-1]: continue
        floor=np.interp(z,levels,floors)
        ij=np.argwhere(occupied[:,:,iz])
        ij=ij[ys[ij[:,1]]>=floor]
        if len(ij)<4 or np.linalg.matrix_rank(ij-ij.mean(axis=0))<2: continue
        hull=ConvexHull(ij)
        xx,yy=np.mgrid[ij[:,0].min():ij[:,0].max()+1,ij[:,1].min():ij[:,1].max()+1]
        points=np.column_stack((xx.ravel(),yy.ravel()))
        inside=Polygon(ij[hull.vertices]).contains_points(points,radius=.01)
        occupied[points[inside,0],points[inside,1],iz]=True
    occupied=ndimage.binary_fill_holes(occupied)
    labels,count=ndimage.label(occupied)
    sizes=np.bincount(labels.ravel());sizes[0]=0
    occupied=labels==sizes.argmax()
    del labels
    np.savez_compressed(OUT/'construction-grid.npz',occupied=occupied,origin=origin,pitch=PITCH)
    field=ndimage.gaussian_filter(occupied.astype(np.float32),sigma=1.0)
    vertices,faces,_,_=marching_cubes(field,.43,spacing=(PITCH,)*3)
    mesh=trimesh.Trimesh(vertices+origin,faces,process=True)
    mesh.fix_normals()
    shells=mesh.split(only_watertight=False)
    mesh=max(shells,key=lambda m:abs(m.volume))
    print('Simplifying',len(mesh.faces),'triangles',flush=True)
    detailed=solid(mesh)
    reduced=detailed.simplify(.08)
    data=reduced.to_mesh()
    vertices,faces=fast_simplification.simplify(np.array(data.vert_properties[:,:3],dtype=np.float64,order='C',copy=True),np.array(data.tri_verts,dtype=np.int64,order='C',copy=True),target_count=100000,agg=5)
    # Normalize collapsed faces and split pinched topology before STL welding.
    normalized=mf.Manifold(mf.Mesh(np.float32(vertices),np.uint32(faces)))
    assert normalized.status()==mf.Error.NoError
    data=normalized.to_mesh()
    result=trimesh.Trimesh(data.vert_properties[:,:3],data.tri_verts,process=False)
    assert result.is_watertight
    # Five micrometres separate coincident surfaces at collapsed scan features.
    # This is an explicit engineering offset, not claimed anatomical precision.
    result.vertices += result.vertex_normals*.005
    path=OUT/'marmoset-skull-print-r01.stl'
    result.export(path)
    saved=trimesh.load(path)
    final_parts=sorted(saved.split(only_watertight=False),key=lambda m:abs(m.volume),reverse=True)
    # Decimation can separate sub-voxel slivers. Keep the skull solid only.
    saved=final_parts[0]
    saved.export(path)
    saved=trimesh.load(path)
    info=stats(saved)
    assert info['watertight'] and info['winding_consistent'] and info['components']==1 and info['volume_mm3']>0, info
    assert solid(saved).status()==mf.Error.NoError
    assert sha(SOURCE)==SOURCE_SHA
    report=dict(revision='ET-MARMOSET-SKULL-PRINT-R01',source=str(SOURCE.relative_to(ROOT)),source_sha256=SOURCE_SHA,
                units='mm assumed; original coordinates and scale 1.0 retained',selected_assembly=None,
                source_mesh=stats(original),removed_components=[dict(rank=i,**stats(m)) for i,m in enumerate(parts[1:],1)],
                parameters=dict(voxel_pitch_mm=PITCH,closing_radius_mm=.30,gaussian_sigma_voxels=1.0,isosurface_level=.43,
                                preliminary_simplification_tolerance_mm=.08,target_triangles=100000,decimation_aggression=5,final_normal_offset_mm=.005,neck_cut='Y < 18 and Z < 0',
                                core_Z_mm=levels,core_min_Y_mm=floors),
                filled_core_voxel_volume_mm3=int(np.count_nonzero(occupied & ~before))*PITCH**3,
                voxel_components_before_largest=count,discarded_surface_shells=len(shells)-1,
                discarded_final_slivers=len(final_parts)-1,
                discarded_final_sliver_volume_mm3=float(sum(abs(m.volume) for m in final_parts[1:])),
                output=dict(path=str(path.relative_to(ROOT)),sha256=sha(path),bytes=path.stat().st_size,**info),
                packages={p:importlib.metadata.version(p) for p in ['numpy','trimesh','scipy','scikit-image','manifold3d','matplotlib','rtree','fast-simplification']},
                status='Geometry checks passed; no slicing, physical print or hardware fit validation.')
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['output'],indent=2),flush=True)

if __name__=='__main__':main()
