from support import *
a=load('04-arms');d=load('02-camera-and-ribbon-study')
for tail in ['UpperSupport','LowerSupport']:assign(d.getObject('Right'+tail),world(a.getObject('Right'+tail)))
r=json.loads((O/'04-arms.json').read_text());r={k:v for k,v in r.items() if k.startswith('Right')};(O/'04-arms.json').write_text(json.dumps(r,indent=2));d.recompute();d.saveAs(str(O/'04-arms-working.FCStd'));A.closeDocument(a.Name);A.closeDocument(d.Name)
