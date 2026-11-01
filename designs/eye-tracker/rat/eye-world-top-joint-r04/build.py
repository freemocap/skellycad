from pathlib import Path
import json,hashlib,zipfile,numpy as np
import FreeCAD as A,FreeCADGui as G,Part
from pivy import coin
R=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent;O=R/'generated/eye-tracker/rat/eye-world-top-joint-r04';P=R/'generated/eye-tracker/rat/lowered-cameras-r43'
def build():
 m=json.loads((S.parent/'eye-world-tray-r03/review.json').read_text());src=R/m['native_checkpoint'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['native_sha256'];assert json.loads((O/'final-validation.json').read_text())['passed'];d=A.openDocument(str(src));rec=json.loads((S/'selected-pose.json').read_text());H=np.array(rec['head_world']);old=np.array(json.loads((S.parent/'eye-world-ribbon-r02/selected-pose.json').read_text())['head_world']);cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull'])
 def read(n,folder=O):
  sh=Part.Shape();sh.read(str(folder/(n+'.brep')));return sh
 def move(s,t):return s.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
 cam=d.LeftCamera;sensor=(H@np.linalg.inv(old)@np.r_[np.array(list(cam.OpticalAxis.SensorCenter)),1])[:3]
 cam.PhysicalParts[0].Shape=Part.makeCompound([move(read('LeftPCB',P),T),read('camera_pcb')]);cam.PhysicalParts[1].Shape=read('M4_lens');cam.PhysicalParts[2].Shape=Part.makeCompound([move(read('LeftJST_4pin',P),T),read('IR_LED'),read('IR_LED_001')]);cam.PhysicalParts[3].Shape=read('Ribbon');cam.Label='World camera - level, moved forward 2 mm'
 cam.OpticalAxis.Origin=A.Vector(*rec['lens_world_mm']);cam.OpticalAxis.Direction=A.Vector(*H[:3,2]);cam.OpticalAxis.SensorCenter=A.Vector(*sensor);cam.OpticalAxis.Shape=Part.makeLine(cam.OpticalAxis.Origin,cam.OpticalAxis.Origin+A.Vector(18,0,0));cam.SensorFrame.Placement=A.Placement(A.Vector(*sensor),A.Rotation(A.Matrix(*H.ravel().tolist())))
 d.EyeWorldCarrier.Shape=read('finished-carrier');d.EyeWorldCarrier.Label='Clean PCB carrier with top socket support'
 d.WorldCameraStemlessTray.Visibility=False
 holder=d.addObject('Part::Feature','WorldCameraTopStemTray');holder.Shape=read('finished-holder');holder.Label='World camera tray with original ball stem relocated to top';holder.ViewObject.ShapeColor=(.25,.48,.76)
 clip=d.addObject('Part::Feature','WorldCameraMatchingClip');clip.Shape=read('world-clip');clip.ViewObject.ShapeColor=(.25,.48,.76)
 d.Label='RAT eye + world R04 - level tray and top ball joint';d.recompute();p=O/'RAT-eye-world-top-joint-R04.FCStd';d.saveAs(str(p));v=G.activeDocument().activeView();v.viewAxonometric();v.fitAll();v.getCameraNode().nearDistance.setValue(.01);v.getCameraNode().farDistance.setValue(10000);G.updateGui();v.saveImage(str(O/'review.png'),1600,1200,'White');d.save()
 with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
 manifest={'revision':'ET-RAT-EYE-WORLD-TOP-JOINT-R04','units':'mm','native_checkpoint':str(p.relative_to(R)),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':m,'lens_delta_world_mm':(np.array(rec['lens_world_mm'])-np.array(json.loads((S.parent/'eye-world-ribbon-r02/selected-pose.json').read_text())['lens_world_mm'])).tolist(),'status':'Level forward camera, relocated original stem and socket, top carrier support; physical trial pending','print_release':False};(S/'review.json').write_text(json.dumps(manifest,indent=2));A.closeDocument(d.Name)
