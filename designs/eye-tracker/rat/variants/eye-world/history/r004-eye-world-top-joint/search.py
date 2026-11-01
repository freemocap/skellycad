from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-top-joint-r04';O=R/'generated/eye-tracker/rat/eye-world-top-joint-r04'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
c=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());B=np.array(c['mount_to_skull'])@np.array(c['sides']['Left']['board_transform']);ll=np.array([.08845911870242962,5.719524249669308,1.607691279838762]);flat=np.array([[x,y,0.] for y in np.linspace(0,g.L,100) for x in [-2.,0.,2.]])
def calc(p):
 pos,rot=g.endpoint(p);h=np.eye(4);h[:3,:3]=B[:3,:3]@rot;h[:3,3]=B[:3,:3]@pos[0]+B[:3,3];rib=g.evaluate(p,flat)[0]@B[:3,:3].T+B[:3,3];return h,h[:3,3]+h[:3,:3]@ll,rib
previous=json.loads((S.parent/'eye-world-ribbon-r02/selected-pose.json').read_text());target=np.array(previous['lens_world_mm'])+[2.,0,0];targetR=np.array([[0,0,1],[0,-1,0],[1,0,0.]])
def residual(p):
 h,l,rib=calc(p);q=p.reshape(3,4);cost=list(((h[:3,:3]-targetR)*1e5).ravel());cost.append((l[0]-target[0])*1e5);cost.extend((l[1:]-target[1:])*.2);cost.append(max(g.zones(p)[-1][-1]-32.6,0)*1e5)
 cost.extend(q[:,2]*3.);return cost
lo=np.tile([3.75,-3.8,-.85,0],3);hi=np.tile([12,3.8,.85,10],3);out=[]
rng=np.random.default_rng(4)
for trial in range(8):
 seed=np.array(previous['parameters']) if trial==0 else np.array(previous['parameters'])+rng.normal(0,.3,12)
 fit=least_squares(residual,np.clip(seed,lo+1e-8,hi-1e-8),bounds=(lo,hi),max_nfev=1000,ftol=1e-11,xtol=1e-11,gtol=1e-10)
 h,l,rib=calc(fit.x);err=float(abs(l[0]-target[0]));re=float(np.linalg.norm(h[:3,:3]-targetR));rec={'parameters':fit.x.tolist(),'head_world':h.tolist(),'lens_world_mm':l.tolist(),'position_error_mm':err,'rotation_error':re,'zone_end_mm':float(g.zones(fit.x)[-1][-1]),'minimum_inside_radius_mm':float(min(fit.x[::4])-.25),'translation_target_mm':[2,0,0],'tray_long_edge_world':[0,-1,0],'forward_axis_world':[1,0,0]};print(trial,rec,flush=True)
 if err<1e-5 and re<1e-7 and rec['zone_end_mm']<32.60001:
  (S/'selected-pose.json').write_text(json.dumps(rec,indent=2));break
else:raise RuntimeError('Exact leveled pose not solved')
