from pathlib import Path
import sys,json
import FreeCAD as A,Mesh,MeshPart
out=Path(sys.argv[1]);native=next(out.glob('ET-*.FCStd'));d=A.openDocument(str(native));camera=Mesh.Mesh()
for n in ['PCB','camera_pcb','JST_4pin','M4_lens','IR_LED','IR_LED_001','RibbonCandidate']:
 o=d.getObject(n);s=o.Shape.copy();s.Placement=o.getGlobalPlacement()
 camera.addMesh(MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False))
camera.write(str(out/'camera-world.stl'));result={}
names=['Skull','Eye1','Eye2'] if d.getObject('Skull') else ['StandardSkull','RightEyeSclera','RightEyeCornea','LeftEyeSclera','LeftEyeCornea']
for n in names:
 o=d.getObject(n);m=Mesh.Mesh(o.Mesh);m.transform(o.getGlobalPlacement().toMatrix());m.write(str(out/(n+'-anatomy.stl')))
 count=m.CountFacets;test=Mesh.Mesh(m);test.addMesh(camera)
 crosses=sum((row[0]<count)!=(row[1]<count) for row in test.getSelfIntersections())
 result[n]={'surface_crossings':crosses};print(n,crosses,flush=True)
(out/'anatomy-surfaces.json').write_text(json.dumps(result,indent=2))
