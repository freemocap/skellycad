from pathlib import Path
import json,numpy as np,trimesh
R=Path.cwd();S=R/'designs/eye-tracker/mouse/skull-clearance-r18';p=json.loads((S/'surface-fit.json').read_text());T=np.array(p['unlifted_transform']);normal=np.array(p['surface_normal_world']);skull=trimesh.load(R/'generated/eye-tracker/mouse/landmark-review-r02/detailed-reference.stl');hole=trimesh.load(S/'rear-hole.stl');axis=np.array([.996194698091746,-.087155742747658,0.]);center=np.array([-3.099789947093754,4.28647574010723,0.]);ts=(hole.vertices-center)@axis;u=np.array([0.,0.,1.]);w=np.cross(axis,u);samples=np.array([center+axis*t+1.45*(u*np.cos(theta)+w*np.sin(theta)) for t in np.linspace(ts.min(),ts.max(),int(np.ceil(np.ptp(ts)/.1))+1) for theta in np.linspace(0,2*np.pi,93) ]);print('samples',len(samples),flush=True)
def gap(T):
 vv=samples@T[:3,:3].T+T[:3,3];mins=[]
 for batch in np.array_split(vv,20):mins.append(trimesh.proximity.closest_point(skull,batch)[1].min())
 return float(min(mins))
old=np.array(json.loads((S.parent/'anatomical-mount-r17/placement.json').read_text())['delta']);print('old',gap(old),flush=True);lift=.75
while True:
 new=T.copy();new[:3,3]+=normal*lift;g=gap(new);print('lift',lift,'gap',g,flush=True)
 if g-.085>=2.5:break
 lift+=.25
 assert lift<6
p.update({'transform':new.tolist(),'raise_along_surface_normal_mm':lift,'rear_hole_sample_minimum_mm':g,'rear_hole_conservative_clearance_mm':g-.085,'clearance_allowance_mm':.085,'clearance_scope':'Entire existing 2.9 mm diameter rear hole wall; no protruding fastener length supplied','samples':len(samples)});(S/'placement.json').write_text(json.dumps(p,indent=2));
# Compare atlas surface area whose centroid is inside the tapered base.
base=trimesh.load(S/'baseplate.stl');report={};cent=skull.triangles_center;region=np.linalg.norm(cent-np.array(json.loads((S.parent/'landmark-eyes-r04/placement.json').read_text())['skull_origin_world_mm']),axis=1)<12;pts=cent[region];area=skull.area_faces[region]
for name,pose in [('R17',old),('R18',new)]:
 q=base.copy();q.apply_transform(pose);inside=q.contains(pts);report[name]={'atlas_surface_area_inside_taper_mm2':float(area[inside].sum()),'inside_triangle_count':int(inside.sum())};print(name,report[name],flush=True)
p['footprint_comparison']=report;(S/'placement.json').write_text(json.dumps(p,indent=2))
