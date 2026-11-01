from pathlib import Path
import FreeCAD as A,json
R=Path.cwd();records=json.loads((R/'designs/eye-tracker/rat/two-arm-r28/review-inputs.json').read_text())['inputs'];a=A.openDocument(str(R/records[0]['source_checkpoint']));b=A.openDocument(str(R/records[2]['source_checkpoint']));report={}
for name in ['eye_primary_Holder','RetainedSocket','skull_mount_Baseplate','camera_pcb','M4_lens']:
 shapes=[]
 for d in [a,b]:
  o=d.getObject(name);s=o.Shape.copy();s.Placement=o.getGlobalPlacement();shapes.append(s)
 x,y=shapes;report[name]={'r27_minus_r21_mm3':x.cut(y).Volume,'r21_minus_r27_mm3':y.cut(x).Volume,'bounds_center_shift_mm':(x.BoundBox.Center-y.BoundBox.Center).Length}
(R/'generated/eye-tracker/rat/two-arm-r28/r21-r27-interface-comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


