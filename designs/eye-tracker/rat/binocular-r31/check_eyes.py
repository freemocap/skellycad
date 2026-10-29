"""Check sampled hardware containment in the retained eye envelopes."""
from pathlib import Path
import json,numpy as np,trimesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/binocular-r31';O=R/'generated/eye-tracker/rat/binocular-r31';report={'passed':False,'parts':{}}
eyes=[]
for e in json.loads((S.parent/'registered-eyes-r14/placement.json').read_text())['eyes']:
 mesh=trimesh.load_mesh(R/'generated/eye-tracker/adult-eyes-r01/rat-whole.stl');mesh.apply_transform(np.array(e['pose']));eyes.append((e['side'],mesh))
for f in (O/'validation-meshes').glob('*.stl'):
 if f.stem=='Baseplate':continue
 m=trimesh.load_mesh(f);points,_=trimesh.sample.sample_surface(m,2000,seed=31);report['parts'][f.stem]={}
 for side,eye in eyes:
  n=int(eye.contains(points).sum());report['parts'][f.stem][side]={'samples':len(points),'inside_eye':n};assert n==0,(f.stem,side,n)
assert len(report['parts'])==19,len(report['parts'])
report['passed']=True;report['scope']='Sampled eye containment; skull crossings are checked natively. Skull volume containment is not asserted for the open source skull mesh. Physical fit and adjustment travel untested.';(O/'containment.json').write_text(json.dumps(report,indent=2));print('EYE_CONTAINMENT_PASS',len(report['parts']))
