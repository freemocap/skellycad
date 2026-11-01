from pathlib import Path
import FreeCAD,Mesh,json
O=Path.cwd()/'generated/eye-tracker/rat/print-r27';report={}
for p in (O/'anatomy').glob('*.stl'):
 m=Mesh.Mesh(str(p));bad=m.getSelfIntersections();report[p.name]={'facets':m.CountFacets,'closed':m.isSolid(),'self_intersections':len(bad)};print(p.name,report[p.name],flush=True);print(bad[:2],flush=True)
(O/'anatomy-mesh-validation.json').write_text(json.dumps(report,indent=2))


assert all(x['facets']>0 and x['closed'] and x['self_intersections']==0 for x in report.values())
