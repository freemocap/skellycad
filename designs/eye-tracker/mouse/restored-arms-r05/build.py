"""New supports to the stationary socket stem, preserving the seated camera."""
from pathlib import Path
import json,hashlib,sys,copy
sys.path.insert(0,str(Path.cwd()/'designs/mouse-hats/b-flared-loop-r07'))
from flared_arm import geometry,unit
import FreeCAD as A,Part
ROOT=Path.cwd();OUT=ROOT/'generated/eye-tracker/mouse/restored-arms-r05';V=A.Vector

def build():
 m=json.loads((ROOT/'designs/eye-tracker/mouse/active-model.json').read_text());assert hashlib.sha256((ROOT/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
 src=ROOT/'generated/eye-tracker/mouse/ribbon-fixed-r03/mouse-fixed-cradle-r03-verified.FCStd';d=A.openDocument(str(src))
 s=json.loads((ROOT/'designs/mouse-hats/b-flared-loop-r07/settings.json').read_text());n=V(*s['rear_data']['socket_axis']);n.normalize();c=V(*s['rear_data']['socket_center_mm'])+V(*s['joint_shift_mm']);center=c+n*3.9
 def radial(v):v=V(*v);v-=n*v.dot(n);v.normalize();return v
 upperend=center+radial((0,1,0))*2.65;rearend=center+radial((-1,0,0))*2.65
 configs={};shapes={}
 for name,key in [('UpperSupport','top_data'),('RearRibbonGuard','rear_data')]:
  cfg=copy.deepcopy(s[key]);cfg['socket_center_mm']=list(V(*cfg['socket_center_mm'])+V(*s['joint_shift_mm']))
  cfg.update(attachment_radius_mm=2.65,socket_lead_mm=1.,socket_width_mm=3.,socket_thickness_mm=2.2)
  if key=='rear_data':
   cfg['sections']=41;cfg['plugward_flare_deg']=s['plugward_flare_deg']
   cfg['arm'].update(root_mm=s['root_mm'],root_handle_mm=23.,socket_handle_mm=23.,root_width_mm=s['root_width_mm'],root_thickness_mm=s['root_thickness_mm'])
   cfg['arm']['radial_direction']=list(A.Rotation(unit(cfg['socket_axis']),s['attachment_angle_deg']).multVec(unit(cfg['arm']['radial_direction'])))
   width,thickness=s['body_width_mm'],s['body_thickness_mm']
  else:
   cfg['arm'].update(root_handle_mm=5.,socket_handle_mm=4.)
   cfg['arm']['root_mm'][1]+=1.5
   cfg['attachment_height_mm']=5.3
   width,thickness=3.,1.8
  configs[name]=dict(cfg,body_width_mm=width,body_thickness_mm=thickness)
  shapes[name]=geometry(cfg,width,thickness)[0]
 tray=d.getObject('RetainedPCBTray').Shape;socket=d.getObject('RetainedSocket').Shape
 obstacles={name:d.getObject(name).Shape for name in ['RibbonCandidate','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','skull_mount_Baseplate']}
 for parent in ['MeasuredMainPCB','MeasuredSensorHead']:
  for ob in d.getObject(parent).Group:
   if hasattr(ob,'Shape'):sh=ob.Shape.copy();sh.Placement=ob.getGlobalPlacement();obstacles[ob.Name]=sh
 checks={}
 for name,sh in shapes.items():
  checks[name]={'tray_overlap_mm3':sh.common(tray).Volume,'socket_overlap_mm3':sh.common(socket).Volume,'obstacles':{k:{'overlap_mm3':sh.common(o).Volume,'clearance_mm':sh.distToShape(o)[0]} for k,o in obstacles.items()}};print(name,checks[name],flush=True)
 fused=tray.fuse(socket).fuse(shapes['UpperSupport']).fuse(shapes['RearRibbonGuard']).removeSplitter()
 report={'source_checkpoint':m['native_checkpoint'],'source_sha256':m['native_sha256'],'input_ribbon_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'units':'mm','arms':configs,'historical_generator':'designs/mouse-hats/b-flared-loop-r07/flared_arm.py','checks':checks,'carrier_valid':fused.isValid(),'carrier_solids':len(fused.Solids)}
 report['static_pass']=report['carrier_valid'] and report['carrier_solids']==1 and all(row['tray_overlap_mm3']>0 and row['socket_overlap_mm3']>0 and all(o['overlap_mm3']<1e-6 for o in row['obstacles'].values()) for row in checks.values())
 (OUT/'validation.json').write_text(json.dumps(report,indent=2));print('STATIC PASS',report['static_pass'],flush=True)
 for name,sh in shapes.items():ob=d.addObject('Part::Feature',name);ob.Shape=sh
 ob=d.addObject('Part::Feature','StemSupportedCarrier');ob.Shape=fused
 d.recompute();d.saveAs(str(OUT/'mouse-restored-arms-r05.FCStd'));d.Label='Mouse R05 - original arm design with ribbon clearance';d.save()
 return report
if __name__=='__main__':build()





