from pathlib import Path
import sys,json
import trimesh
out=Path(sys.argv[1]);camera=trimesh.load_mesh(out/'camera-world.stl');points,_=trimesh.sample.sample_surface(camera,2000,seed=13);report={}
for p in out.glob('*-anatomy.stl'):
 m=trimesh.load_mesh(p);inside=m.contains(points)
 report[p.stem]={'watertight':bool(m.is_watertight),'samples':len(points),'camera_samples_inside':int(inside.sum())}
 print(p.stem,report[p.stem],flush=True)
(out/'anatomy-containment.json').write_text(json.dumps(report,indent=2))
