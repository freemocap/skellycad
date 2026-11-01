from pathlib import Path
import json,numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();O=R/'generated/eye-tracker/rat/eye-world-print-r06';P=R/'generated/eye-tracker/rat/eye-world-top-joint-r04';H=np.array(json.loads((R/'designs/eye-tracker/rat/eye-world-top-joint-r04/selected-pose.json').read_text())['head_world']);s=Part.Shape();s.read(str(P/'finished-holder.brep'));s=s.transformed(A.Matrix(*np.linalg.inv(H).ravel().tolist()));print('HEAD',flush=True)
for lin,ang in [(.04,.15),(.02,.1),(.08,.2),(.03,.12),(.05,.15),(.01,.08)]:
 base=MeshPart.meshFromShape(Shape=s,LinearDeflection=lin,AngularDeflection=ang,Relative=False);print('base',lin,base.isSolid(),len(base.getSelfIntersections()),flush=True)
 for angle in [0,90,180,270]:
  q=s.transformed(A.Placement(A.Vector(),A.Rotation(A.Vector(0,0,1),angle)).toMatrix());bb=MeshPart.meshFromShape(Shape=q,LinearDeflection=lin,AngularDeflection=ang,Relative=False).BoundBox
  for x,y in [(0,0),(5-bb.XMin,5-bb.YMin),(20,0),(0,20),(-20,0),(100,0),(120,0),(140,0)]:
   test=q.copy();test.translate(A.Vector(x,y,-bb.ZMin));mesh=MeshPart.meshFromShape(Shape=test,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
   if mesh.isSolid() and not mesh.hasSelfIntersections():
    print('PASS',lin,ang,angle,x,y,-bb.ZMin,flush=True);test.exportBrep(str(O/'stable-world-holder-print.brep'));(O/'stable-holder-print.json').write_text(json.dumps({'linear':lin,'angular':ang,'angle':angle,'translation':[x,y,-bb.ZMin]},indent=2));raise SystemExit()
raise RuntimeError('No stable holder print mesh')
