from pathlib import Path
import hashlib
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/baseplate'
OUT.mkdir(parents=True,exist_ok=True)
path=ROOT/'designs/mouse-hats/old/58nassembly.step'
assert hashlib.sha256(path.read_bytes()).hexdigest()=='3286036e4cbd6b1c993e96079f24afc29d375bedddda2e24fd93b2d18c3c9260'
assembly=Part.read(str(path))
matches=[s for s in assembly.Solids if len(s.Faces)==34]
assert len(matches)==1
source=matches[0]
source.exportBrep(str(OUT/'source.brep'))
print('SOURCE',source.Volume,source.BoundBox)
try:source.check(True)
except Exception as e:print(str(e))
for i,f in enumerate(source.Faces):
    print(i,type(f.Surface).__name__,round(f.Area,6),'N',list(f.normalAt(0,0)),'C',list(f.CenterOfMass))
    if isinstance(f.Surface,Part.Plane):print(' V',[[round(x,7) for x in v.Point] for v in f.OuterWire.OrderedVertexes])
    else:print(' S',f.Surface)
