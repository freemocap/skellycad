import sys,json,math
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0,str(ROOT/'designs/mouse-hats/model'))
from build_stem_blend import App,OUT
doc=App.openDocument(str(OUT/'stem-blended-carrier.FCStd'))
s=doc.BlendedCarrier.Shape
results=[]
for f in s.Faces:
 if type(f.Surface).__name__!='Cylinder' or abs(f.Surface.Radius-3)>1e-6:continue
 for e in f.Edges:
  for g in s.Faces:
   if type(g.Surface).__name__!='Plane' or not any(e.isSame(a) for a in g.Edges):continue
   pt=e.valueAt((e.FirstParameter+e.LastParameter)/2)
   n=g.normalAt(*g.Surface.parameter(pt))
   if abs(n.z)>.1:continue
   m=f.normalAt(*f.Surface.parameter(pt))
   angle=math.degrees(math.acos(max(-1,min(1,abs(n.dot(m))))))
   results.append({'edge_length_mm':e.Length,'normal_mismatch_degrees':angle})
assert len(results)==2 and max(x['normal_mismatch_degrees'] for x in results)<.001,results
(OUT/'tangency-validation.json').write_text(json.dumps(results,indent=2))
print(results)
