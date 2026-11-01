from pathlib import Path
import json,subprocess,numpy as np,trimesh,itertools
from scipy.spatial import cKDTree
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-eye-bridge-r02';O=R/'generated/eye-tracker/rat/print-eye-bridge-r02';report=[]
for iteration in range(15):
 subprocess.run([str(R/'.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe'),str(S/'probe_mesh.py')],check=True)
 failures=json.loads((O/'mesh-probe.json').read_text())
 if not any(failures.values()):break
 for name,pairs in failures.items():
  if not pairs:continue
  p=O/'anatomy'/(name+'.stl');m=trimesh.load_mesh(p);before=m.volume;tree=cKDTree(m.vertices);choices=[]
  for triangle in pairs[0]:
   ids=tree.query(np.array(triangle))[1]
   for a,b in itertools.combinations(ids,2):choices.append((np.linalg.norm(m.vertices[a]-m.vertices[b]),int(a),int(b)))
  for length,a,b in sorted(choices):
   if length>.05:continue
   clean=m.copy();faces=clean.faces.copy();faces[faces==b]=a;clean.faces=faces;clean.update_faces(clean.nondegenerate_faces());clean.remove_unreferenced_vertices()
   if clean.is_volume and abs(clean.volume-before)<.01:
    clean.export(p);report.append({'part':name,'collapsed_edge_mm':float(length),'volume_delta_mm3':float(clean.volume-before)});print(report[-1],flush=True);break
  else:raise RuntimeError(('No small safe edge collapse',name,choices))
else:raise RuntimeError('Repair did not converge')
(O/'edge-repair-validation.json').write_text(json.dumps(report,indent=2));print('EDGE_REPAIR_VERIFIED')

