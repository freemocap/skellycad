"""Provisional rigid V5 tray alignment; no scaling, repair or source writes."""
from pathlib import Path
import hashlib,itertools,json
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/arms';OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'designs/mouse-hats/old/df-hardware/camera-assembly/camera-assembly-2arm-v5.stl'
raw=trimesh.load_mesh(source,process=False)
v,inv=np.unique(raw.vertices,axis=0,return_inverse=True)
mesh=trimesh.Trimesh(v,inv[raw.faces],process=False)
shells=sorted(mesh.split(only_watertight=False,repair=False),key=lambda m:len(m.faces),reverse=True)
tray=next(m for m in shells if len(m.faces)==650)
data=json.loads((OUT/'tray-reference.json').read_text())
target=trimesh.Trimesh(data['vertices'],data['faces'],process=False)
x=trimesh.sample.sample_surface(tray,8000,seed=7)[0]
y=trimesh.sample.sample_surface(target,14000,seed=8)[0]
tree=cKDTree(y)
cx,cy=x.mean(axis=0),y.mean(axis=0)
_,ea=np.linalg.eigh(np.cov(x.T));_,eb=np.linalg.eigh(np.cov(y.T))
results=[]
for signs in itertools.product((-1,1),repeat=3):
    rot=ea@np.diag(signs)@eb.T
    if np.linalg.det(rot)<0:continue
    trans=cy-cx@rot
    for _ in range(90):
        moved=x@rot+trans
        dist,idx=tree.query(moved)
        keep=dist<np.quantile(dist,0.8)
        a,b=moved[keep],y[idx[keep]];ac,bc=a.mean(axis=0),b.mean(axis=0)
        u,_,vt=np.linalg.svd((a-ac).T@(b-bc))
        fix=np.eye(3);fix[-1,-1]=np.linalg.det(u@vt)
        dr=u@fix@vt;dt=bc-ac@dr
        rot=rot@dr;trans=trans@dr+dt
    dist=tree.query(x@rot+trans)[0]
    results.append(dict(rotation_row_vector=rot.tolist(),translation_mm=trans.tolist(),
        median_sample_distance_mm=float(np.median(dist)),p80_sample_distance_mm=float(np.quantile(dist,.8)),
        p95_sample_distance_mm=float(np.quantile(dist,.95))))
results.sort(key=lambda r:r['p80_sample_distance_mm'])
best=results[0];r=np.array(best['rotation_row_vector']);t=np.array(best['translation_mm'])
components=[]
for i,m in enumerate(shells,1):
    moved=m.copy();moved.vertices=m.vertices@r+t;moved.export(OUT/f'v5-shell-{i}.stl')
    components.append(dict(id=i,triangles=len(m.faces),bounds_mm=moved.bounds.tolist(),
        watertight=bool(m.is_watertight)))
report=dict(source=str(source.relative_to(ROOT)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    method='Tray shell (650 triangles), proper PCA signs then 80-percent trimmed nearest-sample rigid ICP; no scale',
    status='PROVISIONAL: sampled residuals, geometry changes and symmetry require visual/landmark review',
    candidates=results,components=components)
(OUT/'registration.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
