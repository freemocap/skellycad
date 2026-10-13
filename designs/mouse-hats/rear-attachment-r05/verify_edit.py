"""Check a fresh native-document reload and reversible angle edit."""
from pathlib import Path
import sys,json
import FreeCAD as App
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'print-test-r03',HERE.parent/'print-test',HERE.parent/'reconstruction/baseplate',HERE.parent/'reconstruction/main_carrier']:sys.path.insert(0,str(p))
import attachment_sweep,sliding_attachment_features,socket_revision_features,attachment_arm_features,arm_finish_features,stem_blend_features,retention_features,mount_features,carrier_features
out=ROOT/'generated/mouse-hats/rear-attachment-r05'
doc=App.openDocument(str(out/'r05c-carrier.FCStd'));obj=doc.RibbonClearanceCarrier
expected=obj.Shape.Volume;reports=[]
for angle in [25,30]:
 obj.AttachmentAngle=angle;doc.recompute();obj.Shape.check(True)
 assert obj.Shape.isValid() and len(obj.Shape.Solids)==1
 assert not any('Invalid' in o.State for o in doc.Objects)
 reports.append({'angle_deg':angle,'volume_mm3':obj.Shape.Volume})
assert abs(obj.Shape.Volume-expected)<1e-6
(out/'edit-validation.json').write_text(json.dumps({'fresh_reopen_and_angle_restore':True,'checks':reports},indent=2)+'\n')
print('Fresh reopen; 30 -> 25 -> 30 degree edit and restore passed.',flush=True)
