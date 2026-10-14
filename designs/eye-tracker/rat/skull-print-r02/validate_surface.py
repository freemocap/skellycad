from pathlib import Path
import json,numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'generated/eye-tracker/rat/skull-print-r02'
src=trimesh.load(ROOT/'designs/eye-tracker/rat/references/skull/aligned-r01/rat-skull-standard-aligned-r01.stl')
new=trimesh.load(OUT/'rat-skull-detailed-solid-r02.stl');old=trimesh.load(ROOT/'generated/eye-tracker/rat/skull-print-r01/rat-skull-solid-r01.stl')
x,y=np.meshgrid(np.arange(-23,23,.35),np.arange(-11.5,11.5,.35));rays=np.column_stack([x.ravel(),y.ravel(),np.full(x.size,15.)]);dirs=np.tile([0,0,-1.],(len(rays),1))
loc,_,_=src.ray.intersects_location(rays,dirs,multiple_hits=False);loc=loc[loc[:,2]>1]
report={}
for label,m in [('r01',old),('r02',new)]:
 _,d,_=trimesh.proximity.closest_point(m,loc)
 report[label]=dict(samples=len(d),max_mm=float(d.max()),p99_mm=float(np.quantile(d,.99)),p95_mm=float(np.quantile(d,.95)),median_mm=float(np.median(d)),within_0p001_mm=int((d<.001).sum()),over_0p05_mm=int((d>.05).sum()))
 print(label,report[label])
 if label=='r02': assert d.max()<.001
probes=np.array([[x,y,z] for x in [-20,-15,-10,-5,0] for y in [-1,0,1] for z in [1,2,3]])
assert new.contains(probes).all(); assert not new.contains([[.75,-8.35,0],[.75,8.35,0]]).any()
print('fill',new.contains(probes).sum(),len(probes));print('orbits',new.contains([[.75,-8.35,0],[.75,8.35,0]]))
r=json.loads((OUT/'validation.json').read_text());r['dorsal_surface_comparison']=report;r['braincase_probes_inside']=int(new.contains(probes).sum());r['braincase_probes_mm']=probes.tolist();r['orbit_centers_outside']=bool(not new.contains([[.75,-8.35,0],[.75,8.35,0]]).any());(OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n')

