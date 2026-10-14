from pathlib import Path
import FreeCAD as A,Mesh,MeshPart,json,sys
r=Path.cwd();sp=sys.argv[1];folder='compact-guard-r13' if sp=='mouse' else 'compact-guard-r09';out=r/'generated/eye-tracker'/sp/folder;d=A.openDocument(str(next(out.glob('ET-*.FCStd'))));o=d.RearRibbonGuard;s=o.Shape.copy();s.Placement=o.getGlobalPlacement();guard=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False);result={}
for name in (['Skull','Eye1Sclera','Eye1Cornea','Eye2Sclera','Eye2Cornea'] if sp=='mouse' else ['StandardSkull','RightEyeSclera','RightEyeCornea','LeftEyeSclera','LeftEyeCornea']):
 o=d.getObject(name);m=Mesh.Mesh(o.Mesh);m.transform(o.getGlobalPlacement().multiply(o.Placement.inverse()).toMatrix());n=m.CountFacets;m.addMesh(guard);cross=sum((v[0]<n)!=(v[1]<n) for v in m.getSelfIntersections());result[name]={'guard_surface_crossings':cross};print(sp,name,cross,flush=True)
(out/'guard-anatomy.json').write_text(json.dumps(result,indent=2)+'\n')
