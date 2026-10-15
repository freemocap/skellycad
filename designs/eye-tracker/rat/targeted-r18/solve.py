from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
R=Path.cwd();S=R/'designs/eye-tracker/rat/targeted-r18';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
b=json.loads((S/'baseline.json').read_text());old=json.loads((R/'designs/eye-tracker/mouse/nasal-camera-r15/solution.json').read_text());M=np.array(b['mount_to_skull']);Mi=np.linalg.inv(M);e=json.loads((S.parent/'registered-eyes-r14/placement.json').read_text())['eyes'][1];eye=(Mi@np.r_[e['center_mm'],1])[:3];ea=Mi[:3,:3]@np.array(e['axis']);head=np.array(old['head']);lenslocal=head[:3,:3].T@(np.array(b['axis']['origin'])-head[:3,3]);p0=np.array(old['parameters']);ideal=eye+ea*14
lo=np.array([[3.75,-3.8,-1.1,0]]*3).ravel();hi=np.array([[7,-.01,1.1,3],[12,3.8,1.1,3],[12,3.8,1.1,3]]).ravel()
def fun(p):
 q,rr=g.endpoint(p);lens=q[0]+rr@lenslocal;delta=eye-lens;direction=rr[:,2];forward=delta@direction
 return np.r_[np.cross(delta,direction)*150,(direction+ea)*60,(lens-ideal)*.6,max(9-forward,0)*100,max(g.zones(p)[-1][-1]-(g.L-.3),0)*300,(p-p0)*.0001]
best=None
for i in range(6):
 seed=p0 if i==0 else best.x+np.random.default_rng(i).normal(0,.5,12)
 fit=least_squares(fun,np.clip(seed,lo+1e-7,hi-1e-7),bounds=(lo,hi),max_nfev=700)
 if best is None or np.linalg.norm(fit.fun)<np.linalg.norm(best.fun):best=fit
 q,rr=g.endpoint(best.x);lens=q[0]+rr@lenslocal;target=np.eye(4);target[:3,:3]=rr;target[:3,3]=q[0]
 sol={'parameters':best.x.tolist(),'head':target.tolist(),'old_head':head.tolist(),'delta_relative_R16':(target@np.linalg.inv(head)).tolist(),'delta':(target@np.linalg.inv(np.array(old['old_head']))).tolist(),'mount_to_skull':M.tolist(),'lens_local_offset':lenslocal.tolist(),'eye_mount_frame':eye.tolist(),'eye_axis_mount_frame':ea.tolist(),'lens':lens.tolist(),'eye_center_miss_mm':float(np.linalg.norm(np.cross(eye-lens,rr[:,2]))),'axis_angle_deg':float(np.rad2deg(np.arccos(np.clip(rr[:,2]@-ea,-1,1)))),'forward_mm':float((eye-lens)@rr[:,2]),'bend_end_mm':float(g.zones(best.x)[-1][-1])}
 (S/'solution.json').write_text(json.dumps(sol,indent=2));print(i,sol['eye_center_miss_mm'],sol['axis_angle_deg'],sol['forward_mm'],sol['bend_end_mm'],flush=True)
