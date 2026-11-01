from pathlib import Path
import json,hashlib,sys
import FreeCAD as A, Part, Mesh
R=Path.cwd();s=R/'designs/eye-tracker/mouse/nasal-camera-r15';m=json.loads((s.parent/'landmark-eye-placement-r14/review.json').read_text());src=R/m['native_checkpoint'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['native_sha256'];sel=json.loads((s.parent/'active-model.json').read_text());assert hashlib.sha256((R/sel['native_checkpoint']).read_bytes()).hexdigest()==sel['native_sha256'];d=A.openDocument(str(src))
names=['PCB','camera_pcb','DetailedOpticalAxis','RetainedSocket','eye_primary_Holder','UpperSupport','RearRibbonGuard','RetainedPCBTray','Eye1OpticalFrame']
print([(n,d.getObject(n)) for n in names]);o={n:{'pose':list(d.getObject(n).getGlobalPlacement().toMatrix().A),'local':list(d.getObject(n).Placement.toMatrix().A)} for n in names}
a=d.DetailedOpticalAxis;p=a.getGlobalPlacement();o['axis']={'origin':list(p.multVec(a.Origin)),'direction':list(p.Rotation.multVec(a.Direction))};o['camera_recipe']=json.loads(d.DetailedCameraRecipe.RecipeJSON)
(s/'baseline.json').write_text(json.dumps(o,indent=2));print(json.dumps(o,indent=2))

