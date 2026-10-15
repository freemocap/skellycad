from pathlib import Path
import json,sys
import FreeCAD as A,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/blended-arm-r26';O=R/'generated/eye-tracker/rat/blended-arm-r26'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
d=A.openDocument(str(O/'ET-RAT-BLENDED-ARM-R26.FCStd'));m=json.loads((S.parent/'joined-arm-r25/review.json').read_text());old=A.openDocument(str(R/m['native_checkpoint']));report={'fixed_parts':{},'anatomy_crossings':{}}
for name in ['PCB','JST_4pin','eye_primary_Cap','skull_mount_Baseplate','RetainedPCBTray','camera_pcb','M4_lens','IR_LED','IR_LED_001','eye_primary_Holder','eye_primary_Clip','RetainedSocket','DetailedOpticalAxis','RibbonCandidate']:
 a=world(old.getObject(name));b=world(d.getObject(name));err=a.cut(b).Volume+b.cut(a).Volume;assert err<1e-5;assert a.BoundBox.Center.distanceToPoint(b.BoundBox.Center)<1e-6;report['fixed_parts'][name]=err
sk=d.RatDesignSkull.Mesh.copy();sk.Placement=d.RatDesignSkull.getGlobalPlacement()
for name in ['FinishedCarrier','RibbonCandidate']:
 mesh=MeshPart.meshFromShape(Shape=world(d.getObject(name)),LinearDeflection=.06,AngularDeflection=.18,Relative=False);n=mesh.CountFacets;mesh.addMesh(sk);cross=sum((x[0]<n)!=(x[1]<n) for x in mesh.getSelfIntersections());report['anatomy_crossings'][name]=cross;assert cross==0
for name in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 assert old.getObject(name).Mesh.Topology==d.getObject(name).Mesh.Topology
report['anatomy_unchanged']=True
(O/'assembly-validation.json').write_text(json.dumps(report,indent=2));print(report)
