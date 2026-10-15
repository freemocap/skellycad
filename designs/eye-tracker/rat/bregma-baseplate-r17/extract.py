from pathlib import Path
import FreeCAD as A,Part,Mesh,json
R=Path.cwd();S=R/'designs/eye-tracker/rat/bregma-baseplate-r17';s=Part.Shape();s.read(str(S/'source-baseplate.brep'));normal=s.Faces[4].normalAt(0,0);x=A.Vector(1,0,0);y=normal.cross(x);p=max(s.Faces[4].Vertexes,key=lambda v:v.Point.x).Point
mesh=Mesh.Mesh(s.tessellate(.05));mesh.write(str(S/'source-baseplate.stl'))
(S/'source-geometry.json').write_text(json.dumps({'tip':list(p),'normal':list(normal),'lateral':list(y),'bottom_face_center':list(s.Faces[6].CenterOfMass),'volume':s.Volume,'valid':s.isValid(),'cylinders': [{'face':i+1,'radius':f.Surface.Radius,'center':list(f.CenterOfMass)} for i,f in enumerate(s.Faces) if isinstance(f.Surface,Part.Cylinder)]},indent=2))
print((S/'source-geometry.json').read_text())
