"""Build an independent print derivative; all coordinates are assumed mm."""
from pathlib import Path
import hashlib, json, shutil
import numpy as np
import trimesh
import manifold3d
from scipy import ndimage
from scipy.spatial import ConvexHull
from skimage.measure import marching_cubes
from matplotlib.path import Path as Polygon

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'generated/eye-tracker/rat/skull-print-r01'
SOURCE=ROOT/'designs/eye-tracker/rat/references/skull/aligned-r01/rat-skull-standard-aligned-r01.stl'
PITCH=.15

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stats(m):
 return dict(triangles=len(m.faces),components=len(m.split(only_watertight=False)),watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),volume_mm3=float(m.volume),bounds_mm=m.bounds.tolist())

def rebuild(mesh, brain=False):
 vox=mesh.voxelized(PITCH).fill()
 a=np.pad(vox.matrix,5); origin=vox.transform[:3,3]-5*PITCH
 before=a.copy()
 if brain:
  # Chosen print closure envelope, inspected against coronal source sections.
  # Each local hull spans the braincase only, leaving lateral orbits untouched.
  for ix in range(a.shape[0]):
   x=origin[0]+ix*PITCH
   if not -23.7<=x<=3.5: continue
   floor=np.interp(x,[-24,-18,-15,-10,-5,0,3.5],[-2,-6,-5.8,-5,-3.5,-.5,3.5])
   width=np.interp(x,[-24,-20,-15,-10,-5,0,3.5],[2,7,8.7,8.5,6.2,4,1])
   yz=np.argwhere(a[ix]); coords=origin[1:]+yz*PITCH
   yz=yz[(coords[:,1]>=floor)&(np.abs(coords[:,0])<=width)]
   if len(yz)<4: continue
   hull=ConvexHull(yz)
   yy,zz=np.mgrid[yz[:,0].min():yz[:,0].max()+1,yz[:,1].min():yz[:,1].max()+1]
   pts=np.column_stack((yy.ravel(),zz.ravel()))
   inside=Polygon(yz[hull.vertices]).contains_points(pts,radius=.01)
   a[ix,pts[inside,0],pts[inside,1]]=True
 # Close submillimetre gaps and soften scan detail without global convexification.
 sphere=np.indices((7,7,7))-3
 structure=(sphere*sphere).sum(axis=0)<=9
 a=ndimage.binary_closing(a,structure=structure)
 a=ndimage.binary_fill_holes(a)
 field=ndimage.gaussian_filter(a.astype(np.float32),sigma=.65)
 v,f,_,_=marching_cubes(field,level=.45,spacing=(PITCH,)*3)
 result=trimesh.Trimesh(v+origin,f,process=True)
 result.fix_normals()
 result=max(result.split(only_watertight=False),key=lambda c:abs(c.volume))
 solid=manifold3d.Manifold(manifold3d.Mesh(np.asarray(result.vertices,dtype=np.float32),np.asarray(result.faces,dtype=np.uint32)))
 assert solid.status()==manifold3d.Error.NoError, solid.status()
 reduced=solid.simplify(.035).to_mesh()
 result=trimesh.Trimesh(reduced.vert_properties[:,:3],reduced.tri_verts,process=True)
 result.fix_normals()
 return result, int(np.count_nonzero(a&~before))*PITCH**3

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((ROOT/'designs/eye-tracker/rat/active-model.json').read_text())
 assert sha(ROOT/manifest['native_checkpoint'])==manifest['native_sha256']
 source_hash=sha(SOURCE)
 assert source_hash=='06216589919dd73774323e6c0ea934ed73d23e49015531a96a82c3f4ec515b1e'
 src=trimesh.load(SOURCE)
 parts=sorted(src.split(only_watertight=False),key=lambda c:len(c.faces),reverse=True)
 report=dict(revision='ET-RAT-SKULL-PRINT-R01',units='mm assumed; scale unchanged',source=str(SOURCE.relative_to(ROOT)),source_sha256=source_hash,selected_assembly=manifest['revision'],selected_checkpoint_sha256=manifest['native_sha256'],pitch_mm=PITCH,removed_fragments=len(parts)-2,removed_fragment_volume_mm3=sum(abs(c.volume) for c in parts[2:]),source_mesh=stats(src),outputs={})
 for name,part,brain in [('rat-skull-solid-r01',parts[0],True),('rat-mandible-clean-r01',parts[1],False)]:
  print('Building',name,flush=True)
  mesh,added=rebuild(part,brain)
  path=OUT/(name+'.stl');mesh.export(path)
  reloaded=trimesh.load(path)
  info=stats(reloaded)
  assert info['watertight'] and info['winding_consistent'] and info['components']==1 and info['volume_mm3']>0
  report['outputs'][name]=dict(**info,sha256=sha(path),net_voxel_addition_mm3=added)
 assert sha(SOURCE)==source_hash
 report['status']='Geometry validated; not sliced or physically printed. No hardware fit established.'
 (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 shutil.copy2(ROOT/'designs/eye-tracker/rat/references/skull/thingiverse-469391/LICENSE.txt',OUT/'LICENSE-source.txt')
 print(json.dumps(report,indent=2))
if __name__=='__main__': main()



