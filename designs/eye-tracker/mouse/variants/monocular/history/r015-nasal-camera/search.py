from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path.cwd();S=R/'designs/eye-tracker/mouse/nasal-camera-r15';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
b=json.loads((S/'baseline.json').read_text());a=json.loads((S.parent/'landmark-eyes-r04/placement.json').read_text());e=a['eyes'][0];eye=np.array(e['center_world_mm']);axis=np.array(e['axis_world']);old=np.array(b['axis']['origin']);od=np.array(b['axis']['direction']);p0=np.array(b['camera_recipe']['ribbon_parameters']);pos,rot=g.endpoint(p0);head=np.eye(4);head[:3,:3]=rot;head[:3,3]=pos[0];lens_local=rot.T@(old-pos[0]);dist=(old-eye)@axis+3;ideal=(old+np.array(a['skull_basis_columns'])[:,0]*2.5)*.8+(eye+axis*((old-eye)@axis))*.2; desired=(eye-ideal)/np.linalg.norm(eye-ideal)
print('ideal lens shift',ideal-old,'nasal component',(ideal-old)@np.array(a['skull_basis_columns'])[:,0],flush=True)
lo=np.array([[3.75,-3.8,-1.1,0]]*3).ravel();hi=np.array([[7,-.01,1.1,1],[12,3.8,1.1,3],[12,3.8,1.1,3]]).ravel()
def fun(p):
 q,rr=g.endpoint(p);lens=q[0]+rr@lens_local;direction=rr[:,2];delta=eye-lens
 return np.r_[np.cross(delta,direction)*20,(direction-desired)*80,(lens-ideal)*3,max(g.zones(p)[-1][-1]-(g.L-.3),0)*100,(p-p0)*.01]
best=None
for i in range(2):
 seed=p0 if i==0 else best.x+np.random.default_rng(i).normal(0,.25,12)
 res=least_squares(fun,np.clip(seed,lo+1e-7,hi-1e-7),bounds=(lo,hi),max_nfev=600)
 if best is None or np.linalg.norm(res.fun)<np.linalg.norm(best.fun):best=res
 q,rr=g.endpoint(best.x);lens=q[0]+rr@lens_local;direction=rr[:,2];print(i,'miss',np.linalg.norm(np.cross(eye-lens,direction)),'angle',np.degrees(np.arccos(np.clip(direction@-axis,-1,1))),'shift',lens-old,flush=True)
 target=np.eye(4);target[:3,:3]=rr;target[:3,3]=q[0];delta=target@np.linalg.inv(head)
 (S/'solution.json').write_text(json.dumps({'parameters':best.x.tolist(),'delta':delta.tolist(),'head':target.tolist(),'old_head':head.tolist(),'lens':lens.tolist(),'lens_shift':(lens-old).tolist(),'axis':direction.tolist(),'eye_center_miss_mm':float(np.linalg.norm(np.cross(eye-lens,direction))),'axis_angle_deg':float(np.degrees(np.arccos(np.clip(direction@-axis,-1,1)))),'last_bend_end_mm':float(g.zones(best.x)[-1][-1])},indent=2))

