from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
R=Path.cwd();S=R/'designs/eye-tracker/rat/clear-view-r41';O=R/'generated/eye-tracker/rat/clear-view-r41';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);sides=['Right','Left'];B=[T@np.array(cfg['sides'][s]['board_transform']) for s in sides];ll=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset']);eyes=[np.array([8.263833250818816,y,-6.338181566207952]) for y in [-8.284849782773964,8.284849782773964]]
flat=np.array([[x,y,0.] for y in np.linspace(0,g.L,65) for x in [-2.,0.,2.]])
def calc(p,i):
 pos,rot=g.endpoint(p);h=np.eye(4);h[:3,:3]=rot;h[:3,3]=pos[0];h=B[i]@h;l=h[:3,3]+h[:3,:3]@ll;rib=g.evaluate(p,flat)[0]@B[i][:3,:3].T+B[i][:3,3];return h,l,h[:3,2],rib
lo=np.tile([3.75,-3.8,-.85,0],6);hi=np.tile([12,3.8,.85,3],6)
def residual(p):
 rec=[calc(p[i*12:(i+1)*12],i) for i in range(2)];cost=[]
 for i,(h,l,a,rib) in enumerate(rec):
  delta=eyes[i]-l;dist=np.linalg.norm(delta);q=p[i*12:(i+1)*12].reshape(3,4)
  cost.extend((a-delta/dist)*10000);cost.append(max(g.zones(q.ravel())[-1][-1]-32.6,0)*10000)
  cost.extend((l-np.array([8.,(-1 if i==0 else 1)*27.,8.]))*.04);cost.extend(q[:,2]*.1);cost.extend([max(18-dist,0)*10,max(dist-34,0)*10])
  rel=rib-l;z=rel@a;rho=np.linalg.norm(rel-z[:,None]*a,axis=1);radius=2.5+3.5*np.clip(z/dist,0,1)
  cost.extend(np.maximum(np.minimum(np.minimum(z+.2,dist-z),radius-rho),0)*80)
 cost.extend((rec[0][1]*[1,-1,1]-rec[1][1])*10000);cost.extend((rec[0][2]*[1,-1,1]-rec[1][2])*10000)
 cost.extend((rec[1][0][:3,0]-np.array([1,-1,1])*rec[0][0][:3,0]*roll_sign)*10000)
 return cost
if __name__=='__main__':
 seed0=np.array(json.loads((S.parent/'forward-mount-r39/selected-pose.json').read_text())['parameters']);rng=np.random.default_rng(41);out=[]
 for trial in range(2):
  roll_sign=1 if trial%2==0 else -1
  seed=seed0.copy() if trial<2 else np.array(min([r for r in out if r['roll_sign']==roll_sign],key=lambda r:r['score'])['parameters'])+rng.normal(0,.25,24)
  if trial in [3,5,7,9]:seed[17]*=-1;seed[21]*=-1
  res=least_squares(residual,np.clip(seed,lo+1e-8,hi-1e-8),bounds=(lo,hi),max_nfev=350,ftol=1e-8)
  states=[calc(res.x[j*12:(j+1)*12],j) for j in range(2)]
  r={'trial':trial,'score':float(np.linalg.norm(res.fun)),'roll_sign':roll_sign,'parameters':res.x.tolist(),'heads_world':[h.tolist() for h,l,a,rib in states],'lens_world':[l.tolist() for h,l,a,rib in states],'axis_miss_mm':[float(np.linalg.norm(np.cross(eyes[j]-l,a))) for j,(h,l,a,rib) in enumerate(states)],'symmetry_error_mm':float(np.linalg.norm(states[0][1]*[1,-1,1]-states[1][1])),'zone_end_mm':[g.zones(res.x[j*12:(j+1)*12])[-1][-1] for j in range(2)]};out.append(r);(O/'pose-candidates.json').write_text(json.dumps(sorted(out,key=lambda x:x['score']),indent=2));print(trial,roll_sign,r['score'],r['axis_miss_mm'],r['lens_world'],flush=True)
  if trial>=1 and r['score']<2:break

