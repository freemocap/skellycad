"""Sample containment separately from the FreeCAD surface intersection checks."""
import argparse,json
from pathlib import Path
import numpy as np,trimesh
p=argparse.ArgumentParser();p.add_argument('out',type=Path);args=p.parse_args();out=args.out
skull=trimesh.load(out/'skull-world.stl',force='mesh');assert skull.is_watertight
report={}
validation=json.loads((out/'validation.json').read_text())
for name in ['FinishedCarrier','eye_primary_Holder','skull_mount_Baseplate','RibbonCandidate','camera_pcb','M4_lens']:
 mesh=trimesh.load(out/(name+'-world.stl'),force='mesh');points,_=trimesh.sample.sample_surface(mesh,600,seed=13);inside=skull.contains(points);_,dist,_=trimesh.proximity.closest_point(skull,points);report[name]={'surface_samples':len(points),'samples_inside_skull_bone':int(inside.sum()),'sampled_min_skull_distance_mm':float(dist.min())};print(name,report[name],flush=True);assert not inside.any() or (name=='skull_mount_Baseplate' and validation['anatomy_surface_checks'][name].get('contact_policy')=='boolean_cut_stock')
(out/'anatomy-containment.json').write_text(json.dumps(report,indent=2))
