from pathlib import Path
import json,hashlib,zipfile
import FreeCAD as A,FreeCADGui as G,Part
from pivy import coin
R=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent;O=R/'generated/eye-tracker/rat/eye-world-tray-r03'
def build():
 m=json.loads((S.parent/'eye-world-ribbon-r02/review.json').read_text());p=R/m['native_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256'];check=json.loads((O/'repair-validation.json').read_text());assert check['carrier_solids']==1 and check['tray_solids']==1
 d=A.openDocument(str(p))
 def read(n):
  sh=Part.Shape();sh.read(str(O/(n+'.brep')));return sh
 d.EyeWorldCarrier.Shape=read('restored-carrier');d.EyeWorldCarrier.Label='Complete PCB holder with retained eye supports';d.EyeWorldCarrier.Visibility=True
 tray=d.addObject('Part::Feature','WorldCameraStemlessTray');tray.Shape=read('world-stemless-tray');tray.Label='World camera tray - copy with stem and ball removed';tray.ViewObject.ShapeColor=(.25,.48,.76);tray.Visibility=True;tray.addProperty('App::PropertyString','Source').Source='R43 Lefteye_primary_Holder; camera seating geometry retained';tray.addProperty('App::PropertyBool','PrintReady').PrintReady=False
 d.Label='RAT eye + world R03 - restored holder and stemless tray';d.recompute();out=O/'RAT-eye-world-tray-R03.FCStd';d.saveAs(str(out));v=G.activeDocument().activeView();v.viewAxonometric();v.fitAll();v.getCameraNode().nearDistance.setValue(.01);v.getCameraNode().farDistance.setValue(10000);G.updateGui();v.saveImage(str(O/'review.png'),1600,1200,'White');d.save()
 with zipfile.ZipFile(out) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
 result={'revision':'ET-RAT-EYE-WORLD-TRAY-R03','units':'mm','native_checkpoint':str(out.relative_to(R)),'native_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source':m,'camera_and_ribbon_pose_unchanged':True,'new_object':'WorldCameraStemlessTray','status':'Restored PCB holder and stemless camera tray; world supports not designed','print_release':False};(S/'review.json').write_text(json.dumps(result,indent=2));A.closeDocument(d.Name)
