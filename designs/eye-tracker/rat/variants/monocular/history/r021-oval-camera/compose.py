from pathlib import Path
import sys,json,hashlib
import FreeCAD as A,Part,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/oval-camera-r21';O=R/'generated/eye-tracker/rat/oval-camera-r21';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
for f in [S.parent/'bregma-baseplate-r17/review.json',S.parent/'symmetric-design-r16/review.json']:
 a=json.loads(f.read_text());assert hashlib.sha256((R/a['native_checkpoint']).read_bytes()).hexdigest()==a['native_sha256']
report=json.loads((O/'validation.json').read_text());assert all(v['overlap_mm3']<1e-6 for v in report['ribbon'].values())
d=A.openDocument(str(O/'ET-RAT-OVAL-R21.FCStd'));sol=json.loads((S/'solution.json').read_text());M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])))
for name in ['eye_primary_UpperCatch','eye_primary_UpperRail','eye_primary_SideLedge']:
 o=d.getObject(name);sh=world(o);sh.Placement=M.multiply(sh.Placement);assign(o,sh)
base=Part.Shape();base.read(str(S.parent/'bregma-baseplate-r17/source-baseplate.brep'));D=A.Placement(A.Matrix(*sum(json.loads((S.parent/'bregma-baseplate-r17/placement.json').read_text())['transform'],[])));base.Placement=D.multiply(base.Placement);actual=world(d.skull_mount_Baseplate);difference=base.cut(actual).Volume+actual.cut(base).Volume;assert difference<1e-5
skull=d.addObject('Mesh::Feature','RatDesignSkull');skull.Mesh=Mesh.Mesh(str(R/'generated/eye-tracker/rat/symmetric-design-r16/rat-skull-symmetric-r16.stl'));skull.Label='Rat symmetric design skull R16'
eyes=json.loads((S.parent/'registered-eyes-r14/placement.json').read_text())['eyes']
for e in eyes:
 side=e['side']
 for region in ['sclera','cornea']:
  o=d.addObject('Mesh::Feature','Rat'+side+region.title());o.Mesh=Mesh.Mesh(str(R/'generated/eye-tracker/rat/registered-eyes-r14'/(side+'-'+region+'.stl')))
 c=A.Vector(*e['center_mm']);axis=A.Vector(*e['axis']);o=d.addObject('Part::Feature','Rat'+side+'OpticalAxis');o.Shape=Part.makeLine(c-axis*3.04,c+axis*11);o.addProperty('App::PropertyVector','EyeCenter');o.EyeCenter=c;o.addProperty('App::PropertyVector','OutwardDirection');o.OutwardDirection=axis
a=d.DetailedOpticalAxis;p=a.getGlobalPlacement();origin=p.multVec(a.Origin);direction=p.Rotation.multVec(a.Direction);e=eyes[1];delta=A.Vector(*e['center_mm'])-origin;angle=direction.getAngle(-A.Vector(*e['axis']))*180/3.141592653589793
validation={'accepted_baseplate_difference_mm3':difference,'actual_aim':{'origin':list(origin),'direction':list(direction),'miss_mm':delta.cross(direction).Length,'forward_mm':delta.dot(direction),'opposing_eye_axis_angle_deg':angle},'anatomy':{}}
assert delta.cross(direction).Length<.02 and delta.dot(direction)>0
hardware=Mesh.Mesh()
for name in ['FinishedCarrier','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','RibbonCandidate','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
 sh=world(d.getObject(name));mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.05,AngularDeflection=.15,Relative=False);mesh.write(str(O/(name+'-world.stl')));hardware.addMesh(mesh)
for name,mesh in [('Skull',skull.Mesh)]+[(e['side'],Mesh.Mesh(str(R/'generated/eye-tracker/rat/registered-eyes-r14'/(e['side']+'-sclera.stl')))) for e in eyes]:
 count=mesh.CountFacets;joined=Mesh.Mesh(mesh);joined.addMesh(hardware);pairs=joined.getSelfIntersections();cross=sum((ids[0]<count)!=(ids[1]<count) for ids in pairs);validation['anatomy'][name]={'surface_crossings':cross};print(name,cross,flush=True)
carrier=MeshPart.meshFromShape(Shape=world(d.FinishedCarrier),LinearDeflection=.03,AngularDeflection=.12,Relative=False);validation['carrier_mesh']={'closed':carrier.isSolid(),'self_intersections':carrier.hasSelfIntersections()}
(O/'anatomy-validation.json').write_text(json.dumps(validation,indent=2));d.recompute();d.save();print(validation,flush=True)


