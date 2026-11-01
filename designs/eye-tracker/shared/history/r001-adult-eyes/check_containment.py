from pathlib import Path
import json,numpy as np,trimesh
root=Path.cwd()
for sp,rev in [('mouse','adult-anatomy-r11'),('rat','adult-anatomy-r07')]:
 out=root/'generated/eye-tracker'/sp/rev;skull=trimesh.load_mesh(out/'skull-world.stl');hardware=trimesh.load_mesh(out/'hardware-world.stl');result={}
 for file in out.glob('*Eye*-world.stl'):
  eye=trimesh.load_mesh(file);points,_=trimesh.sample.sample_surface(eye,3000,seed=16)
  inside=skull.contains(points);depth=skull.nearest.on_surface(points[inside])[1] if inside.any() else np.array([0])
  hi=hardware.contains(points)
  row={'eye_watertight':bool(eye.is_watertight),'surface_samples':len(points),'eye_samples_inside_skull':int(inside.sum()),'max_sampled_skull_penetration_mm':float(depth.max()),'eye_samples_inside_hardware':int(hi.sum())}
  # Evaluate nearby skull vertices too; narrow overlaps can miss eye surface samples.
  near=skull.vertices[np.all((skull.vertices>=eye.bounds[0])&(skull.vertices<=eye.bounds[1]),axis=1)]
  ins=eye.contains(near);d=eye.nearest.on_surface(near[ins])[1] if ins.any() else np.array([0])
  row.update(skull_vertices_inside_eye=int(ins.sum()),max_skull_vertex_penetration_mm=float(d.max()))
  result[file.stem]=row;print(sp,file.stem,row,flush=True)
 (out/'containment.json').write_text(json.dumps(result,indent=2)+'\n')
