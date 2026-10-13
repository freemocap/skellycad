"""Measure corresponding bottom polygons after rigid alignment of unchanged faces."""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
r=HERE.parent/'old/df-hardware/baseplate'
paths=[r/'tall_53n_baseplate.stl',r/'tall_tapered_53n_baseplate.stl']
a,b=[trimesh.load_mesh(p,process=False) for p in paths]
assert a.triangles.shape==b.triangles.shape
lengths=lambda m:np.linalg.norm(m.triangles-np.roll(m.triangles,1,axis=1),axis=2)
mask=np.max(abs(lengths(a)-lengths(b)),axis=1)<1e-4
x=a.triangles[mask].reshape(-1,3);y=b.triangles[mask].reshape(-1,3)
ac=x.mean(axis=0);bc=y.mean(axis=0)
u,_,vt=np.linalg.svd((x-ac).T@(y-bc));rot=u@vt;t=bc-ac@rot
assert np.linalg.det(rot)>.999999
# Bottom plane in this specific supplied mesh: normal and offset disambiguate
# the small parallel facets on the upper pocket. Units are mm.
idx=np.where((a.face_normals@np.array([-.0005,.384,-.9233])>.9999)&
    (abs(np.einsum('ij,ij->i',a.face_normals,a.triangles_center)+13.1336)<.01))[0][0]
n=a.face_normals[idx];offset=a.triangles_center[idx]@n
keep=abs(a.vertices@n-offset)<1e-5
old=a.vertices[keep];new=(b.vertices[keep]-t)@rot.T
u=np.array([1.,0,0]);u-=n*(u@n);u/=np.linalg.norm(u)
basis=np.column_stack([u,np.cross(n,u)])
p=old@basis;q=new@basis;design=np.column_stack([p,np.ones(len(p))])
fit=np.linalg.lstsq(design,q,rcond=None)[0]
report={'units':'mm','source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
 'matching_triangles':int(mask.sum()),'rigid_alignment_max_error_mm':float(np.linalg.norm(x@rot+t-y,axis=1).max()),
 'bottom_affine_2d':fit.tolist(),'bottom_scale':float(np.trace(fit[:2])/2),
 'bottom_fit_max_error_mm':float(abs(design@fit-q).max()),
 'normal_displacement_max_mm':float(abs((new-old)@n).max())}
assert abs(report['bottom_scale']-.57004)<1e-6
out=ROOT/'generated/mouse-hats/baseplate-taper';out.mkdir(parents=True,exist_ok=True)
(out/'mesh-measurement.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
