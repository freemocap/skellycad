from pathlib import Path
import numpy as np,trimesh,json,hashlib
R=Path.cwd();S=R/'designs/eye-tracker/rat/bregma-baseplate-r17';O=R/'generated/eye-tracker/rat/bregma-baseplate-r17';O.mkdir(parents=True,exist_ok=True)
for f in [S.parent/'active-model.json',S.parent/'symmetric-design-r16/review.json']:
 a=json.loads(f.read_text());assert hashlib.sha256((R/a['native_checkpoint']).read_bytes()).hexdigest()==a['native_sha256']
m=trimesh.load_mesh(R/'generated/eye-tracker/rat/symmetric-design-r16/rat-skull-symmetric-r16.stl');g=json.loads((S/'source-geometry.json').read_text())
xy=np.array([[x,y] for x in np.arange(-11,-1.99,.4) for y in np.arange(-3,3.01,.4)]);hits,_,_=m.ray.intersects_location(np.c_[xy,np.full(len(xy),10)],np.tile([0,0,-1.],(len(xy),1)),multiple_hits=False)
# Symmetric fit fixes roll at zero and fits the roof's average AP slope.
raw_count=len(hits)
# Reject rays through source-mesh holes that hit internal bone instead of the roof.
hits=hits[abs(hits[:,2]-np.median(hits[:,2]))<.8]
fit=np.linalg.lstsq(np.c_[hits[:,0],np.ones(len(hits))],hits[:,2],rcond=None)[0];n=np.array([-fit[0],0,1.]);n/=np.linalg.norm(n);ap=np.array([n[2],0,-n[0]]);F=np.column_stack([ap,[0,1,0],n]);C=np.column_stack([[1,0,0],g['lateral'],g['normal']]);rot=F@C.T
tip=np.array(g['tip']);bottom=np.array(g['bottom_face_center']);localbottom=(bottom-tip)@C
# Contact-stock convention: lower face center 0.25 mm beneath fitted roof.
h=fit[1]-.25-(rot@(bottom-tip))[2]+fit[0]*(rot@(bottom-tip))[0]
target=np.array([0,0,h]);T=np.eye(4);T[:3,:3]=rot;T[:3,3]=target-rot@tip
plate=trimesh.load_mesh(S/'source-baseplate.stl');plate.apply_transform(T);plate.export(O/'candidate-baseplate.stl')
datum,_,_=m.ray.intersects_location([[0,0,10]],[[0,0,-1]],multiple_hits=False)
result={'units':'mm','transform':T.tolist(),'rostral_tip_design_mm':target.tolist(),'bregma_design_proxy_mm':datum[0].tolist(),'datum_basis':'R16 design midline at atlas-derived bregma AP=0, projected onto symmetric skull; not reidentified specimen suture','tip_definition':'Most rostral vertex of top mating face 5; aligned above bregma in dorsal projection','roof_fit_AP_mm':[-11,-2],'roof_fit_ML_mm':[-3,3],'roof_samples':len(hits),'roof_slope_intercept':fit.tolist(),'roof_fit_rms_mm':float(np.sqrt(np.mean((hits[:,0]*fit[0]+fit[1]-hits[:,2])**2))),'plane_normal':n.tolist(),'lower_face_center_below_fitted_plane_vertical_mm':.25,'plate_bounds_mm':plate.bounds.tolist(),'scope':'Placement study only; inherited tapered base is uncut contact stock; camera assembly not reattached'}
(S/'placement.json').write_text(json.dumps(result,indent=2));print(result)
