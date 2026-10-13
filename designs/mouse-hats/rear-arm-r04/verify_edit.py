"""Fresh-process proxy restoration and A/B route control test."""
from pathlib import Path
import sys,json
import FreeCAD as A
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'print-test-r03',HERE.parent/'print-test',HERE.parent/'reconstruction/baseplate',HERE.parent/'reconstruction/main_carrier']:sys.path.insert(0,str(p))
import ribbon_carrier_features,rear_sweep,socket_revision_features,attachment_arm_features,arm_finish_features,stem_blend_features,retention_features,mount_features,carrier_features
out=ROOT/'generated/mouse-hats/rear-arm-r04'
a=A.openDocument(str(out/'r04a-carrier.FCStd'));b=A.openDocument(str(out/'r04b-carrier.FCStd'))
va=a.RibbonClearanceCarrier.Shape.Volume;vb=b.RibbonClearanceCarrier.Shape.Volume
obj=a.RibbonClearanceCarrier
for drop,expected in [(1.25,vb),(0,va)]:
 obj.ExtraDrop=drop;a.recompute();obj.Shape.check(True)
 assert abs(obj.Shape.Volume-expected)<1e-6,(drop,obj.Shape.Volume,expected)
 assert not any('Invalid' in o.State for o in a.Objects)
(out/'edit-validation.json').write_text(json.dumps({'fresh_reopen_A_to_B_and_restore':True,'A_mm3':va,'B_mm3':vb},indent=2)+'\n')
print('Fresh reopen, A -> B -> A control edit passed.')
