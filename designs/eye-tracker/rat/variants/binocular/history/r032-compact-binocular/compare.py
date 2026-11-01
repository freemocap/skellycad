from pathlib import Path
import json,sys
import FreeCAD as A
R=Path.cwd();S=R/'designs/eye-tracker/rat/compact-binocular-r32';O=R/'generated/eye-tracker/rat/compact-binocular-r32'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
m=json.loads((S.parent/'binocular-r31/review.json').read_text());old=A.openDocument(str(R/m['native_checkpoint']));d=A.openDocument(str(O/'ET-RAT-COMPACT-BINOCULAR-R32.FCStd'))
report={'units':'mm','old_carrier_volume_mm3':old.FinishedCarrier.Shape.Volume,'new_carrier_volume_mm3':d.FinishedCarrier.Shape.Volume,'old_carrier_world_z_max_mm':world(old.FinishedCarrier).BoundBox.ZMax,'new_carrier_world_z_max_mm':world(d.FinishedCarrier).BoundBox.ZMax}
report['carrier_volume_reduction_percent']=100*(1-report['new_carrier_volume_mm3']/report['old_carrier_volume_mm3']);report['carrier_height_reduction_mm']=report['old_carrier_world_z_max_mm']-report['new_carrier_world_z_max_mm'];report['arm_routing']=json.loads((S/'arms.json').read_text());assert report['carrier_volume_reduction_percent']>0
(S/'comparison.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='arm_routing'});A.closeDocument(d.Name);A.closeDocument(old.Name)
