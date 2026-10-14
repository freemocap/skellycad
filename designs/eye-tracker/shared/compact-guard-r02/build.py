from pathlib import Path
import json,sys,hashlib
import FreeCAD as A,Part,MeshPart
from guard import build
ROOT=Path(__file__).resolve().parents[4]
f=Path(sys.argv[1]).resolve();cfg=json.loads(f.read_text());sp=cfg['species'];src=ROOT/cfg['source']['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg['source']['sha256']
selected=json.loads((f.parent.parent/'active-model.json').read_text());assert hashlib.sha256((ROOT/selected['native_checkpoint']).read_bytes()).hexdigest()==selected['native_sha256']
d=A.openDocument(str(src));T=A.Placement()
if sp=='rat':T=A.Placement(A.Matrix(*sum(json.loads(d.TargetRecipe.RecipeJSON)['mount_to_skull'],[])))
inv=T.inverse();out=ROOT/'generated/eye-tracker'/sp/f.parent.name;out.mkdir(parents=True,exist_ok=True)
def local(o):
 s=o.Shape.copy();s.Placement=inv.multiply(o.getGlobalPlacement());return s
names=['RetainedPCBTray','RetainedSocket','UpperSupport','RearRibbonGuard','FinishedCarrier','RibbonCandidate','eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','skull_mount_Baseplate','PCB','camera_pcb','JST_4pin','M4_lens','IR_LED','IR_LED_001']
s={n:local(d.getObject(n)) for n in names}
guard=build(cfg['guard']['parameters'],cfg['guard']['outer_mm']);guard.exportBrep(str(out/'guard-mount.brep'))
report={'revision':cfg['revision'],'units':'mm','guard_clearance':{},'attachment':{},'source':cfg['source'],'targeting_recipe':cfg['targeting_recipe']}
for name in ['RibbonCandidate','eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','PCB','camera_pcb','JST_4pin','M4_lens','UpperSupport']:
 overlap=guard.common(s[name]).Volume;gap=guard.distToShape(s[name])[0]
 report['guard_clearance'][name]={'overlap_mm3':overlap,'gap_mm':gap};print(sp,name,'gap',gap,'overlap',overlap,flush=True)
 assert overlap<1e-6,name
 if name=='RibbonCandidate':assert gap>=cfg['minimum_guard_ribbon_gap_mm'],gap
for name in ['RetainedPCBTray','RetainedSocket']:
 v=guard.common(s[name]).Volume;assert v>.1,(name,v);report['attachment'][name]={'engagement_mm3':v}
protected=s['RetainedPCBTray'].multiFuse([s['RetainedSocket'],s['UpperSupport']])
if sp=='mouse':
 # Cutting only the free guard avoids a coincident-surface union in the imported mouse carrier.
 free_guard=s['RearRibbonGuard'].cut(protected,1e-6)
 core=s['FinishedCarrier'].cut(free_guard,1e-6).removeSplitter()
else:
 core=s['FinishedCarrier'].cut(s['RearRibbonGuard']).fuse(protected.common(s['FinishedCarrier'])).removeSplitter()
carrier=core.fuse(guard).removeSplitter();carrier.limitTolerance(1e-6);carrier.check(True);assert carrier.isValid() and len(carrier.Solids)==1
report['carrier']={'valid':True,'solids':len(carrier.Solids),'volume_mm3':carrier.Volume,'previous_volume_mm3':s['FinishedCarrier'].Volume,'old_guard_xmin_mm':s['RearRibbonGuard'].BoundBox.XMin,'new_guard_xmin_mm':guard.BoundBox.XMin}
report['carrier_clearance']={}
for name in ['RibbonCandidate','eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','PCB','camera_pcb','JST_4pin','M4_lens']:
 v=carrier.common(s[name]).Volume;old=s['FinishedCarrier'].common(s[name]).Volume
 report['carrier_clearance'][name]={'overlap_mm3':v,'previous_overlap_mm3':old};assert v<=old+1e-5,(name,v,old)
report['fixed_interfaces']={}
for name in ['RetainedPCBTray','RetainedSocket','UpperSupport']:
 before=s['FinishedCarrier'].common(s[name]);after=carrier.common(s[name]);difference=before.cut(after).Volume+after.cut(before).Volume
 report['fixed_interfaces'][name]={'material_difference_mm3':difference}
 # Root and socket gain engagement material, but cannot lose protected material.
 assert before.cut(after).Volume<1e-6
for name,shape in [('RearRibbonGuard',guard),('FinishedCarrier',carrier)]:
 o=d.getObject(name);parent=o.getGlobalPlacement().multiply(o.Placement.inverse());shape=shape.copy();shape.Placement=parent.inverse().multiply(T).multiply(shape.Placement);o.Shape=shape
report['other_shapes_and_poses_preserved']=True
for name in names:
 if name in ['RearRibbonGuard','FinishedCarrier']:continue
 current=local(d.getObject(name));assert current.cut(s[name]).Volume+s[name].cut(current).Volume<1e-7,name
carrier.exportBrep(str(out/'carrier-mount.brep'))
(out/'solid-validation.json').write_text(json.dumps(report,indent=2)+'\n')
d.recompute();d.Label=cfg['revision']+' — compact front-root ribbon guard';d.saveAs(str(out/(cfg['revision']+'-solid-review.FCStd')))
mesh=MeshPart.meshFromShape(Shape=carrier,LinearDeflection=.03,AngularDeflection=.12,Relative=False)
closed=mesh.isSolid();intersections=mesh.hasSelfIntersections()
report['carrier_mesh']={'closed':closed,'self_intersections':intersections,'export_withheld':not closed or intersections,'linear_deflection_mm':.03,'angular_deflection_rad':.12}
print('carrier tessellation',closed,intersections,flush=True)
if closed and not intersections:mesh.write(str(out/'carrier-review-mount.stl'))
carrier.exportBrep(str(out/'carrier-mount.brep'));d.recompute();d.Label=cfg['revision']+' — compact front-root ribbon guard';d.saveAs(str(out/(cfg['revision']+'.FCStd')))
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('GUARD_CAD_REVIEW_MESH_BLOCKED' if report['carrier_mesh']['export_withheld'] else 'GUARD_OK',sp,flush=True)
