from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
R=Path.cwd();S=Path(__file__).parent;O=R/'generated/eye-tracker/rat/lowered-cameras-r43'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
c=json.loads((S/'recipe.json').read_text());T=np.array(c['mount_to_skull']);ll=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset']);sides=['Right','Left'];B=[T@np.array(c['sides'][s]['board_transform']) for s in sides];baseline=json.loads((S.parent/'orthogonal-arms-r42/recipe.json').read_text());old=[T@np.array(baseline['sides'][s]['head']) for s in sides];targets=[h[:3,3]+h[:3,:3]@ll-[0,0,3] for h in old];eyes=[np.array([8.263833250818816,y,-6.338181566207952]) for y in [-8.284849782773964,8.284849782773964]];axes=[(e-l)/np.linalg.norm(e-l) for e,l in zip(eyes,targets)]
seed=np.array(json.loads((S.parent/'clear-view-r41/selected-pose.json').read_text())['parameters']);flat=np.array([[x,y,0.] for y in np.linspace(0,g.L,65) for x in [-2.,0.,2.]])
def calc(p,i):
 pos,rot=g.endpoint(p);h=np.eye(4);h[:3,:3]=rot;h[:3,3]=pos[0];h=B[i]@h;return h,h[:3,3]+h[:3,:3]@ll
def residual(p):
 states=[calc(p[i*12:(i+1)*12],i) for i in range(2)];cost=[]
 for i,(h,l) in enumerate(states):
  q=p[i*12:(i+1)*12];cost.extend((l-targets[i])*1e5);cost.extend((h[:3,2]-axes[i])*1e5);cost.append(max(g.zones(q)[-1][-1]-32.6,0)*1e5)
  rib=g.evaluate(q,flat)[0]@B[i][:3,:3].T+B[i][:3,3];rel=rib-l;z=rel@axes[i];rho=np.linalg.norm(rel-z[:,None]*axes[i],axis=1);dist=np.linalg.norm(eyes[i]-l);cost.extend(np.maximum(np.minimum(np.minimum(z-2.1,dist-z),2.7+3.5*np.clip(z/dist,0,1)-rho),0)*100)
 cost.extend((states[1][0][:3,0]-states[0][0][:3,0]*[1,-1,1])*1e5);cost.extend((p-seed)*.001);return cost
lo=np.tile([3.75,-3.8,-.85,0],6);hi=np.tile([12,3.8,.85,3],6);rng=np.random.default_rng(43);best=None
for trial in range(10):
 p0=seed if trial==0 else best.x+rng.normal(0,.3,24)
 fit=least_squares(residual,np.clip(p0,lo+1e-7,hi-1e-7),bounds=(lo,hi),max_nfev=1000,ftol=1e-10,xtol=1e-11,gtol=1e-9)
 if best is None or np.linalg.norm(fit.fun)<np.linalg.norm(best.fun):best=fit
 states=[calc(fit.x[i*12:(i+1)*12],i) for i in range(2)];pe=max(np.linalg.norm(l-targets[i]) for i,(h,l) in enumerate(states));ae=max(np.linalg.norm(h[:3,2]-axes[i]) for i,(h,l) in enumerate(states));sym=np.max(np.abs(states[1][0][:3,:3]-np.diag([1,-1,1])@states[0][0][:3,:3]@np.diag([1,-1,1])));print(trial,pe,ae,sym,flush=True)
 if pe<1e-5 and ae<1e-7 and sym<1e-6:
  result={'parameters':fit.x.tolist(),'heads_world':[h.tolist() for h,l in states],'lens_world':[l.tolist() for h,l in states],'drop_mm':3.,'position_error_mm':pe,'axis_error':ae,'frame_symmetry_error':sym};(S/'selected-pose.json').write_text(json.dumps(result,indent=2));(O/'pose-candidates.json').write_text(json.dumps([result],indent=2));break
else:raise RuntimeError('No valid paired lowering solution')
