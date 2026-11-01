from pathlib import Path
import json
import FreeCAD as A,Part,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/mouse/nasal-camera-r15';O=R/'generated/eye-tracker/mouse/nasal-camera-r15';m=json.loads((S.parent/'landmark-eye-placement-r14/review.json').read_text());old=A.openDocument(str(R/m['native_checkpoint']));d=A.openDocument(str(O/'ET-MOUSE-NASAL-R15.FCStd'));D=A.Placement(A.Matrix(*sum(json.loads((S/'solution.json').read_text())['delta'],[])));report={}
for n in ['PCB','JST_4pin','eye_primary_Cap','skull_mount_Baseplate','Eye1OpticalFrame','Eye2OpticalFrame','Skull']:
 a=old.getObject(n);b=d.getObject(n);err=max(abs(x-y) for x,y in zip(a.getGlobalPlacement().toMatrix().A,b.getGlobalPlacement().toMatrix().A));assert err<1e-10;report[n]={'pose_error':err}
 if hasattr(a,'Shape'):assert a.Shape.exportBrepToString()==b.Shape.exportBrepToString()
for n in ['RetainedSocket','eye_primary_Holder','eye_primary_Clip','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
 a=old.getObject(n);b=d.getObject(n);expected=D.multiply(a.getGlobalPlacement());err=max(abs(x-y) for x,y in zip(expected.toMatrix().A,b.getGlobalPlacement().toMatrix().A));assert err<1e-9;report[n]={'common_rigid_delta_error':err}
(O/'interface-validation.json').write_text(json.dumps(report,indent=2));print('Fixed interfaces and common moving assembly transform PASS')
