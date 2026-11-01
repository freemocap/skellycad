from pathlib import Path
import json,hashlib
import FreeCAD as A,Part,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/mouse/anatomical-mount-r17';m=json.loads((S.parent/'compact-guard-r16/review.json').read_text());src=R/m['native_checkpoint'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(src));o=d.skull_mount_Baseplate;s=o.Shape.copy();s.Placement=o.getGlobalPlacement();print('pose',o.getGlobalPlacement());print('bounds',s.BoundBox,'center',s.BoundBox.Center);print('faces',[(i+1,round(f.Area,3),list(f.CenterOfMass),str(type(f.Surface))) for i,f in enumerate(s.Faces)]);print('parents',[(x.Name,x.TypeId) for x in o.InList]);print('parts',[(x.Name,x.Label) for x in d.Objects if x.TypeId=='App::Part'])
s.exportBrep(str(S/'baseline-baseplate-world.brep'))

