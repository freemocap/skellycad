from pathlib import Path
import json,sys
import FreeCAD as A,Part,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/mouse/nasal-camera-r15';O=R/'generated/eye-tracker/mouse/nasal-camera-r15';d=A.openDocument(str(O/'ET-MOUSE-NASAL-R15.FCStd'))
hardware=Mesh.Mesh()
for n in ['FinishedCarrier','camera_pcb','M4_lens','IR_LED','IR_LED_001','eye_primary_Holder','eye_primary_Clip','RibbonCandidate']:
 o=d.getObject(n);s=o.Shape.copy();s.Placement=o.getGlobalPlacement();hardware.addMesh(MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False))
hardware.write(str(O/'changed-hardware-world.stl'));report={}
for n in ['Skull','Eye1','Eye2']:
 o=d.getObject(n);m=Mesh.Mesh(o.Mesh);m.transform(o.getGlobalPlacement().multiply(o.Placement.inverse()).toMatrix());m.write(str(O/(n+'-anatomy.stl')));k=m.CountFacets;joined=Mesh.Mesh(m);joined.addMesh(hardware);cross=sum((v[0]<k)!=(v[1]<k) for v in joined.getSelfIntersections());report[n]={'surface_crossings':cross};print(n,cross,flush=True)
car=d.FinishedCarrier.Shape;cm=MeshPart.meshFromShape(Shape=car,LinearDeflection=.03,AngularDeflection=.12,Relative=False);report['carrier_mesh']={'closed':cm.isSolid(),'self_intersections':cm.hasSelfIntersections()};print(report['carrier_mesh'],flush=True)
a=d.DetailedOpticalAxis;p=a.getGlobalPlacement();org=p.multVec(a.Origin);direction=p.Rotation.multVec(a.Direction);eye=d.Eye1OpticalFrame.getGlobalPlacement();v=eye.Base-org;ea=eye.Rotation.multVec(A.Vector(0,0,1));report['actual_aim']={'miss_mm':v.cross(direction).Length,'forward_mm':v.dot(direction),'axis_angle_deg':direction.getAngle(-ea)*180/3.141592653589793};(O/'anatomy-validation.json').write_text(json.dumps(report,indent=2));print(report['actual_aim'],flush=True)
