from pathlib import Path
import FreeCAD as A,Mesh
for p in Path('generated/eye-tracker/rat/print-r04/hardware').glob('*.stl'):
 m=Mesh.Mesh(str(p));bad=m.getSelfIntersections();print(p.name,len(bad),flush=True);assert not bad
