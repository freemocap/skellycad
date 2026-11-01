from pathlib import Path
import json,hashlib,zipfile,numpy as np
import FreeCAD as A,FreeCADGui as G,Part
from pivy import coin
R=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent;O=R/'generated/eye-tracker/rat/eye-world-ribbon-r02';P=R/'generated/eye-tracker/rat/lowered-cameras-r43'
def build():
 src=json.loads((S.parent/'lowered-cameras-r43/review.json').read_text());path=R/src['native_checkpoint'];assert hashlib.sha256(path.read_bytes()).hexdigest()==src['native_sha256'];check=json.loads((O/'selected-validation.json').read_text());assert check['passed'];rec=json.loads((S/'selected-pose.json').read_text());cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull']);H=np.array(rec['head_world']);D=H@np.linalg.inv(np.array(cfg['sides']['Left']['head']));d=A.openDocument(str(path));sensor=(D@np.r_[np.array(list(d.LeftCamera.OpticalAxis.SensorCenter)),1])[:3]
 def read(n,folder=O):
  s=Part.Shape();s.read(str(folder/(n+'.brep')));return s
 def move(s,t):return s.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
 for o in d.Objects:o.Visibility=o.TypeId=='App::Part'
 for n in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea','Baseplate','Righteye_primary_Holder','Righteye_primary_Clip']:d.getObject(n).Visibility=True
 carrier=d.addObject('Part::Feature','EyeWorldCarrier');carrier.Shape=read('Carrier');carrier.ViewObject.ShapeColor=(.65,.68,.72)
 for o in d.RightCamera.PhysicalParts:o.Visibility=True
 d.RightCamera.OpticalAxis.Visibility=True
 cam=d.LeftCamera;cam.Label='World camera - ribbon-derived pose';cam.Placement=A.Placement()
 cam.PhysicalParts[0].Shape=Part.makeCompound([move(read('LeftPCB',P),T),read('camera_pcb')]);cam.PhysicalParts[1].Shape=read('M4_lens');cam.PhysicalParts[2].Shape=Part.makeCompound([move(read('LeftJST_4pin',P),T),read('IR_LED'),read('IR_LED_001')]);cam.PhysicalParts[3].Shape=read('Ribbon')
 for o,col in zip(cam.PhysicalParts,[(.9,.12,.1),(.12,.12,.14),(.94,.94,.9),(1.,.8,.02)]):o.Visibility=True;o.ViewObject.ShapeColor=col;o.ViewObject.DisplayMode='Shaded'
 cam.OpticalAxis.Origin=A.Vector(*rec['lens_world_mm']);cam.OpticalAxis.Direction=A.Vector(*H[:3,2]);cam.OpticalAxis.SensorCenter=A.Vector(*sensor);cam.OpticalAxis.Shape=Part.makeLine(cam.OpticalAxis.Origin,cam.OpticalAxis.Origin+cam.OpticalAxis.Direction*18);cam.OpticalAxis.Visibility=True;cam.OpticalAxis.ViewObject.LineColor=(0.,.65,.95)
 cam.SensorFrame.Placement=A.Placement(A.Vector(*sensor),A.Rotation(A.Matrix(*H.ravel().tolist())));cam.SensorFrame.Visibility=False
 # Retain actual matched fixtures in the tree, transformed to the solved pose,
 # but hidden because their original back stem/socket collide with fixed boards.
 for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:
  obj=d.getObject('Left'+tail);obj.Shape=read('candidate-'+str(check['index'])+'-'+tail);obj.Visibility=False;obj.Label='World '+tail+' - original fixture, refit required'
 record=d.addObject('App::FeaturePython','RibbonDrivenStudy');record.addProperty('App::PropertyString','ValidationJSON').ValidationJSON=json.dumps(check);record.addProperty('App::PropertyBool','PrintReady').PrintReady=False
 d.Label='RAT eye + world - R02 ribbon-driven placement';d.recompute();p=O/'RAT-eye-world-ribbon-R02.FCStd';d.saveAs(str(p));v=G.activeDocument().activeView();v.viewAxonometric();v.fitAll();v.getCameraNode().nearDistance.setValue(.01);v.getCameraNode().farDistance.setValue(10000);G.updateGui();v.saveImage(str(O/'review.png'),1600,1200,'White');v.viewTop();v.fitAll();G.updateGui();v.saveImage(str(O/'top.png'),1600,1200,'White');v.viewAxonometric();v.fitAll();d.save()
 with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
 manifest={'revision':'ET-RAT-EYE-WORLD-RIBBON-R02','units':'mm','native_checkpoint':str(p.relative_to(R)),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':{k:src[k] for k in ['revision','native_checkpoint','native_sha256']},'status':'Ribbon-driven placement review; world holder and supports need refit','physical_fit_verified':False,'print_release':False};(S/'review.json').write_text(json.dumps(manifest,indent=2));A.closeDocument(d.Name)
