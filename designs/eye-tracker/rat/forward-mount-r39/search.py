from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
R=Path.cwd();S=R/'designs/eye-tracker/rat/forward-mount-r39';O=R/'generated/eye-tracker/rat/forward-mount-r39';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);sides=['Right','Left'];B=[np.array(cfg['sides'][s]['board_transform']) for s in sides];ll=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset']);eyes=[np.array([8.263833250818816,y,-6.338181566207952]) for y in [-8.284849782773964,8.284849782773964]]
def calc(p,i):
 pos,rot=g.endpoint(p);h=np.eye(4);h[:3,:3]=rot;h[:3,3]=pos[0];h=T@B[i]@h;l=h[:3,3]+h[:3,:3]@ll;return h,l,h[:3,2]
lo=np.tile([3.625,-3.6,-.85,0],6);hi=np.tile([10,3.6,.85,3],6)
def residual(p):
 rec=[calc(p[i*12:(i+1)*12],i) for i in range(2)];cost=[]
 for i,(h,l,a) in enumerate(rec):
  delta=eyes[i]-l;dist=np.linalg.norm(delta);q=p[i*12:(i+1)*12].reshape(3,4)
  cost.extend((a-delta/dist)*1000);cost.append(max(g.zones(q.ravel())[-1][-1]-32.4,0)*100)
  cost.extend((l-np.array([7.,(-1 if i==0 else 1)*24.,2.]))*.08);cost.extend(q[:,2]*.25);cost.extend([max(15-dist,0)*10,max(dist-23,0)*10])
 cost.extend((rec[0][1]*[1,-1,1]-rec[1][1])*100);cost.extend((rec[0][2]*[1,-1,1]-rec[1][2])*1000)
 return cost
rng=np.random.default_rng(39);records=[]
for trial in range(32):
 seed=np.tile([5.,-1.5,0.,.4,4.,1.2,0.,.4,4.,-1.5,0.,.4],2) if trial==0 else rng.uniform(lo,hi)
 if trial%3==0 and records:seed=np.array(min(records,key=lambda r:r['score'])['parameters'])+rng.normal(0,.16,24)
 res=least_squares(residual,np.clip(seed,lo+1e-6,hi-1e-6),bounds=(lo,hi),max_nfev=200,ftol=1e-8)
 rec=[calc(res.x[i*12:(i+1)*12],i) for i in range(2)];r={'trial':trial,'score':float(np.linalg.norm(res.fun)),'parameters':res.x.tolist(),'heads_world':[h.tolist() for h,l,a in rec],'lens_world':[l.tolist() for h,l,a in rec],'axis_miss_mm':[float(np.linalg.norm(np.cross(eyes[i]-l,a))) for i,(h,l,a) in enumerate(rec)],'symmetry_error_mm':float(np.linalg.norm(rec[0][1]*[1,-1,1]-rec[1][1])),'zone_end_mm':[g.zones(res.x[i*12:(i+1)*12])[-1][-1] for i in range(2)]};records.append(r);(O/'pose-candidates.json').write_text(json.dumps(sorted(records,key=lambda r:r['score']),indent=2));print(trial,r['score'],r['axis_miss_mm'],r['lens_world'],flush=True)
 if r['score']<1.2 and max(r['axis_miss_mm'])<.001:break
