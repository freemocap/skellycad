"""Check the exported hardware and anatomy meshes with FreeCAD's mesh checker."""
from pathlib import Path
import json
import FreeCAD,Mesh
O=Path.cwd()/'generated/eye-tracker/rat/print-r32'
for folder in ['hardware','anatomy']:
 report={}
 for p in (O/folder).glob('*.stl'):
  mesh=Mesh.Mesh(str(p));bad=mesh.getSelfIntersections();report[p.name]={'facets':mesh.CountFacets,'closed':mesh.isSolid(),'self_intersections':len(bad)};print(folder,p.name,report[p.name],flush=True)
 (O/(folder+'-native-mesh-validation.json')).write_text(json.dumps(report,indent=2));assert report and all(v['facets']>0 and v['closed'] and v['self_intersections']==0 for v in report.values())
print('EXPORTED_MESHES_PASS')
