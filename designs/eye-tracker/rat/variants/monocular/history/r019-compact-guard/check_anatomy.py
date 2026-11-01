from pathlib import Path
import sys,json
import FreeCAD as A,Mesh,MeshPart
R=Path.cwd();O=R/'generated/eye-tracker/rat/compact-guard-r19'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
from replace_camera import world
d=A.openDocument(str(O/'ET-RAT-COMPACT-GUARD-R19.FCStd'))
guard=MeshPart.meshFromShape(Shape=world(d.RearRibbonGuard),LinearDeflection=.03,AngularDeflection=.12,Relative=False)
guard.write(str(O/'guard.stl'));report={}
for name in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 mesh=d.getObject(name).Mesh.copy();count=mesh.CountFacets;mesh.addMesh(guard)
 crosses=sum((pair[0]<count)!=(pair[1]<count) for pair in mesh.getSelfIntersections())
 report[name]={'surface_crossings':crosses};assert crosses==0,name
(O/'anatomy-validation.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
