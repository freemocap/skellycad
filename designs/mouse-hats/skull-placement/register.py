"""Recover the Blender mount pose in the native assembly frame, rigid only."""
from pathlib import Path
import itertools,json
import numpy as np
import trimesh
from scipy.spatial import cKDTree
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-placement'
def mesh(n):return trimesh.Trimesh(**json.loads((OUT/n).read_text()),process=False)
a=mesh('mount-0.json');b=mesh('native-baseplate.json')
x=np.unique(a.vertices,axis=0);y=np.unique(b.vertices,axis=0);tree=cKDTree(y)
cx,cy=x.mean(0),y.mean(0);_,ea=np.linalg.eigh(np.cov(x.T));_,eb=np.linalg.eigh(np.cov(y.T))
results=[]
for perm in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  r=ea@np.diag(signs)@eb[:,perm].T
  if np.linalg.det(r)<0:continue
  t=cy-cx@r
  for _ in range(80):
   moved=x@r+t;dist,idx=tree.query(moved);keep=dist<=np.quantile(dist,.85)
   aa,bb=moved[keep],y[idx[keep]];ac,bc=aa.mean(0),bb.mean(0)
   u,_,vt=np.linalg.svd((aa-ac).T@(bb-bc));fix=np.eye(3);fix[-1,-1]=np.linalg.det(u@vt);dr=u@fix@vt
   r=r@dr;t=t@dr+bc-ac@dr
  dist=tree.query(x@r+t)[0];results.append(dict(rotation_row_vector=r.tolist(),translation_mm=t.tolist(),median_mm=float(np.median(dist)),p85_mm=float(np.quantile(dist,.85)),max_mm=float(dist.max())))
results.sort(key=lambda d:d['p85_mm']);best=results[0]
r=np.array(best['rotation_row_vector']);t=np.array(best['translation_mm'])
# Recover source STL -> Blender world using the scene skull's corresponding vertices.
src=trimesh.load_mesh(OUT/'solid_w_eyes-0.stl');world=mesh('mount-1.json')
scene=json.loads((OUT/'blender-scenes.json').read_text())[0];sk=next(o for o in scene['objects'] if 'skull' in o['name'])
sw=np.array(sk['matrix_world'])
sr=sw[:3,:3].T;st=sw[:3,3]
# Verify the scene matrix against the STL vertex set before applying it to eyes.
distance=cKDTree(world.vertices).query(src.vertices@sr+st)[0]
assert distance.max()<1e-4, distance.max()
cr=sr@r;ct=st@r+t
for i in range(4):
 m=trimesh.load_mesh(OUT/f'solid_w_eyes-{i}.stl');m.vertices=m.vertices@cr+ct;m.export(OUT/f'placed-reference-{i}.stl')
eyes=json.loads((OUT/'mesh-audit.json').read_text())['solid_w_eyes']['eye_sphere_fits']
for e in eyes:e['assembly_center_mm']=(np.array(e['center_mm'])@cr+ct).tolist()
report=dict(units='mm; established hardware scale, no scaling',method='Rigid PCA candidates and trimmed nearest-vertex ICP of Blender baseplate to native uncut baseplate; provisional placement',best=best,candidates=results,stl_to_assembly=dict(rotation_row_vector=cr.tolist(),translation_mm=ct.tolist()),scene_skull_matrix_max_error_mm=float(distance.max()),eyes=eyes)
(OUT/'placement.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='candidates'},indent=2))
