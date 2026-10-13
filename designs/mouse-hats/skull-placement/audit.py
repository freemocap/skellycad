"""Exact welding, explicit topology audit and conservative cleanup; raw units treated as mm."""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-placement';OUT.mkdir(parents=True,exist_ok=True)
def load(p):
 m=trimesh.load_mesh(p,process=False)
 v,inv=np.unique(m.vertices,axis=0,return_inverse=True)
 return trimesh.Trimesh(v,inv[m.faces],process=False)
def audit(m):
 counts=np.bincount(m.edges_unique_inverse)
 return dict(vertices=len(m.vertices),faces=len(m.faces),boundary_edges=int((counts==1).sum()),nonmanifold_edges=int((counts>2).sum()),duplicate_faces=int(len(m.faces)-m.unique_faces().sum()),degenerate_faces=int((~m.nondegenerate_faces()).sum()),watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),signed_volume_mm3=float(m.volume),bounds_mm=m.bounds.tolist())
report={}
for kind in ['hollow','solid','solid_w_eyes']:
 p=ROOT/f'designs/mouse-hats/old/df-hardware/utility/mouse_skull_low_poly_{kind}.stl'
 m=load(p);data=dict(source=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw=audit(m))
 # Remove duplicate triangles and zero-area faces only; no smoothing or filling.
 m.update_faces(m.unique_faces() & m.nondegenerate_faces());m.remove_unreferenced_vertices()
 parts=sorted(m.split(only_watertight=False,repair=False),key=lambda s:len(s.faces),reverse=True)
 data['clean_components']=[audit(c) for c in parts]
 for i,c in enumerate(parts):c.export(OUT/f'{kind}-{i}.stl')
 if kind=='solid_w_eyes':
  eyes=[]
  for i,c in enumerate(parts[1:3],1):
   v=c.vertices;a=np.column_stack([2*v,np.ones(len(v))]);sol=np.linalg.lstsq(a,(v*v).sum(axis=1),rcond=None)[0];center=sol[:3];r=np.sqrt(sol[3]+center@center)
   eyes.append(dict(component=i,center_mm=center.tolist(),radius_mm=float(r),radial_max_residual_mm=float(abs(np.linalg.norm(v-center,axis=1)-r).max())))
  data['eye_sphere_fits']=eyes
 report[kind]=data
(OUT/'mesh-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
