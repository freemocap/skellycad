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
  cost.extend((a-delta/dist)*100000);cost.append(max(g.zones(q.ravel())[-1][-1]-32.4,0)*10000)
  cost.extend((l-np.array([7.,(-1 if i==0 else 1)*24.,2.]))*.08);cost.extend(q[:,2]*.25);cost.extend([max(15-dist,0)*10,max(dist-23,0)*10])
 cost.extend((rec[0][1]*[1,-1,1]-rec[1][1])*10000);cost.extend((rec[0][2]*[1,-1,1]-rec[1][2])*100000)
 cost.extend((rec[1][0][:3,0]-np.array([1,-1,1])*rec[0][0][:3,0]*roll_sign)*10000)
 return cost


records=json.loads((O/'refined-candidates.json').read_text());out=[]
for roll_sign in [-1,1]:
 for i,rec in enumerate(records[:4]):
  res=least_squares(residual,rec['parameters'],bounds=(lo,hi),max_nfev=500,ftol=1e-10,xtol=1e-10,gtol=1e-10)
  states=[calc(res.x[j*12:(j+1)*12],j) for j in range(2)]
  r={'score':float(np.linalg.norm(res.fun)),'roll_sign':roll_sign,'parameters':res.x.tolist(),'heads_world':[h.tolist() for h,l,a in states],'lens_world':[l.tolist() for h,l,a in states],'axis_miss_mm':[float(np.linalg.norm(np.cross(eyes[j]-l,a))) for j,(h,l,a) in enumerate(states)],'symmetry_error_mm':float(np.linalg.norm(states[0][1]*[1,-1,1]-states[1][1])),'roll_error':float(np.linalg.norm(states[1][0][:3,0]-np.array([1,-1,1])*states[0][0][:3,0]*roll_sign)),'zone_end_mm':[g.zones(res.x[j*12:(j+1)*12])[-1][-1] for j in range(2)]};out.append(r);(O/'symmetric-roll-candidates.json').write_text(json.dumps(sorted(out,key=lambda x:x['score']),indent=2));print(roll_sign,i,r['score'],r['roll_error'],r['axis_miss_mm'],r['lens_world'],flush=True)
