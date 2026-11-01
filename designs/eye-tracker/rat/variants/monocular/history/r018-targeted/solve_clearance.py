from pathlib import Path
import sys,json,numpy as np
import FreeCAD as A
from scipy.spatial import cKDTree
from scipy.optimize import least_squares
R=Path.cwd();S=R/'designs/eye-tracker/rat/targeted-r18';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
from refine import sampled_surface
b=json.loads((S/'baseline.json').read_text());sol=json.loads((S/'solution.json').read_text());d=A.openDocument(str(R/b['source']['native_checkpoint']));surf,norm=sampled_surface(d.RetainedPCBTray.Shape,np.random.default_rng(55));tree=cKDTree(surf);flat=np.array([[x,y,0.] for y in np.linspace(.8,12,100) for x in np.linspace(-2,2,9)]);p=np.array(sol['parameters']);eye=np.array(sol['eye_mount_frame']);ea=np.array(sol['eye_axis_mount_frame']);local=np.array(sol['lens_local_offset']);ideal=eye+ea*14
lo=np.array([[3.75,-3.8,-1.1,0]]*3).ravel();hi=np.array([[7,-.01,1.1,3],[12,3.8,1.1,3],[12,3.8,1.1,3]]).ravel()
for iteration in range(5):
 vv,_=g.evaluate(p,flat);dist,idx=tree.query(vv);near=dist<1.;points=flat[near];qs=surf[idx[near]];ns=norm[idx[near]]
 def fun(x):
  q,rr=g.endpoint(x);lens=q[0]+rr@local;direction=rr[:,2];v,_=g.evaluate(x,points);gap=np.sum((v-qs)*ns,axis=1)
  return np.r_[np.cross(eye-lens,direction)*2000,(direction+ea)*50,(lens-ideal)*.4,np.maximum(.5-gap,0)*150,max(g.zones(x)[-1][-1]-(g.L-.3),0)*1000]
 fit=least_squares(fun,np.clip(p,lo+1e-9,hi-1e-9),bounds=(lo,hi),max_nfev=700);p=fit.x;print(iteration,np.linalg.norm(fit.fun),flush=True)
q,rr=g.endpoint(p);head=np.eye(4);head[:3,:3]=rr;head[:3,3]=q[0];old=json.loads((R/'designs/eye-tracker/mouse/nasal-camera-r15/solution.json').read_text());lens=q[0]+rr@local
sol.update(parameters=p.tolist(),head=head.tolist(),delta_relative_R16=(head@np.linalg.inv(np.array(old['head']))).tolist(),delta=(head@np.linalg.inv(np.array(old['old_head']))).tolist(),lens=lens.tolist(),eye_center_miss_mm=float(np.linalg.norm(np.cross(eye-lens,rr[:,2]))),axis_angle_deg=float(np.rad2deg(np.arccos(rr[:,2]@-ea))),forward_mm=float((eye-lens)@rr[:,2]),bend_end_mm=float(g.zones(p)[-1][-1]));(S/'solution.json').write_text(json.dumps(sol,indent=2));print(sol['eye_center_miss_mm'],sol['axis_angle_deg'])
