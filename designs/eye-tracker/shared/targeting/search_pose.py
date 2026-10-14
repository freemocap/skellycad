"""Search camera rest pose through ribbon variables while preserving exact eye aim."""
from pathlib import Path
import json,numpy as np
import FreeCAD as A,Part
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from refine import sampled_surface
from prepare import checkpoint
import ribbon_geometry as g

def search(recipe_path,out):
 cfg=json.loads(Path(recipe_path).read_text());out=Path(out);source,_=checkpoint(cfg['hardware_manifest']);d=A.openDocument(str(source));T=np.array(cfg['mount_to_skull']);old=np.array(cfg['sensor_reference_in_mount']);target=T[:3,:3].T@(np.array(cfg['target_center_world_mm'])-T[:3,3]);lenslocal=np.array(cfg['lens_local_mm']);seed=np.array(cfg['ribbon_seed']);lensstart=T[:3,:3].T@(np.array(cfg['lens_position_world_mm'])-T[:3,3]);rng=np.random.default_rng(38)
 obstacles=[]
 for name,moving in [('RetainedPCBTray',False),('RetainedSocket',True),('eye_primary_Holder',True),('eye_primary_Clip',True)]:
  s=d.getObject(name).Shape;v,n=sampled_surface(s,rng);obstacles.append((name,moving,cKDTree(v),v,n))
 flat=np.array([[x,y,0.] for y in np.linspace(.45,g.L-.45,110) for x in np.linspace(-2,2,7)])
 lo,hi=g.parameter_bounds(cfg['ribbon_bounds'])
 def residual(p):
  pos,R=g.endpoint(p);origin=pos[0];lens=origin+R@lenslocal;delta=target-lens;dist=np.linalg.norm(delta);direction=delta/dist;DR=R@old[:3,:3].T;Dt=origin-DR@old[:3,3];vv,_=g.evaluate(p,flat);cost=[]
  for name,moving,tree,v,n in obstacles:
   query=(vv-Dt)@DR if moving else vv;ds,idx=tree.query(query);signed=np.sum((query-v[idx])*n[idx],axis=1);cost.extend(np.where(ds<1.3,np.maximum(.20-signed,0),0)*12)
  return np.r_[(R[:,2]-direction)*500,max(g.zones(p)[-1][-1]-(g.L-.4),0)*100,max(11-dist,0)*20,max(dist-22,0)*20,cost,(lens-lensstart)*.02,Rotation.from_matrix(old[:3,:3].T@R).as_rotvec()*.02,(p-seed)*.00001]
 best=None
 for trial in range(8):
  start=seed if trial==0 else seed+rng.normal(0,.25,12);res=least_squares(residual,np.clip(start,lo+1e-9,hi-1e-9),bounds=(lo,hi),max_nfev=260,ftol=1e-8,xtol=1e-8,gtol=1e-8);pos,R=g.endpoint(res.x);lens=pos[0]+R@lenslocal;axis=np.linalg.norm(np.cross(target-lens,R[:,2]));score=np.linalg.norm(res.fun);print('pose trial',trial,'score',score,'axis miss',axis,'lens shift',np.linalg.norm(lens-lensstart),flush=True)
  record={'parameters':res.x.tolist(),'score':float(score),'axis_miss_mm':float(axis),'sensor_origin_mount':pos[0].tolist(),'sensor_rotation_mount':R.tolist(),'lens_world_mm':(T[:3,:3]@lens+T[:3,3]).tolist()}
  if best is None or score<best['score']:best=record;(out/'pose-search.json').write_text(json.dumps(best,indent=2))
  if score<.3 and axis<.001:break
 return best
