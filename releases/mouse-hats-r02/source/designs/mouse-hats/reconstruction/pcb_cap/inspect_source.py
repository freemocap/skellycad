"""Identify and inspect RightCap from the hash-pinned 58 STEP."""
from pathlib import Path
import hashlib,json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/pcb-cap'
OUT.mkdir(parents=True,exist_ok=True)
path=ROOT/'designs/mouse-hats/old/58nassembly.step'
assert hashlib.sha256(path.read_bytes()).hexdigest()=='3286036e4cbd6b1c993e96079f24afc29d375bedddda2e24fd93b2d18c3c9260'
matches=[s for s in Part.read(str(path)).Solids if len(s.Faces)==69]
assert len(matches)==1
s=matches[0];s.exportBrep(str(OUT/'source.brep'))
print('SOURCE',s.Volume,s.BoundBox)
try:s.check(True);print('BOP passed')
except Exception as e:print(str(e))
data=[]
for i,f in enumerate(s.Faces):
    d=dict(index=i,type=type(f.Surface).__name__,area_mm2=f.Area,normal=list(f.normalAt(0,0)),center_mm=list(f.CenterOfMass),vertices_mm=[list(v.Point) for v in f.OuterWire.OrderedVertexes])
    data.append(d)
    print(i,d['type'],round(f.Area,5),'N',[round(x,5) for x in d['normal']],'C',[round(x,5) for x in d['center_mm']])
(OUT/'faces.json').write_text(json.dumps(data,indent=2)+'\n')
