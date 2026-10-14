"""Collision refinement using sampled CAD surfaces; exact Booleans remain the gate."""
from pathlib import Path
import json,numpy as np
import FreeCAD as A,Part
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
import ribbon_geometry as g

def sampled_surface(shape,rng):
 verts,faces=shape.tessellate(.025);tri=np.array([list(v) for v in verts])[np.array(faces)];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(cross,axis=1)/2;valid=areas>1e-10;tri=tri[valid];cross=cross[valid];areas=areas[valid];normals=cross/(2*areas[:,None]);count=max(3000,int(areas.sum()/.015));idx=rng.choice(len(tri),count,p=areas/areas.sum());uv=rng.random((count,2));u=np.sqrt(uv[:,0]);points=(1-u[:,None])*tri[idx,0]+(u*(1-uv[:,1]))[:,None]*tri[idx,1]+(u*uv[:,1])[:,None]*tri[idx,2]
 return points,normals[idx]

def refine(out,rounds=6):
 out=Path(out);target=np.array(json.loads((out/'target.json').read_text())['sensor_in_mount']);p=np.array(json.loads((out/'solve.json').read_text())['parameters']);seed=p.copy();rng=np.random.default_rng(51)
 names=['RetainedPCBTray','RetainedSocket','eye_primary_Holder','eye_primary_Clip','UpperSupport','RearRibbonGuard'];obstacles=[]
 for name in names:
  shape=Part.Shape();shape.read(str(out/(name+'.brep')));vv,nn=sampled_surface(shape,rng);obstacles.append((name,cKDTree(vv),vv,nn))
 flat=np.array([[x,y,0.] for y in np.linspace(.5,g.L-.5,150) for x in np.linspace(-2,2,9)])
 bounds=g.parameter_bounds(json.loads((out/'target.json').read_text())['ribbon_bounds'])
 for step in range(rounds):
  vv,_=g.evaluate(p,flat);points=[];qs=[];ns=[];margins=[];worst=100
  for name,tree,surface,normals in obstacles:
   dist,idx=tree.query(vv);near=dist<.8
   if not near.any():continue
   q=surface[idx[near]];n=normals[idx[near]];points.extend(flat[near]);qs.extend(q);ns.extend(n);margins.extend([.085 if name=='RetainedPCBTray' else .15]*len(q));worst=min(worst,float(np.min(np.sum((vv[near]-q)*n,axis=1))))
  print('collision round',step,'planes',len(points),'worst neutral distance',worst,flush=True);points=np.array(points);qs=np.array(qs);ns=np.array(ns);margins=np.array(margins)
  def residual(x):
   pos,R=g.endpoint(x);vv,_=g.evaluate(x,points);dist=np.sum((vv-qs)*ns,axis=1)
   return np.r_[(pos[0]-target[:3,3])*100,Rotation.from_matrix(target[:3,:3].T@R).as_rotvec()*800,max(g.zones(x)[-1][-1]-(g.L-.3),0)*100,np.maximum(margins-dist,0)*10,(x-seed)*1e-5]
  res=least_squares(residual,np.clip(p,np.array(bounds[0])+1e-10,np.array(bounds[1])-1e-10),bounds=bounds,max_nfev=500,ftol=1e-10,xtol=1e-10,gtol=1e-10);p=res.x;pos,R=g.endpoint(p);print('endpoint',np.linalg.norm(pos[0]-target[:3,3]),'cost',np.linalg.norm(res.fun),flush=True)
  (out/'solve.json').write_text(json.dumps({'parameters':p.tolist(),'endpoint_error_mm':float(np.linalg.norm(pos[0]-target[:3,3])),'frame_error':float(np.linalg.norm(R-target[:3,:3])),'collision_plane_cost':float(np.linalg.norm(res.fun)),'straight_entry_mm':g.L-g.zones(p)[-1][-1]},indent=2))
 return p
