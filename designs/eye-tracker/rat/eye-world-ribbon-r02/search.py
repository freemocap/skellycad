from pathlib import Path
import sys,json,numpy as np
from scipy.optimize import least_squares
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-ribbon-r02';O=R/'generated/eye-tracker/rat/eye-world-ribbon-r02'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
c=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());B=np.array(c['mount_to_skull'])@np.array(c['sides']['Left']['board_transform']);ll=np.array([.08845911870242962,5.719524249669308,1.607691279838762]);flat=np.array([[x,y,0.] for y in np.linspace(0,g.L,100) for x in [-2.,0.,2.]])
def calc(p):
 pos,rot=g.endpoint(p);h=np.eye(4);h[:3,:3]=B[:3,:3]@rot;h[:3,3]=B[:3,:3]@pos[0]+B[:3,3];rib=g.evaluate(p,flat)[0]@B[:3,:3].T+B[:3,3];return h,h[:3,3]+h[:3,:3]@ll,rib
# Conservative carrier/board volume guides search only. Full solids gate acceptance.
def residual(p):
 h,l,rib=calc(p);q=p.reshape(3,4);cost=list((h[:3,2]-[1,0,0])*10000);cost+=[max(g.zones(p)[-1][-1]-32.6,0)*10000]
 boxlo=np.array([3.1,-20.7,3.]);boxhi=np.array([9.,20.7,20.4]);depth=np.min(np.minimum(rib-boxlo,boxhi-rib),axis=1);cost.extend(np.maximum(depth,0)*100)
 rel=rib-l;forward=rel[:,0];rad=np.linalg.norm(rel[:,1:],axis=1);cost.extend(np.maximum(np.minimum(np.minimum(forward-2.1,30-forward),2.4+forward*.5-rad),0)*100)
 # Free camera translation and roll: only broad placement bounds, no fixed pose.
 cost.extend(np.maximum([10-l[0],l[0]-19,8-l[2],l[2]-20,abs(l[1])-16],0)*30)
 cost.extend(q[:,2]*2);cost.extend(q[1:,1]*.4);cost.extend([l[1]*.015,(l[0]-12)*.02]);return cost
lo=np.tile([3.75,-3.8,-.85,0],3);hi=np.tile([12,3.8,.85,10],3);out=[]
for r,gap in [(4,6),(4.5,5),(5,4),(3.8,7)]:
 seed=np.array([r,-np.pi,0,gap,4,.04,0,.1,4,.01,0,.1])
 fit=least_squares(residual,seed,bounds=(lo,hi),max_nfev=500,ftol=1e-9,xtol=1e-10,gtol=1e-9)
 h,l,rib=calc(fit.x);rec={'parameters':fit.x.tolist(),'head_world':h.tolist(),'lens_world_mm':l.tolist(),'axis_error':float(np.linalg.norm(h[:3,2]-[1,0,0])),'zone_end_mm':g.zones(fit.x)[-1][-1],'score':float(np.linalg.norm(fit.fun)),'ribbon_length_mm':g.L,'width_mm':4,'thickness_mm':.25,'minimum_inside_radius_mm':float(min(fit.x[::4])-.25),'method':'Camera pose derived exclusively from cylindrical ribbon endpoint; free roll and translation; forward aim constraint'};out.append(rec);(O/'candidates.json').write_text(json.dumps(sorted(out,key=lambda r:r['score']),indent=2));print(rec,flush=True)
