import FreeCAD as A,Part,MeshPart,json
from pathlib import Path
out=Path('generated/eye-tracker/mouse/joined-arms-r06');s=Part.Shape();s.read(str(out/'finished.brep'));before=s.Volume
# Remove only the obsolete raised B label, outside the flat rear tray face.
label=Part.makeBox(3.70677424482636-3.2,3.7,5.8,A.Vector(3.2,11.4,-2.9))
s=s.cut(label).removeSplitter();s.limitTolerance(1e-6);s.check(True);assert s.isValid() and len(s.Solids)==1
m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.03,AngularDeflection=.12,Relative=False);print('removed volume',before-s.Volume,'closed',m.isSolid(),'self',m.hasSelfIntersections(),flush=True)
assert m.isSolid() and not m.hasSelfIntersections();s.exportBrep(str(out/'finished.brep'));(out/'label-cleanup.json').write_text(json.dumps({'removed_obsolete_mark':'raised B on rear tray','removed_volume_mm3':before-s.Volume,'rear_face_x_mm':3.70677424482636},indent=2))
