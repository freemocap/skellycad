"""Screen planar rear-arm routes against the frozen camera and ribbon."""
import json, sys, itertools
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
R=Path.cwd(); S=Path(__file__).parent; O=R/'generated/eye-tracker/rat/orthogonal-arms-r42'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
import ribbon_geometry as g
cfg=json.loads((S/'recipe.json').read_text())
old=json.loads((R/'generated/eye-tracker/rat/clear-view-r41/04-arms.json').read_text())
pars=json.loads((S.parent/'clear-view-r41/selected-pose.json').read_text())['parameters']
flat=np.array([[x,y,0] for y in np.linspace(0,g.L,300) for x in np.linspace(-2,2,9)])
out={}
for side,offset in [('Right',0),('Left',12)]:
 H=np.array(cfg['sides'][side]['head']); B=np.array(cfg['sides'][side]['board_transform'])
 ribbon=g.evaluate(pars[offset:offset+12],flat)[0]@B[:3,:3].T+B[:3,3]
 axis=H[:3,2]; up=np.cross([1,0,0],axis); up/=np.linalg.norm(up); up=up if up[1]>0 else -up
 rad=np.cross(axis,up); rad=rad if rad[0]*(1 if side=='Left' else -1)>0 else -rad
 tip=(H@np.array([3.094423077,6.76759978,-9.3,1]))[:3]+2*rad
 roots=[]
 for y,z in itertools.product([8.2],[17.8,18.2]):
  root=np.array(old[side+'LowerSupport']['poles_mm'][0]); root[1]=y;root[2]=z*(1 if side=='Right' else -1);roots.append(root)
 candidates=[]
 for root in roots:
  n=np.cross(tip-root,rad);n/=np.linalg.norm(n)
  for f,h,r in itertools.product([.15,.3,.5,.7],[4,8,12,16,22,28,34],[6,10,15,20,26,32]):
   p=np.array([root,root+(tip-root)*f+rad*h,tip+rad*r,tip]);u=np.linspace(0,1,101)[:,None]
   c=(1-u)**3*p[0]+3*(1-u)**2*u*p[1]+3*(1-u)*u*u*p[2]+u**3*p[3]
   v=3*(1-u)**2*(p[1]-p[0])+6*(1-u)*u*(p[2]-p[1])+3*u*u*(p[3]-p[2]); a=6*(1-u)*(p[2]-2*p[1]+p[0])+6*u*(p[3]-2*p[2]+p[1])
   if np.max(np.linalg.norm(np.cross(v,a),axis=1)/np.linalg.norm(v,axis=1)**3)>.4:continue
   t=v/np.linalg.norm(v,axis=1)[:,None];w=np.cross(n,t);width=2.6+.4*np.exp(-(u/.18)**2)+.4*np.exp(-((1-u)/.18)**2);thick=2.-.4*np.exp(-(u/.12)**2)+.1*np.exp(-((1-u)/.18)**2)
   probes=np.concatenate([c+w*width*i/2+n*thick*j/2 for i,j in itertools.product([-1,0,1],repeat=2)])
   hp=(probes-H[:3,3])@H[:3,:3]
   if np.any(np.all((hp>[-7.5,-1.5,-6.8])&(hp<[7.5,17.5,8]),axis=1)):continue
   _,idx=cKDTree(c).query(ribbon);d=ribbon-c[idx];dn=np.abs(d@n);dw=np.abs(np.sum(d*w[idx],axis=1));dt=np.abs(np.sum(d*t[idx],axis=1))
   if np.any((dn<thick[idx,0]/2+.2)&(dw<width[idx,0]/2+.2)&(dt<.6)):continue
   candidates.append({'poles':p.tolist(),'normal':n.tolist(),'direction':rad.tolist(),'length':float(np.linalg.norm(np.diff(c,axis=0),axis=1).sum())})
 out[side]=sorted(candidates,key=lambda x:x['length']);print(side,len(candidates),out[side][0] if candidates else '',flush=True)
(O/'rear-candidates.json').write_text(json.dumps(out,indent=2))
