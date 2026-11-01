from pathlib import Path
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/mouse/skull-clearance-r18';sh=Part.Shape();sh.read(str(S.parent/'anatomical-mount-r17/baseline-baseplate-world.brep'));MeshPart.meshFromShape(Shape=sh,LinearDeflection=.01,AngularDeflection=.06,Relative=False).write(str(S/'baseplate.stl'));MeshPart.meshFromShape(Shape=sh.Faces[34],LinearDeflection=.005,AngularDeflection=.04,Relative=False).write(str(S/'rear-hole.stl'))
