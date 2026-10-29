"""Remove tiny intersecting facets at Boolean seams and verify closed print meshes."""
from pathlib import Path
import json,zipfile
import FreeCAD as A,Mesh
O=Path.cwd()/'generated/eye-tracker/rat/print-eye-bridge-r02';report={}
d=A.newDocument('RatReinforcedEyeBridge');d.Label='RAT R32 EB02 - continuous white eye bridge'
for p in (O/'anatomy').glob('*.stl'):
 m=Mesh.Mesh(str(p));v=m.Volume;repairs=[]
 for k in range(12):
  pairs=m.getSelfIntersections()
  if not pairs:break
  i=min(pairs[0][:2],key=lambda i:m.Facets[i].Area);facet=m.Facets[i]
  assert facet.Area<.005,(p.name,facet.Area)
  repairs.append({'facet_area_mm2':facet.Area,'points_mm':[list(v) for v in facet.Points]});m.collapseFacet(i)
 assert m.isSolid() and not m.hasSelfIntersections(),p.name
 assert abs(m.Volume-v)<.01
 assert not repairs,'Run repair_edges.py before saving the native review'
 report[p.name]={'closed':True,'self_intersections':0,'repairs':repairs,'native_volume_change_mm3':m.Volume-v}
 if p.stem in ['Skull-and-bridge','Sclera','Cornea','Baseplate']:
  o=d.addObject('Mesh::Feature',p.stem.replace('-','_'));o.Label=p.stem;o.Mesh=m
d.recompute();p=O/'RAT-R32-EB02-anatomy-print.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);(O/'native-repair-validation.json').write_text(json.dumps(report,indent=2));print('SAVED_NATIVE_AND_VERIFIED_ALL_MESHES')
