"""Rigid fit of the unchanged holder reference to supplied V5 holder mesh."""
from pathlib import Path
import json,itertools
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/print-test/r01'
data=json.loads((OUT/'holder-reference-mesh.json').read_text())
source=trimesh.Trimesh(data['vertices'],data['faces'],process=False)
target=trimesh.load_mesh(ROOT/'generated/mouse-hats/arms/v5-shell-1.stl',process=True)
x=trimesh.sample.sample_surface(source,7000,seed=18)[0]
y=trimesh.sample.sample_surface(target,18000,seed=19)[0]
tree=cKDTree(y);cx=x.mean(axis=0);cy=y.mean(axis=0)
_,ea=np.linalg.eigh(np.cov(x.T));_,eb=np.linalg.eigh(np.cov(y.T))
results=[]
for signs in itertools.product((-1,1),repeat=3):
    rot=ea@np.diag(signs)@eb.T
    if np.linalg.det(rot)<0:continue
    trans=cy-cx@rot
    for _ in range(100):
        moved=x@rot+trans;dist,idx=tree.query(moved)
        keep=dist<np.quantile(dist,.7)
        a,b=moved[keep],y[idx[keep]];ac,bc=a.mean(axis=0),b.mean(axis=0)
        u,_,vt=np.linalg.svd((a-ac).T@(b-bc));fix=np.eye(3);fix[-1,-1]=np.linalg.det(u@vt)
        dr=u@fix@vt;dt=bc-ac@dr;rot=rot@dr;trans=trans@dr+dt
    dist=tree.query(x@rot+trans)[0]
    results.append(dict(rotation_row_vector=rot.tolist(),translation_mm=trans.tolist(),
                        median_mm=float(np.median(dist)),p70_mm=float(np.quantile(dist,.7))))
results.sort(key=lambda r:r['p70_mm'])
(OUT/'holder-pose-fit.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
