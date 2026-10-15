from pathlib import Path
import sys,json,numpy as np
import FreeCAD as A
from scipy.spatial import cKDTree
from scipy.optimize import least_squares
R=Path.cwd();S=R/'designs/eye-tracker/rat/neutral-camera-r20';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
from refine import sampled_surface
b=json.loads((S/'baseline.json').read_text());sol=json.loads((S/'solution.json').read_text());d=A.openDocument(str(R/b['source']['native_checkpoint']));surf,norm=sampled_surface(d.RetainedPCBTray.Shape,np.random.default_rng(55));tree=cKDTree(surf);flat=np.array([[x,y,0.] for y in np.linspace(.8,12,100) for x in np.linspace(-2,2,9)]);p=np.array(sol['parameters']);eye=np.array(sol['eye_mount_frame']);ea=np.array(sol['eye_axis_mount_frame']);local=np.array(sol['lens_local_offset']);ideal=eye+ea*14
lo=np.array([[3.75,-4.8,-1.1,0]]*3).ravel();hi=np.array([[7,4.8,1.1,5],[12,4.8,1.1,5],[12,4.8,1.1,5]]).ravel()
best=None
rng=np.random.default_rng(20)
for iteration in range(12):
 seed=np.clip(p+rng.normal(0,[1,1.5,.4,.8]*3),lo+1e-8,hi-1e-8); seed[1]=abs(seed[1])
 def fun(x):
  q,rr=g.endpoint(x);lens=q[0]+rr@local;direction=rr[:,2]
  return np.r_[np.cross(eye-lens,direction)*2000,(direction+ea)*1000,max(8-(eye-lens)@direction,0)*1000,max(g.zones(x)[-1][-1]-(g.L-.3),0)*2000,(lens-ideal)*.02]
 fit=least_squares(fun,seed,bounds=(lo,hi),max_nfev=350)
 if best is None or np.linalg.norm(fit.fun)<np.linalg.norm(best.fun):best=fit
 print(iteration,np.linalg.norm(best.fun),flush=True)
p=best.x
q,rr=g.endpoint(p);head=np.eye(4);head[:3,:3]=rr;head[:3,3]=q[0];old=json.loads((R/'designs/eye-tracker/mouse/nasal-camera-r15/solution.json').read_text());lens=q[0]+rr@local
sol.update(parameters=p.tolist(),head=head.tolist(),delta_relative_R16=(head@np.linalg.inv(np.array(old['head']))).tolist(),delta=(head@np.linalg.inv(np.array(old['old_head']))).tolist(),lens=lens.tolist(),eye_center_miss_mm=float(np.linalg.norm(np.cross(eye-lens,rr[:,2]))),axis_angle_deg=float(np.rad2deg(np.arccos(rr[:,2]@-ea))),forward_mm=float((eye-lens)@rr[:,2]),bend_end_mm=float(g.zones(p)[-1][-1]));(S/'positive-solution.json').write_text(json.dumps(sol,indent=2));print(sol['eye_center_miss_mm'],sol['axis_angle_deg'])
