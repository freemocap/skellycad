from pathlib import Path
import json,hashlib,zipfile
import FreeCAD as A,FreeCADGui as G,Part
from pivy import coin
R=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent;O=R/'generated/eye-tracker/rat/eye-world-two-supports-r05'
def build():
 m=json.loads((S/'source.json').read_text());source=R/m['native_checkpoint'];assert hashlib.sha256(source.read_bytes()).hexdigest()==m['native_sha256'];checks=json.loads((O/'support-validation.json').read_text());assert checks['mesh']['closed'] and not checks['mesh']['self_intersections'];assert json.loads((O/'final-validation.json').read_text())['passed'];d=A.openDocument(str(source));shape=Part.Shape();shape.read(str(O/'finished-carrier.brep'));d.EyeWorldCarrier.Shape=shape;d.EyeWorldCarrier.Label='PCB carrier - two perpendicular world-camera supports';d.Label='RAT eye + world R05 - two-arm world camera support';d.recompute();p=O/'RAT-eye-world-two-supports-R05.FCStd';d.saveAs(str(p));v=G.activeDocument().activeView();v.viewAxonometric();v.fitAll();v.getCameraNode().nearDistance.setValue(.01);v.getCameraNode().farDistance.setValue(10000);G.updateGui();v.saveImage(str(O/'review.png'),1600,1200,'White');d.save()
 with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
 record={'revision':'ET-RAT-EYE-WORLD-TWO-SUPPORTS-R05','units':'mm','native_checkpoint':str(p.relative_to(R)),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':m,'camera_and_ribbon_unchanged':True,'world_support_count':2,'socket_approach_angle_degrees':checks['socket_approach_angle_degrees'],'physical_fit_verified':False,'print_release':False};(S/'review.json').write_text(json.dumps(record,indent=2));A.closeDocument(d.Name)
