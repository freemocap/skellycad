"""Create a complete review assembly in the anatomy's world frame."""
from pathlib import Path
import json,hashlib,numpy as np
import FreeCAD as A,Part
from prepare import checkpoint,verified_asset,placement

def assemble(recipe_path,out):
 cfg=json.loads(Path(recipe_path).read_text());out=Path(out);source,manifest=checkpoint(cfg['hardware_manifest']);src=A.openDocument(str(source));d=A.openDocument(str(verified_asset(cfg['anatomy'])));T=placement(cfg['mount_to_skull']);target=json.loads((out/'target.json').read_text());sensor_delta=placement(np.array(target['sensor_in_mount'])@np.linalg.inv(np.array(cfg['sensor_reference_in_mount'])))
 group=d.addObject('App::DocumentObjectGroup','CameraAssembly');group.Label=cfg['revision']
 names=['eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','skull_mount_Baseplate']
 for name in names+['RetainedPCBTray','RetainedSocket','UpperSupport','RearRibbonGuard']:
  sh=Part.Shape();sh.read(str(out/(name+'.brep')));sh.Placement=T.multiply(sh.Placement);o=d.addObject('Part::Feature',name);o.Shape=sh;group.addObject(o)
 for name,file in [('FinishedCarrier','finished.brep'),('RibbonCandidate','ribbon.brep')]:
  sh=Part.Shape();sh.read(str(out/file));sh.Placement=T.multiply(sh.Placement);o=d.addObject('Part::Feature',name);o.Shape=sh;group.addObject(o)
 for parent in ['MeasuredMainPCB','MeasuredSensorHead']:
  sub=d.addObject('App::DocumentObjectGroup',parent);group.addObject(sub)
  for ob in src.getObject(parent).Group:
   if not hasattr(ob,'Shape'):continue
   sh=ob.Shape.copy();original_pose=ob.getGlobalPlacement();sh.Placement=T.multiply(sensor_delta.multiply(original_pose) if parent=='MeasuredSensorHead' else original_pose);o=d.addObject('Part::Feature',ob.Name);o.Label=ob.Label;o.Shape=sh;sub.addObject(o)
 lens=A.Vector(*cfg['lens_position_world_mm']);eye=A.Vector(*cfg['target_center_world_mm']);axis=d.addObject('Part::Feature','CameraOpticalAxis');axis.Label='Optical axis to right-eye center';axis.Shape=Part.makeLine(lens,eye);group.addObject(axis)
 d.addObject('App::FeaturePython','TargetRecipe').addProperty('App::PropertyString','RecipeJSON');d.TargetRecipe.RecipeJSON=json.dumps(cfg)
 d.recompute();path=out/(cfg.get('document_name','monocular-rat-targeted-r02')+'.FCStd');d.saveAs(str(path));d.Label=cfg['revision'];d.save();return d
