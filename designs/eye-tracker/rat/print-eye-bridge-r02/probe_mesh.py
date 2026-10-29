from pathlib import Path
import FreeCAD,Mesh,json
O=Path.cwd()/'generated/eye-tracker/rat/print-eye-bridge-r02';r={}
for n in ['Skull-and-bridge','Sclera','rat-eyes','rat-eyes-embedded-baseplate']:
 m=Mesh.Mesh(str(O/'anatomy'/(n+'.stl')));r[n]=[[[list(v) for v in m.Facets[i].Points] for i in pair[:2]] for pair in m.getSelfIntersections()]
(O/'mesh-probe.json').write_text(json.dumps(r))

