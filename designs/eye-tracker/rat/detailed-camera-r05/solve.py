from pathlib import Path
import sys,json,numpy as np
import FreeCAD as A,Part
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
r=Path.cwd();out=r/'generated/eye-tracker/rat/detailed-camera-r05';sys.path.insert(0,str(r/'designs/eye-tracker/mouse/ribbon-fixed-r03'));import geometry as g
doc=A.openDocument(str(out/'ET-RAT-DETAILED-R05.FCStd'));arm=doc.FinishedCarrier.Shape.copy();T=A.Placement(A.Matrix(*sum(json.loads(doc.TargetRecipe.RecipeJSON)['mount_to_skull'],[])));arm.Placement=T.inverse().multiply(arm.Placement)
p0=np.array(json.loads((r/'designs/eye-tracker/rat/detailed-camera-r05/recipe.json').read_text())['ribbon_parameters']);goal,Rgoal=g.endpoint(p0)
flat=np.array([[x,y,0.] for y in np.linspace(0,g.L,200) for x in np.linspace(-2,2,9)])
vv,_=g.evaluate(p0,flat);near=[]
for i,v in enumerate(vv):
 if arm.distToShape(Part.Vertex(A.Vector(*v)))[0]<.8:near.append(i)
points=flat[near];print('near points',len(points),flush=True)
# Local planes taken from nearest arm surfaces guide the ribbon off the interference.
planes=[]
for v in vv[near]:
 dist,pairs,info=arm.distToShape(Part.Vertex(A.Vector(*v)));q=np.array(pairs[0][0]);direction=v-q
 if arm.isInside(A.Vector(*v),1e-7,True):direction=-direction
 direction/=np.linalg.norm(direction);planes.append((q,direction))
qs=np.array([x[0] for x in planes]);ns=np.array([x[1] for x in planes])
bounds=(np.array([[3.5,-3.8,-1.1,0],[3.5,-3.8,-1.1,0],[3.5,-3.8,-1.1,0]]).ravel(),np.array([[5.075,-.01,1.1,1],[12,3.8,1.1,3],[12,3.8,1.1,3]]).ravel())
def residual(p):
 pos,R=g.endpoint(p);vv,_=g.evaluate(p,points);d=np.sum((vv-qs)*ns,axis=1)
 return np.r_[(pos[0]-goal[0])*1000,Rotation.from_matrix(Rgoal.T@R).as_rotvec()*8000,max(g.zones(p)[-1][-1]-(g.L-.3),0)*100,np.maximum(.32-d,0)*10,(p-p0)*.0001]
res=least_squares(residual,np.clip(p0,bounds[0]+1e-9,bounds[1]-1e-9),bounds=bounds,max_nfev=700,xtol=1e-12,ftol=1e-12,gtol=1e-12);pos,R=g.endpoint(res.x)
report={'parameters':res.x.tolist(),'endpoint_error_mm':float(np.linalg.norm(pos-goal)),'frame_error':float(np.linalg.norm(R-Rgoal)),'inside_radii_mm':res.x[::4].tolist(),'straight_entry_mm':g.L-g.zones(res.x)[-1][-1]};print(report,flush=True);(out/'solve.json').write_text(json.dumps(report,indent=2));cfgpath=r/'designs/eye-tracker/rat/detailed-camera-r05/recipe.json';cfg=json.loads(cfgpath.read_text());cfg['original_ribbon_parameters']=cfg['ribbon_parameters'];cfg['ribbon_parameters']=report['parameters'];cfg['ribbon_surface_policy']='Three cylindrical zones re-solved at fixed endpoints for 0.25 mm ribbon clearance';cfgpath.write_text(json.dumps(cfg,indent=2))
