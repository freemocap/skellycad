from pathlib import Path
import json,numpy as np,trimesh
from scipy.spatial import cKDTree
ROOT=Path.cwd();ST=ROOT/'designs/eye-tracker/mouse/registered-eyes-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/registered-eyes-study-r01'
r=json.loads((ST/'registration.json').read_text());a=trimesh.load(OUT/'digimouse-head-source.stl');b=trimesh.load(ROOT/'designs/eye-tracker/mouse/references/skull/Skull.stl');np.random.seed(284)
p,_=trimesh.sample.sample_surface(a,14000);q,_=trimesh.sample.sample_surface(b,22000);tree=cKDTree(q);base=np.array(r['matrix_source_index_mm_to_assembly']);rows=[]
for trim in [.7,.8,.9]:
 T=base.copy()
 for j in range(40):
  v=trimesh.transform_points(p,T);dist,ids=tree.query(v);keep=dist<np.quantile(dist,trim);dt,_,_=trimesh.registration.procrustes(v[keep],q[ids[keep]],reflection=False,scale=True);T=dt@T
 c=np.array([e['source_centroid_index_mm'] for e in r['eyes']]);bc=trimesh.transform_points(c,base);tc=trimesh.transform_points(c,T)
 rows.append({'retained_fraction':trim,'scale':float(np.cbrt(np.linalg.det(T[:3,:3]))),'eye_anchor_shift_from_primary_mm':np.linalg.norm(tc-bc,axis=1).tolist(),'matrix':T.tolist()})
report={'interpretation':'Local ICP sensitivity to trimming with new surface samples, not biological uncertainty or global registration validation','trials':rows};(ST/'sensitivity.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
