from pathlib import Path
import FreeCAD as A,Part
s=Part.Shape();s.read(str(Path.cwd()/'designs/eye-tracker/mouse/anatomical-mount-r17/baseline-baseplate-world.brep'))
for i,f in enumerate(s.Faces):
 if isinstance(f.Surface,Part.Cylinder):print(i+1,'radius',f.Surface.Radius,'axis',f.Surface.Axis,'center',f.Surface.Center,'bounds',f.BoundBox)
