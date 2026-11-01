"""Preserve scan surfaces and boolean-union an inset braincase core."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
import trimesh,manifold3d as mf
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'generated/eye-tracker/rat/skull-print-r02'
SRC=ROOT/'designs/eye-tracker/rat/references/skull/aligned-r01/rat-skull-standard-aligned-r01.stl'
R01=ROOT/'generated/eye-tracker/rat/skull-print-r01/rat-skull-solid-r01.stl'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def solid(m):
 s=mf.Manifold(mf.Mesh(np.float32(m.vertices),np.uint32(m.faces)))
 assert s.status()==mf.Error.NoError,s.status()
 return s

def mesh(s):
 assert s.status()==mf.Error.NoError,s.status()
 a=s.to_mesh();return trimesh.Trimesh(a.vert_properties[:,:3],a.tri_verts,process=True)
def facekeys(m):
 return [tuple(sorted(tuple(v) for v in np.round(t,5))) for t in m.triangles]
def stats(m):
 return dict(triangles=len(m.faces),components=len(m.split(only_watertight=False)),watertight=bool(m.is_watertight),winding=bool(m.is_winding_consistent),volume_mm3=float(m.volume),bounds_mm=m.bounds.tolist())
def bridge(a,b,radius=1.1):
 delta=b-a;length=np.linalg.norm(delta);direction=delta/length
 t=trimesh.geometry.align_vectors([0,0,1],direction);t[:3,3]=(a+b)/2
 return trimesh.creation.cylinder(radius=radius,height=length+1.6,sections=48,transform=t)
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((ROOT/'designs/eye-tracker/rat/active-model.json').read_text())
 assert sha(ROOT/manifest['native_checkpoint'])==manifest['native_sha256']
 assert sha(SRC)=='06216589919dd73774323e6c0ea934ed73d23e49015531a96a82c3f4ec515b1e'
 assert sha(R01)=='2ea4812284d7856d906a8a55814e7d7288184678938dd817594894fc45a4caf3'
 original=trimesh.load(SRC);parts=sorted(original.split(),key=lambda c:len(c.faces),reverse=True);skull,jaw=parts[:2]
 print('Creating inset internal core',flush=True)
 vox=trimesh.load(R01).voxelized(.15).fill();a=np.pad(vox.matrix,5);origin=vox.transform[:3,3]-.75
 distance=ndimage.distance_transform_edt(a)*.15
 core=distance>.70
 xs=origin[0]+np.arange(core.shape[0])*.15
 core[xs>3.5]=False
 v,f,_,_=marching_cubes(core.astype(np.float32),.5,spacing=(.15,)*3)
 c=trimesh.Trimesh(v+origin,f,process=True);c.fix_normals();c=max(c.split(),key=lambda x:abs(x.volume))
 c=mesh(solid(c).simplify(.04));c.export(OUT/'internal-core.stl')
 result=solid(skull)+solid(c)
 detail=mesh(result)
 # An enclosed void is represented by an independent inward-facing shell.
 shells=detail.split(only_watertight=False)
 internal=[s for s in shells if s.volume<0]
 if internal: detail=trimesh.util.concatenate([s for s in shells if s.volume>0]);result=solid(detail)
 print('Skull',stats(detail),flush=True)
 keys=set(facekeys(detail));keep=np.array([k in keys for k in facekeys(skull)])
 roof=(skull.triangles_center[:,2]>1)&(skull.face_normals[:,2]>.3)
 print('Exact roof faces',int(keep[roof].sum()),int(roof.sum()),flush=True)
 connectors=[];records=[]
 for sign in [-1,1]:
  sv=skull.vertices[(skull.vertices[:,0]<-7)&(skull.vertices[:,1]*sign>5)&(skull.vertices[:,2]<-1)]
  jv=jaw.vertices[(jaw.vertices[:,0]<-7)&(jaw.vertices[:,1]*sign>5)&(jaw.vertices[:,2]>-7)]
  distances,idx=cKDTree(sv).query(jv);i=int(np.argmin(distances));p,q=jv[i],sv[idx[i]]
  connectors.append(bridge(p,q));records.append(dict(side=sign,jaw_point_mm=p.tolist(),skull_point_mm=q.tolist(),gap_mm=float(distances[i]),radius_mm=1.1,endpoint_extension_mm=.8))
 fused=result+solid(jaw)
 for b in connectors:fused=fused+solid(b)
 combined=mesh(fused)
 report=dict(revision='ET-RAT-SKULL-PRINT-R02',source_sha256=sha(SRC),source=str(SRC.relative_to(ROOT)),core_lineage_r01_sha256=sha(R01),checkpoint_sha256=manifest['native_sha256'],units='mm assumed; no scale or pose change',removed_small_fragments=len(parts)-2,removed_enclosed_void_shells=len(internal),source_skull_triangles=len(skull.faces),exact_retained_source_skull_triangles=int(keep.sum()),protected_roof_triangles=int(roof.sum()),exact_retained_roof_triangles=int(keep[roof].sum()),bridges=records,outputs={})
 for name,m in [('rat-skull-detailed-solid-r02',detail),('rat-skull-mandible-fused-r02',combined),('rat-mandible-original-detail-r02',jaw)]:
  path=OUT/(name+'.stl');m.export(path);saved=trimesh.load(path);info=stats(saved)
  assert info['watertight'] and info['winding'] and info['components']==1 and info['volume_mm3']>0,info
  report['outputs'][name]=dict(**info,sha256=sha(path))
 (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()

