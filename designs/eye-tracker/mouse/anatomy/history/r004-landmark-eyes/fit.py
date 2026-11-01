from pathlib import Path
import json,hashlib,numpy as np,trimesh
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
R=Path.cwd();S=R/'designs/eye-tracker/mouse/landmark-eyes-r04';O=R/'generated/eye-tracker/mouse/landmark-eyes-r04'
ls=json.loads((R/'designs/eye-tracker/mouse/skull-landmarks-study-r01/landmarks.json').read_text())['landmarks'];P={x['source_label']:np.array(x['transferred_assembly_mm']) for x in ls};unit=lambda v:v/np.linalg.norm(v)
x=unit(P['13']-P['16']);y=(P['8']+P['10']-P['9']-P['11'])/2;y=unit(y-x*x.dot(y));z=np.cross(x,y);B=np.column_stack([x,y,z]);assert np.linalg.det(B)>.999999
oldreg=json.loads((R/'designs/eye-tracker/mouse/registered-eyes-study-r01/registration.json').read_text());T0=np.array(oldreg['matrix_source_index_mm_to_assembly']);src=trimesh.load(R/'generated/eye-tracker/mouse/registered-eyes-study-r01/digimouse-head-source.stl');target=trimesh.load(R/'generated/eye-tracker/mouse/landmark-review-r02/detailed-reference.stl')
np.random.seed(441);p,_=trimesh.sample.sample_surface(src,26000);q,_=trimesh.sample.sample_surface(target,40000)
# Restrict fitting to cranium height; the template lacks the source mandible.
keep=((trimesh.transform_points(p,T0)-P['13'])@z)>-5;p=p[keep];q=q[((q-P['13'])@z)>-5];tree=cKDTree(q)
trials=[]
for fraction in [.7,.8,.9]:
 T=T0.copy()
 for i in range(60):
  pts=trimesh.transform_points(p,T);dd,ii=tree.query(pts);keep=dd<np.quantile(dd,fraction);dt,_,_=trimesh.registration.procrustes(pts[keep],q[ii[keep]],reflection=False,scale=True);T=dt@T
 trials.append(T)
T=trials[1];assert np.linalg.det(T[:3,:3])>0
m=src.copy();m.apply_transform(T);m.export(O/'tissue-skull-registered.stl')
np.random.seed(772);evalp,_=trimesh.sample.sample_surface(src,2500);ev=trimesh.transform_points(evalp,T);ev=ev[((ev-P['13'])@z)>-5];_,dist,_=trimesh.proximity.closest_point(target,ev)
annotations=json.loads((S/'tissue-rim-picks.json').read_text());poses=[];old=json.loads((R/'designs/eye-tracker/mouse/adult-anatomy-r11/validation.json').read_text())['eyes']
for k,eye in enumerate(annotations['eyes']):
 pts=[]
 for plane in eye['planes']:
  fixed=plane['fixed_mm']
  for u,v in plane['points_uv_mm']:pts.append([u,v,fixed] if plane['fixed_axis']=='z' else ([fixed,v,u] if plane['fixed_axis']=='x' else [u,fixed,v]))
 pts=np.array(pts);initial=np.r_[pts.mean(0),1.5];fit=lambda a:least_squares(lambda v:np.linalg.norm(a-v[:3],axis=1)-v[3],initial,loss='soft_l1',f_scale=.15).x
 fitted=fit(pts);c=fitted[:3];rad=fitted[3];res=np.linalg.norm(pts-c,axis=1)-rad
 world=trimesh.transform_points(c[None],T)[0];sign=-1 if k==0 else 1;az=np.deg2rad(sign*64);el=np.deg2rad(22);dh=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)]);ds=Rotation.from_euler('y',29,degrees=True).inv().apply(dh);direction=B@ds
 # Reading sensitivity, not biological confidence intervals.
 rng=np.random.default_rng(811+k);centers=np.array([fit(pts+rng.uniform(-.15,.15,pts.shape))[:3] for j in range(150)]);jitter=np.linalg.norm(centers-c,axis=1)
 shifts=[float(np.linalg.norm(trimesh.transform_points(c[None],t)[0]-world)) for t in trials]
 orig=old[eye['eye']];row={'eye':eye['eye'],'center_source_index_mm':c.tolist(),'fitted_source_radius_mm':float(rad),'boundary_fit_rms_mm':float(np.sqrt(np.mean(res**2))),'boundary_points_source_mm':pts.tolist(),'center_world_mm':world.tolist(),'center_skull_mm':(B.T@(world-P['13'])).tolist(),'axis_world':direction.tolist(),'axis_skull':ds.tolist(),'point_reading_perturbation_max_mm':float(jitter.max()),'registration_trim_shift_max_mm':max(shifts),'old_center_shift_mm':float(np.linalg.norm(world-orig['frame_origin_world_mm'])),'old_axis_change_deg':float(np.degrees(np.arccos(np.clip(direction@orig['axis_world'],-1,1))))};poses.append(row)
 for region in ['sclera','cornea','whole']:
  mesh=trimesh.load(R/f'generated/eye-tracker/adult-eyes-r01/mouse-{region}.stl');M=np.eye(4);M[:3,:3]=Rotation.align_vectors([direction],[[0,0,1]])[0].as_matrix();M[:3,3]=world;mesh.apply_transform(M);mesh.export(O/(eye['eye']+'-'+region+'.stl'))
report={'units':'mm','landmark_status':'User visually accepted named R03 landmarks for this model on 2026-10-14; no claim of verified author ID dictionary','origin_landmark':'13 bregma','forward_landmarks':['16','13'],'lateral_pairs':[['9','8'],['11','10']],'skull_basis_columns':B.tolist(),'skull_origin_world_mm':P['13'].tolist(),'source_tissue_to_assembly':T.tolist(),'tissue_registration_target':'Maga detailed atlas in existing assembly frame','registration_cranial_surface_median_mm':float(np.median(dist)),'registration_cranial_surface_p95_mm':float(np.percentile(dist,95)),'head_pitch_deg':-29,'horizon_gaze_azimuth_deg':64,'horizon_gaze_elevation_deg':22,'eyes':poses,'shape_profile':'adult-eyes-r01, dimensions unchanged','physical_fit_verified':False}
(S/'placement.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='eyes'},indent=2));print([(r['eye'],r['center_world_mm'],r['fitted_source_radius_mm'],r['boundary_fit_rms_mm']) for r in poses])
