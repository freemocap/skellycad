from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path.cwd();S=R/'designs/eye-tracker/rat/neutral-camera-r20';O=R/'generated/eye-tracker/rat/neutral-camera-r20';rng=np.random.default_rng(18)
points=[]
for f in O.glob('*-world.stl'):
 m=trimesh.load_mesh(f);q,_=trimesh.sample.sample_surface(m,600,seed=18);points.append(q)
q=np.vstack(points);report={}
for e in json.loads((S.parent/'registered-eyes-r14/placement.json').read_text())['eyes']:
 m=trimesh.load_mesh(R/'generated/eye-tracker/adult-eyes-r01/rat-whole.stl');m.apply_transform(np.array(e['pose']));inside=m.contains(q);report[e['side']]={'samples':len(q),'inside_eye':int(inside.sum())};assert not inside.any()
report['skull_containment']='Not asserted: source-derived anatomical skull is open. Native mesh surface-crossing checks are recorded separately.'
c=json.loads((R/'designs/eye-tracker/shared/cameras/pupil-core-eye/active-model.json').read_text())
for rec in [c['native_checkpoint'],*c['parts'].values()]:assert hashlib.sha256((R/rec['path']).read_bytes()).hexdigest()==rec['sha256']
report['shared_camera_asset_hashes_verified']=True;(O/'containment.json').write_text(json.dumps(report,indent=2));print(report)
