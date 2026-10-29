from pathlib import Path
import sys,json,hashlib,zipfile
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/two-arm-r28';O=R/'generated/eye-tracker/rat/two-arm-r28';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
records=json.loads((S/'review-inputs.json').read_text())['inputs'];docs=[]
for rec in [records[0],records[2]]:
 p=R/rec['source_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['source_sha256'];docs.append(A.openDocument(str(p)))
d,old=docs;report={'units':'mm','revision':'ET-RAT-TWO-ARM-R28','sources':[records[0],records[2]],'arms':{},'interfaces':{},'physical_stiffness_verified':False,'full_joint_sweep_verified':False}
fixed=['RetainedSocket','RetainedPCBTray','eye_primary_Holder','skull_mount_Baseplate','camera_pcb','M4_lens']
for n in fixed:
 a,b=world(d.getObject(n)),world(old.getObject(n));delta=a.cut(b).Volume+b.cut(a).Volume;assert delta<1e-5,n
report['r21_attachment_frame_matches_r27']=True
before={n:(d.getObject(n).Shape.copy(),d.getObject(n).getGlobalPlacement()) for n in ['RibbonCandidate','DetailedOpticalAxis','camera_pcb','M4_lens','eye_primary_Holder','skull_mount_Baseplate','PCB']}
rib=world(d.RibbonCandidate);carrier=world(old.FinishedCarrier)
# Retain R27's ribbon exit relief between the two separated tray roots.
sol=json.loads((S.parent/'oval-camera-r21/solution.json').read_text());M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])))
relief=Part.makeBox(1.4,4.5,3.2,A.Vector(4.8,10.53,16.4)).transformed(M.toMatrix());carrier=carrier.cut(relief).removeSplitter()
report['ribbon_exit_relief']='R27 1.4 x 4.5 x 3.2 mm box at local (4.8,10.53,16.4)'

for n in ['UpperSupport','RearRibbonGuard']:
 arm=world(old.getObject(n));checks={'ribbon_gap_mm':arm.distToShape(rib)[0],'ribbon_overlap_mm3':arm.common(rib).Volume,'tray_engagement_mm3':arm.common(world(d.RetainedPCBTray)).Volume,'socket_engagement_mm3':arm.common(world(d.RetainedSocket)).Volume}
 assert checks['ribbon_gap_mm']>.65 and checks['ribbon_overlap_mm3']<1e-6 and min(checks['tray_engagement_mm3'],checks['socket_engagement_mm3'])>.05,checks
 assign(d.getObject(n),arm);report['arms'][n]=checks
assign(d.FinishedCarrier,carrier);assert carrier.isValid() and len(carrier.Solids)==1
# Carry the revised clip from the validated R27 print pack, preserving its mating pose.
p=R/'generated/eye-tracker/rat/print-r27/RAT-R27-clip-C01.FCStd';manifest=json.loads((R/'designs/eye-tracker/rat/print-r27/print-pack.json').read_text());archive=R/'generated/eye-tracker/rat/print-r27/RAT-R27-print-pack.zip'
with zipfile.ZipFile(archive) as z:clip_bytes=z.read('RAT-R27-clip-C01.FCStd')
assert hashlib.sha256(clip_bytes).hexdigest()==manifest['files']['RAT-R27-clip-C01.FCStd'];p=O/'clip-C01-input.FCStd';p.write_bytes(clip_bytes);c=A.openDocument(str(p));clip=c.Clip.Shape.copy();clip.Placement=d.eye_primary_Clip.getGlobalPlacement();assign(d.eye_primary_Clip,clip);report['clip']='R27 C01, hash verified'
for n in ['RibbonCandidate','eye_primary_Holder','eye_primary_Clip','camera_pcb','M4_lens','PCB','JST_4pin','eye_primary_Cap','skull_mount_Baseplate']:
 s=world(d.getObject(n));v=carrier.common(s).Volume;previous=world(old.FinishedCarrier).common(world(old.getObject(n))).Volume if n not in ['RibbonCandidate','eye_primary_Clip'] else 0
 assert v<=previous+1e-5,(n,v,previous);report['interfaces'][n]={'overlap_mm3':v,'r21_inherited_overlap_mm3':previous}
for n,(shape,pose) in before.items():
 o=d.getObject(n);assert o.getGlobalPlacement()==pose;assert len(o.Shape.Faces)==len(shape.Faces) and abs(o.Shape.Volume-shape.Volume)<1e-7 and abs(o.Shape.Area-shape.Area)<1e-7,n;assert len(o.Shape.Vertexes)==len(shape.Vertexes) and all((v.Point-w.Point).Length<1e-8 for v,w in zip(o.Shape.Vertexes,shape.Vertexes)),n
report['camera_ribbon_axis_baseplate_unchanged']=True;report['carrier_valid_single_solid']=True
sk=d.RatDesignSkull.Mesh.copy();sk.Placement=d.RatDesignSkull.getGlobalPlacement();mesh=MeshPart.meshFromShape(Shape=carrier,LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/'carrier.stl'));count=mesh.CountFacets;mesh.addMesh(sk);cross=sum((x[0]<count)!=(x[1]<count) for x in mesh.getSelfIntersections());assert cross==0;report['carrier_skull_surface_crossings']=cross
report['carrier_holder_gap_mm']=carrier.distToShape(world(d.eye_primary_Holder))[0];report['clip_holder_contact_mm3']=world(d.eye_primary_Clip).common(world(d.eye_primary_Holder)).Volume
for n in ['SingleTaperedArm','UpperSupport','RearRibbonGuard','RetainedPCBTray','RetainedSocket']:
 o=d.getObject(n)
 if o and hasattr(o,'Visibility'):o.Visibility=False
d.Label='Rat R28 - two arms, current camera and ribbon';d.recompute();d.saveAs(str(O/'ET-RAT-TWO-ARM-R28.FCStd'));(O/'validation.json').write_text(json.dumps(report,indent=2));(S/'recipe.json').write_text(json.dumps({'revision':report['revision'],'sources':report['sources'],'support_geometry':'R21 paired supports and fused carrier','preserved':'R27 complete camera pose, ribbon, anatomy, baseplate and optical axes','clip':'R27 print C01','units':'mm'},indent=2));print(json.dumps(report,indent=2),flush=True)
