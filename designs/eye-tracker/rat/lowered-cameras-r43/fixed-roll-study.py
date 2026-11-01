"""Refit developable ribbon bends to a symmetric 3 mm camera lowering."""
from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
R=Path.cwd();S=Path(__file__).parent;O=R/'generated/eye-tracker/rat/lowered-cameras-r43'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
c=json.loads((S/'recipe.json').read_text());T=np.array(c['mount_to_skull']);ll=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset'])
seed=np.array(json.loads((S.parent/'clear-view-r41/selected-pose.json').read_text())['parameters'])
flat=np.array([[x,y,0.] for y in np.linspace(0,g.L,90) for x in [-2.,0.,2.]])
result={'parameters':[],'heads_world':[],'lens_world':[],'fits':[],'drop_mm':3.}
for i,side in enumerate(['Right','Left']):
 B=T@np.array(c['sides'][side]['board_transform']);old=T@np.array(c['sides'][side]['head']);lens=old[:3,3]+old[:3,:3]@ll;lens[2]-=3
 eye=np.array([8.263833250818816,(-1 if i==0 else 1)*8.284849782773964,-6.338181566207952]);axis=(eye-lens)/np.linalg.norm(eye-lens)
 cross=np.cross(old[:3,2],axis);rotation=Rotation.from_rotvec(cross/np.linalg.norm(cross)*np.arctan2(np.linalg.norm(cross),old[:3,2]@axis)).as_matrix()
 H=old.copy();H[:3,:3]=rotation@old[:3,:3];H[:3,3]=lens-H[:3,:3]@ll;target=np.linalg.inv(B)@H;p0=seed[i*12:(i+1)*12]
 def residual(p):
  pos,rot=g.endpoint(p);rib=g.evaluate(p,flat)[0]@B[:3,:3].T+B[:3,3];rel=rib-lens;z=rel@axis;rho=np.linalg.norm(rel-z[:,None]*axis,axis=1);dist=np.linalg.norm(eye-lens)
  return np.r_[(pos[0]-target[:3,3])*1e5,(rot-target[:3,:3]).ravel()*1e5,max(g.zones(p)[-1][-1]-32.6,0)*1e5,np.maximum(np.minimum(np.minimum(z-2.1,dist-z),2.7+3.5*np.clip(z/dist,0,1)-rho),0)*100,(p-p0)*.002]
 lo=np.tile([3.75,-3.8,-.85,0],3);hi=np.tile([12,3.8,.85,3],3)
 fit=least_squares(residual,np.clip(p0,lo+1e-8,hi-1e-8),bounds=(lo,hi),max_nfev=1200,ftol=1e-10,xtol=1e-11,gtol=1e-9)
 pos,rot=g.endpoint(fit.x);pe=float(np.linalg.norm(pos[0]-target[:3,3]));re=float(np.max(np.abs(rot-target[:3,:3])));print(side,pe,re,'lens',lens,'zone_end',g.zones(fit.x)[-1][-1],flush=True)
 assert pe<1e-5 and re<1e-6 and g.zones(fit.x)[-1][-1]<32.60001
 result['parameters']+=fit.x.tolist();result['heads_world'].append(H.tolist());result['lens_world'].append(lens.tolist());result['fits'].append({'position_error_mm':pe,'rotation_matrix_error':re})
(S/'selected-pose.json').write_text(json.dumps(result,indent=2));(O/'pose-candidates.json').write_text(json.dumps([result],indent=2))
