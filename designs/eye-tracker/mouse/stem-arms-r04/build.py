"""New supports to the stationary socket stem, preserving the seated camera."""
from pathlib import Path
import json,hashlib
import FreeCAD as A,Part
ROOT=Path.cwd();OUT=ROOT/'generated/eye-tracker/mouse/stem-arms-r04';V=A.Vector

def tube(poles,radius):
 curve=Part.BezierCurve();curve.setPoles([V(*p) for p in poles])
 section=Part.Wire([Part.makeCircle(radius,curve.value(0),curve.tangent(0)[0])])
 return Part.Wire([curve.toShape()]).makePipeShell([section],True,False)

def build():
 m=json.loads((ROOT/'designs/eye-tracker/mouse/active-model.json').read_text());assert hashlib.sha256((ROOT/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
 src=ROOT/'generated/eye-tracker/mouse/ribbon-fixed-r03/mouse-fixed-cradle-r03-verified.FCStd';d=A.openDocument(str(src))
 s=json.loads((ROOT/'designs/mouse-hats/b-flared-loop-r07/settings.json').read_text());n=V(*s['rear_data']['socket_axis']);n.normalize();c=V(*s['rear_data']['socket_center_mm'])+V(*s['joint_shift_mm']);center=c+n*3.9
 def radial(v):v=V(*v);v-=n*v.dot(n);v.normalize();return v
 upperend=center+radial((0,1,0))*2.65;rearend=center+radial((-1,0,0))*2.65
 configs={'UpperSupport':{'radius_mm':1.35,'poles_mm':[(4.05,17.7,17.2),(4.05,19.0,34),(4.4,11,34),list(upperend)]},'RearRibbonGuard':{'radius_mm':1.15,'poles_mm':[(4.5,8.2,12.1),(-22,8.2,12.1),(-16,-4,42),list(rearend)]}}
 shapes={};bore=Part.makeCylinder(1.45,12,c+n*2.4,n)
 for name,cfg in configs.items():sh=tube(cfg['poles_mm'],cfg['radius_mm']).cut(bore).removeSplitter();assert sh.isValid();shapes[name]=sh
 tray=d.getObject('RetainedPCBTray').Shape;socket=d.getObject('RetainedSocket').Shape
 obstacles={name:d.getObject(name).Shape for name in ['RibbonCandidate','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','skull_mount_Baseplate']}
 for parent in ['MeasuredMainPCB','MeasuredSensorHead']:
  for ob in d.getObject(parent).Group:
   if hasattr(ob,'Shape'):sh=ob.Shape.copy();sh.Placement=ob.getGlobalPlacement();obstacles[ob.Name]=sh
 checks={}
 for name,sh in shapes.items():
  checks[name]={'tray_overlap_mm3':sh.common(tray).Volume,'socket_overlap_mm3':sh.common(socket).Volume,'obstacles':{k:{'overlap_mm3':sh.common(o).Volume,'clearance_mm':sh.distToShape(o)[0]} for k,o in obstacles.items()}};print(name,checks[name],flush=True)
 fused=tray.fuse(socket).fuse(shapes['UpperSupport']).fuse(shapes['RearRibbonGuard']).removeSplitter()
 report={'source_checkpoint':m['native_checkpoint'],'source_sha256':m['native_sha256'],'input_ribbon_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'units':'mm','arms':configs,'checks':checks,'carrier_valid':fused.isValid(),'carrier_solids':len(fused.Solids)}
 report['static_pass']=report['carrier_valid'] and report['carrier_solids']==1 and all(row['tray_overlap_mm3']>0 and row['socket_overlap_mm3']>0 and all(o['overlap_mm3']<1e-6 for o in row['obstacles'].values()) for row in checks.values())
 (OUT/'validation.json').write_text(json.dumps(report,indent=2));print('STATIC PASS',report['static_pass'],flush=True)
 for name,sh in shapes.items():ob=d.addObject('Part::Feature',name);ob.Shape=sh
 ob=d.addObject('Part::Feature','StemSupportedCarrier');ob.Shape=fused
 d.recompute();d.saveAs(str(OUT/'mouse-stem-arms-r04.FCStd'));d.Label='Mouse R04 - stem supports and ribbon guard';d.save()
 return report
if __name__=='__main__':build()

