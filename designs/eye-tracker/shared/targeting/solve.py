"""Solve an unstretched camera ribbon against fixed endpoint frames."""
import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import ribbon_geometry as g

def solve(recipe_path,out):
 cfg=json.loads(Path(recipe_path).read_text());out=Path(out);target=np.array(json.loads((out/'target.json').read_text())['sensor_in_mount']);p0=np.array(cfg['ribbon_seed'])
 bounds=g.parameter_bounds(cfg['ribbon_bounds'])
 def residual(p):
  pos,R=g.endpoint(p)
  return np.r_[(pos[0]-target[:3,3])*100,Rotation.from_matrix(target[:3,:3].T@R).as_rotvec()*800,max(g.zones(p)[-1][-1]-(g.L-.3),0)*100,(p-p0)*1e-5]
 rng=np.random.default_rng(23);results=[]
 for i in range(16):
  x=np.clip(p0 if i==0 else p0+rng.normal(0,.5,12),np.array(bounds[0])+1e-9,np.array(bounds[1])-1e-9)
  res=least_squares(residual,x,bounds=bounds,max_nfev=700,ftol=1e-11,xtol=1e-11,gtol=1e-11);pos,R=g.endpoint(res.x);err=np.linalg.norm(pos[0]-target[:3,3]);frame=np.linalg.norm(R-target[:3,:3]);print(i,'endpoint',err,'frame',frame,flush=True)
  if err<1e-5 and frame<1e-5 and g.zones(res.x)[-1][-1]<g.L-.299:
   record={'parameters':res.x.tolist(),'endpoint_error_mm':float(err),'frame_error':float(frame),'straight_entry_mm':g.L-g.zones(res.x)[-1][-1]};results.append(record);(out/'solve.json').write_text(json.dumps(record,indent=2));break
 if not results:raise ValueError('No endpoint-constrained ribbon solution; change explicit camera pose or bounds')
 return results[0]
