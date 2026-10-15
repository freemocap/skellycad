from pathlib import Path
import json,sys,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path.cwd();S=R/'designs/eye-tracker/mouse/raised-target-r19';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
old=json.loads((S.parent/'nasal-camera-r15/solution.json').read_text());M=np.array(json.loads((S.parent/'skull-clearance-r18/placement.json').read_text())['transform']);target=np.linalg.inv(M)@np.array(old['head']);p0=np.array(old['parameters']);lo=np.array([[3.75,-3.8,-1.1,0]]*3).ravel();hi=np.array([[7,-.01,1.1,3],[12,3.8,1.1,3],[12,3.8,1.1,3]]).ravel()
def fun(p):
 q,rr=g.endpoint(p);return np.r_[(q[0]-target[:3,3])*100,Rotation.from_matrix(target[:3,:3].T@rr).as_rotvec()*800,max(g.zones(p)[-1][-1]-(g.L-.3),0)*100,(p-p0)*1e-5]
res=least_squares(fun,np.clip(p0,lo+1e-9,hi-1e-9),bounds=(lo,hi),max_nfev=900,xtol=1e-12,ftol=1e-12,gtol=1e-12);q,rr=g.endpoint(res.x);assert np.linalg.norm(q[0]-target[:3,3])<1e-5;assert np.linalg.norm(rr-target[:3,:3])<1e-5
D=target@np.linalg.inv(np.array(old['old_head']));sol={'parameters':res.x.tolist(),'head':target.tolist(),'delta':D.tolist(),'delta_relative_R16':(D@np.linalg.inv(np.array(old['delta']))).tolist(),'mount_to_skull':M.tolist(),'endpoint_error_mm':float(np.linalg.norm(q[0]-target[:3,3])),'frame_error':float(np.linalg.norm(rr-target[:3,:3])),'aim_policy':'Preserve validated R15/R16 lens position and aim in skull coordinates; refit to R18 main mount placement'};(S/'solution.json').write_text(json.dumps(sol,indent=2));print('SOLVED',sol['endpoint_error_mm'],sol['frame_error'])
