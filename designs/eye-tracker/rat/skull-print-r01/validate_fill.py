from pathlib import Path
import json
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'generated/eye-tracker/rat/skull-print-r01'
m=trimesh.load(OUT/'rat-skull-solid-r01.stl')
def occupied(x,y,z):
 s=trimesh.intersections.mesh_plane(m,[1,0,0],[x,0,0])[:,:,1:]
 a,b=s[:,0],s[:,1]
 cross=(a[:,1]>z)!=(b[:,1]>z)
 a,b=a[cross],b[cross]
 hits=a[:,0]+(z-a[:,1])*(b[:,0]-a[:,0])/(b[:,1]-a[:,1])
 return bool(np.count_nonzero(hits>y)%2)
probes=[[x,y,z] for x in [-20,-15,-10,-5,0] for y in [-1,0,1] for z in [1,2,3]]
assert all(occupied(*p) for p in probes)
orbits=[[.75,-8.35,0],[.75,8.35,0]]
assert not any(occupied(*p) for p in orbits)
r=json.loads((OUT/'validation.json').read_text())
r['braincase_probes']={'points_mm':probes,'all_inside_solid':True}
r['orbit_center_probes']={'points_mm':orbits,'both_outside_solid':True,'scope':'Point checks only; eye/hardware surface clearance and physical fit not established.'}
(OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
print('45 braincase points are solid; both provisional orbital centers remain open.')
