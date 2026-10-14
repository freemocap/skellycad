"""Resolve target pose, rigid fixture motion and arm geometry from a recipe."""
from pathlib import Path
import json,hashlib,sys,copy
import numpy as np
import FreeCAD as A,Part
from poses import aim_sensor,axis_error,rigid
ROOT=Path(__file__).resolve().parents[4]
import importlib.util
_spec=importlib.util.spec_from_file_location('_skellycad_flared_arm',ROOT/'designs/mouse-hats/b-flared-loop-r07/flared_arm.py')
_arm=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_arm)
geometry,rectangle,unit=_arm.geometry,_arm.rectangle,_arm.unit

def verified_asset(record):
 p=ROOT/record['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],str(p);return p

def checkpoint(manifest):
 m=json.loads((ROOT/manifest).read_text());return verified_asset({'path':m['native_checkpoint'],'sha256':m['native_sha256']}),m

def placement(T):
 T=rigid(T);m=A.Matrix(*T.ravel().tolist());return A.Placement(m)

def prepare(recipe_path,out):
 cfg=json.loads(Path(recipe_path).read_text());out=Path(out);out.mkdir(parents=True,exist_ok=True)
 checkpoint(cfg['selected_species_manifest']);checkpoint(cfg['hardware_selected_manifest'])
 source,manifest=checkpoint(cfg['hardware_manifest']);anatomy=A.openDocument(str(verified_asset(cfg['anatomy'])));eye=anatomy.getObject(cfg['target_eye_object']);assert eye is not None;assert np.linalg.norm(np.array(eye.getGlobalPlacement().Base)-cfg['target_center_world_mm'])<1e-6,'Recipe target differs from anatomy eye center';d=A.openDocument(str(source))
 T=rigid(cfg['mount_to_skull']);reference=rigid(cfg['sensor_reference_in_mount']);sensor_world=aim_sensor(cfg['target_center_world_mm'],cfg['lens_position_world_mm'],cfg['lens_local_mm'],T[:3,:3]@np.array(cfg.get('target_sensor_rotation_in_mount',reference[:3,:3].tolist())));sensor= np.linalg.inv(T)@sensor_world;D=sensor@np.linalg.inv(reference);move=placement(D)
 target={'ribbon_bounds':cfg['ribbon_bounds'],'sensor_in_mount':sensor.tolist(),'sensor_in_skull':sensor_world.tolist(),'socket_delta_in_mount':D.tolist(),'aim':axis_error(sensor_world,cfg['lens_local_mm'],cfg['target_center_world_mm'])}
 (out/'target.json').write_text(json.dumps(target,indent=2));shapes={}
 for name in ['RetainedPCBTray','RetainedSocket','eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','skull_mount_Baseplate']:
  sh=d.getObject(name).Shape.copy()
  if name in ['RetainedSocket','eye_primary_Holder','eye_primary_Clip']:sh.Placement=move.multiply(sh.Placement)
  if name=='RetainedSocket':sh.fixTolerance(1e-6)
  shapes[name]=sh;sh.exportBrep(str(out/(name+'.brep')))
 arms=copy.deepcopy(cfg['arm_parameters'])
 for name,arm in arms.items():
  arm['socket_center_mm']=(D[:3,:3]@np.array(arm['socket_center_mm'])+D[:3,3]).tolist();arm['socket_axis']=(D[:3,:3]@np.array(arm['socket_axis'])).tolist();arm['arm']['radial_direction']=(D[:3,:3]@np.array(arm['arm']['radial_direction'])).tolist()
  sh=None;errors=[];original_handles=(arm['arm']['root_handle_mm'],arm['arm']['socket_handle_mm'])
  for factor in [1.,.85,1.15,.65,1.4,.45,1.8]:
   arm['arm']['root_handle_mm']=original_handles[0]*factor;arm['arm']['socket_handle_mm']=original_handles[1]*factor
   try:sh=geometry(arm,arm['body_width_mm'],arm['body_thickness_mm'])[0];break
   except Exception as exc:errors.append(str(exc));print(name,'handle factor rejected',factor,flush=True)
  if sh is None:raise ValueError(name+' arm build failed: '+str(errors))
  n=unit(arm['socket_axis']);v=unit(arm['arm']['radial_direction']);c=A.Vector(*arm['socket_center_mm']);end=c+n*arm['attachment_height_mm']+v*arm['attachment_radius_mm'];w=unit(v.cross(n));extension=Part.makeLoft([rectangle(end+v*.25,-v,w,3,2.2),rectangle(end-v*.8,-v,w,3,2.2)],True,True);sh=sh.fuse(extension).removeSplitter();sh.check(True);sh.exportBrep(str(out/(name+'.brep')));shapes[name]=sh
  print(name,'socket engagement',sh.common(shapes['RetainedSocket']).Volume,'root engagement',sh.common(shapes['RetainedPCBTray']).Volume,flush=True)
 (out/'arms.json').write_text(json.dumps(arms,indent=2));d.close() if hasattr(d,'close') else None
 return cfg,target

