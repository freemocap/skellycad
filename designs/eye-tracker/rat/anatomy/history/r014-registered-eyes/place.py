from pathlib import Path
import json,hashlib,numpy as np,trimesh
from scipy.optimize import least_squares
R=Path.cwd();S=R/'designs/eye-tracker/rat/registered-eyes-r14';O=R/'generated/eye-tracker/rat/registered-eyes-r14';O.mkdir(parents=True,exist_ok=True)
for path in [S.parent/'active-model.json',S.parent/'surface-landmarks-r13/review.json']:
 a=json.loads(path.read_text());assert hashlib.sha256((R/a['native_checkpoint']).read_bytes()).hexdigest()==a['native_sha256']
definition=json.loads((R/'designs/eye-tracker/shared/adult-eyes-r01/rat-definition.json').read_text());E=R/'generated/eye-tracker/adult-eyes-r01';eye=trimesh.load_mesh(E/'rat-whole.stl');cornea=trimesh.load_mesh(E/'rat-cornea.stl');sclera=trimesh.load_mesh(E/'rat-sclera.stl')
assert all(m.is_volume for m in [eye,cornea,sclera]);assert np.allclose(eye.extents,[6.41,6.41,6.291],atol=1e-5);assert np.allclose(cornea.extents[:2],[5.64,5.64],atol=1e-5)
# Rotation-symmetric profile reconstructed directly from saved eye mesh.
z=np.unique(eye.vertices[:,2]);rad=np.array([np.linalg.norm(eye.vertices[eye.vertices[:,2]==v,:2],axis=1).max() for v in z])
skull=trimesh.load_mesh(R/'generated/eye-tracker/rat/skull-registration-r12/rat-skull-high-res-refined-atlas-frame-r12.stl');pts=np.vstack([skull.vertices,skull.triangles_center]);T=np.array(json.loads((S.parent/'skull-registration-r12/registration.json').read_text())['source_to_atlas']);old=[(T@np.array([.75,sign*8.35,0,1]))[:3] for sign in [1,-1]];seed=np.array([np.mean([p[0] for p in old]),np.mean([abs(p[1]) for p in old]),np.mean([p[2] for p in old])])
def rotation(sign,az=70,el=15):
 a,e=np.deg2rad([az,el]);axis=np.array([np.cos(e)*np.cos(a),sign*np.cos(e)*np.sin(a),np.sin(e)]);x=np.cross([0,0,1],axis);x/=np.linalg.norm(x);y=np.cross(axis,x);return np.column_stack([x,y,axis])
rot=[rotation(s) for s in [1,-1]];crops=[pts[np.linalg.norm(pts-c,axis=1)<6] for c in old]
def intrusion(p,sign,B,points):
 c=p*np.array([1,sign,1]);loc=(points-c)@B;rr=np.linalg.norm(loc[:,:2],axis=1);profile=np.interp(loc[:,2],z,rad,left=0,right=0);return np.maximum(0,profile+.10-rr)*((loc[:,2]>z[0])&(loc[:,2]<z[-1]))
def residual(p):return np.r_[(p-seed)*2,*[intrusion(p,s,b,q)*4 for s,b,q in zip([1,-1],rot,crops)]]
fit=least_squares(residual,seed,bounds=(seed-[1.5,1.5,1.5],seed+[1.5,1.5,1.5]),diff_step=1e-4,max_nfev=180);p=fit.x;print('seed / solution',seed,p,'success',fit.success,flush=True)
report={'units':'mm','skull_frame':'X anterior, Y left, Z superior; bregma origin','model':'Hughes exterior retained; interpolated sclera and oblate cornea','dimensions_mm':{k:definition[k] for k in ['width_mm','external_length_mm','limbus_diameter_mm','anterior_apical_radius_mm','posterior_apical_radius_mm']},'mesh_dimensions_verified':True,'neutral_azimuth_deg':70,'neutral_elevation_deg':15,'gaze_basis':'Engineering neutral near inherited lateral-forward-up pose; not a measured universal rest gaze','center_basis':'Transformed prior orbital estimate, bilateral symmetry and minimal motion penalized against sampled bone intrusion; no paired soft tissue','seed_AP_absML_DV_mm':seed.tolist(),'fitted_AP_absML_DV_mm':p.tolist(),'fit_success':bool(fit.success),'position_uncertainty_sweep_mm':.5,'angle_uncertainty_sweep_deg':10,'eyes':[]}
for sign,side,B,q,c0 in zip([1,-1],['Left','Right'],rot,crops,old):
 c=p*np.array([1,sign,1]);pose=np.eye(4);pose[:3,:3]=B;pose[:3,3]=c
 for region,mesh in [('sclera',sclera),('cornea',cornea)]:
  m=mesh.copy();m.apply_transform(pose);m.export(O/(side+'-'+region+'.stl'))
 # Independent dense barycentric sampling of nearby triangles, including edges.
 triangles=skull.triangles[np.linalg.norm(skull.triangles_center-c,axis=1)<7]
 dense=np.vstack([(triangles[:,0]*i+triangles[:,1]*j+triangles[:,2]*(12-i-j))/12 for i in range(13) for j in range(13-i)])
 q=dense
 depth=intrusion(p,sign,B,q);sensitivity=[]
 for az,el in [(60,15),(80,15),(70,5),(70,25)]:
  dep=intrusion(p,sign,rotation(sign,az,el),q);sensitivity.append({'azimuth':az,'elevation':el,'max_radial_clearance_deficit_mm':float(dep.max())})
 positions=[]
 for coordinate in range(3):
  for shift in [-.5,.5]:
   trial=p.copy();trial[coordinate]+=shift;dep=intrusion(trial,sign,B,q)
   positions.append({'coordinate':['AP','absML','DV'][coordinate],'shift_mm':shift,'max_sampled_radial_penetration_mm':float(max(0,dep.max()-.1))})
 report['eyes'].append({'side':side,'center_mm':c.tolist(),'axis':B[:,2].tolist(),'pose':pose.tolist(),'corneal_apex_mm':(c+B[:,2]*definition['apex_z_mm']).tolist(),'center_shift_from_previous_mm':float(np.linalg.norm(c-c0)),'sample_count':len(q),'max_radial_clearance_deficit_mm':float(depth.max()),'max_sampled_radial_penetration_mm':float(max(0,depth.max()-.1)),'samples_in_clearance_margin':int((depth>0).sum()),'angular_sensitivity':sensitivity,'position_sensitivity':positions})
assert abs(sclera.volume+cornea.volume-eye.volume)<1e-4
assert abs(2.9297427871121955**2/2.8949048224741776-2.965)<1e-9
report['validation_scope']='Closed positive eye meshes; partition volumes; extents and analytical corneal apical radius. Independent local skull triangle barycentric sampling (12 subdivisions), not continuous collision proof. Sensitivity ranges are chosen scenarios, not confidence intervals.'
(S/'placement.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(7,5));lim=definition['limbus_z_mm'];ax.plot(z[z<=lim],rad[z<=lim],label='Sclera: interpolated exterior');ax.plot(z[z>=lim],rad[z>=lim],label='Cornea: oblate cap');ax.plot(z,-rad,color='.5');ax.axvline(lim,color='.7',ls='--');ax.set(xlabel='Optical-axis coordinate (mm)',ylabel='Radius (mm)',title='Rat eye exterior: width 6.410 mm; axial length 6.291 mm');ax.axis('equal');ax.legend();fig.tight_layout();fig.savefig(O/'eye-profile.png')
