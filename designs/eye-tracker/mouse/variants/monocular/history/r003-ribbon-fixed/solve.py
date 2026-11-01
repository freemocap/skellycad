from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'designs/eye-tracker/mouse/ribbon-fixed-r03'))
import geometry as g
report=json.loads((ROOT/'generated/eye-tracker/mouse/camera-fit-r01/fit-report.json').read_text());goal=np.array(report['head_pose']['translation']);rotation=Rotation.from_quat(report['head_pose']['quaternion_xyzw']).as_matrix()
bounds=(np.array([[3.575,-3.8,-1.1,0],[3.575,-3.8,-1.1,0],[3.575,-3.8,-1.1,0]]).ravel(),np.array([[5.075,-.01,1.1,1],[12,3.8,1.1,3],[12,3.8,1.1,3]]).ravel())
def residual(p):
 pos,R=g.endpoint(p);end=g.zones(p)[-1][-1]
 return np.r_[(pos[0]-goal),Rotation.from_matrix(rotation.T@R).as_rotvec()*8,max(end-(g.L-.3),0)*10]
rng=np.random.default_rng(18);best=None
for i in range(70):
 res=least_squares(residual,rng.uniform(*np.array(bounds)),bounds=bounds,max_nfev=300)
 err=np.linalg.norm(res.fun)
 if best is None or err<best['error']:
  best={'error':err,'parameters':res.x.tolist(),'residual':res.fun.tolist()};print(i,best,flush=True)
 if err<1e-5:break
(ROOT/'generated/eye-tracker/mouse/ribbon-fixed-r03/solve.json').write_text(json.dumps(best,indent=2))
