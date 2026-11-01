from pathlib import Path
import json,sys,numpy as np
import FreeCAD as A,Part,Mesh
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
R=Path.cwd();S=R/'designs/eye-tracker/mouse/nasal-camera-r15';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
from refine import sampled_surface
cfg=json.loads((S/'solution.json').read_text());target=np.array(cfg['head']);p=np.array(cfg['parameters']);seed=p.copy();m=json.loads((S.parent/'landmark-eye-placement-r14/review.json').read_text());d=A.openDocument(str(R/m['native_checkpoint']));surf,norm=sampled_surface(d.RetainedPCBTray.Shape,np.random.default_rng(55));tree=cKDTree(surf);flat=np.array([[x,y,0.] for y in np.linspace(.5,8,100) for x in np.linspace(-2,2,9)]);lo=np.array([[3.75,-3.8,-1.1,0]]*3).ravel();hi=np.array([[7,-.01,1.1,3],[12,3.8,1.1,3],[12,3.8,1.1,3]]).ravel()
for i in range(4):
 vv,_=g.evaluate(p,flat);dist,idx=tree.query(vv);near=dist<.7;points=flat[near];qs=surf[idx[near]];ns=norm[idx[near]]
 def fun(x):
  pos,rr=g.endpoint(x);v,_=g.evaluate(x,points);gap=np.sum((v-qs)*ns,axis=1)
  return np.r_[(pos[0]-target[:3,3])*1000,Rotation.from_matrix(target[:3,:3].T@rr).as_rotvec()*2000,np.maximum(.25-gap,0)*20,max(g.zones(x)[-1][-1]-(g.L-.3),0)*100,(x-seed)*1e-5]
 res=least_squares(fun,np.clip(p,lo+1e-9,hi-1e-9),bounds=(lo,hi),max_nfev=400);p=res.x;print(i,'cost',np.linalg.norm(res.fun),'endpoint',np.linalg.norm(g.endpoint(p)[0][0]-target[:3,3]),flush=True)
cfg['parameters']=p.tolist();cfg['ribbon_refinement']='Sampled tray planes, 0.25 mm top-surface margin; fixed endpoint';(S/'solution.json').write_text(json.dumps(cfg,indent=2))

