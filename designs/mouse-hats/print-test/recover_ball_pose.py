"""Anchor the V5 holder pose to the unchanged ball sphere; no source writes."""
from pathlib import Path
import json
import numpy as np
import trimesh
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/print-test/r01'
target=trimesh.load_mesh(ROOT/'generated/mouse-hats/arms/v5-shell-1.stl',process=True)
p=json.loads((ROOT/'designs/mouse-hats/reconstruction/camera_holder/parameters.json').read_text())
fit=json.loads((OUT/'holder-pose-fit.json').read_text())[0]
r=np.array(fit['rotation_row_vector']);t=np.array(fit['translation_mm'])
bc=np.array(p['neck_center_mm'])+3*np.array(p['neck_axis_up'])
guess=bc@r+t
v=target.vertices;v=v[np.linalg.norm(v-guess,axis=1)<3]
rng=np.random.default_rng(81);best=None
for _ in range(15000):
 q=v[rng.choice(len(v),4,replace=False)]
 try:c=np.linalg.solve(2*(q[1:]-q[0]),np.sum(q[1:]**2,axis=1)-np.sum(q[0]**2))
 except np.linalg.LinAlgError:continue
 radius=np.linalg.norm(q[0]-c)
 if abs(radius-2)>.015:continue
 mask=np.abs(np.linalg.norm(v-c,axis=1)-radius)<.002
 if best is None or mask.sum()>best[0]:best=(mask.sum(),mask,c,radius)
print('best',best[0],best[2],best[3],flush=True)
q=v[best[1]];a=np.column_stack((2*q,np.ones(len(q))))
fitball=np.linalg.lstsq(a,np.sum(q*q,axis=1),rcond=None)[0];center=fitball[:3]
radius=np.sqrt(fitball[3]+center@center)
fit['translation_mm']=(center-bc@r).tolist();fit['ball_center_mm']=center.tolist();fit['ball_radius_mm']=float(radius)
fit['ball_vertex_inliers']=int(best[0]);fit['note']='ICP orientation; translation anchored to fitted unchanged spherical ball'
(OUT/'holder-pose.json').write_text(json.dumps(fit,indent=2))
print(json.dumps(fit,indent=2))
