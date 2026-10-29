from pathlib import Path
import numpy as np,trimesh,json
R=Path.cwd();O=R/'generated/eye-tracker/rat/two-arm-r28';m=trimesh.load_mesh(O/'carrier.stl');q,_=trimesh.sample.sample_surface(m,3000,seed=28);report={}
for e in json.loads((R/'designs/eye-tracker/rat/registered-eyes-r14/placement.json').read_text())['eyes']:
 eye=trimesh.load_mesh(R/'generated/eye-tracker/adult-eyes-r01/rat-whole.stl');eye.apply_transform(np.array(e['pose']));inside=int(eye.contains(q).sum());assert inside==0;report[e['side']]={'samples':len(q),'inside_eye':inside}
report['scope']='Carrier sampled containment only; skull surface crossings checked natively. Full motion sweep and physical stiffness untested.';(O/'eye-clearance.json').write_text(json.dumps(report,indent=2));print(report)
