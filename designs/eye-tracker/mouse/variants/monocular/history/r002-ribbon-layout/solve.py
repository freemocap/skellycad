import FreeCAD as A,Part,json,sys
from pathlib import Path
root=Path.cwd();sys.path.insert(0,str(root/'designs/eye-tracker/mouse/ribbon-layout-r02'))
import geometry as g
import numpy as np
from scipy.optimize import least_squares
out=root/'generated/eye-tracker/mouse/ribbon-layout-r02';out.mkdir(parents=True,exist_ok=True)
d=A.openDocument(str(root/'generated/eye-tracker/mouse/camera-fit-r01/mouse-camera-fit-r01.FCStd'))
h=d.getObject('MeasuredSensorHead');lens=next(o for o in h.Group if 'M4-lens'==getattr(o,'SourceName',''))
b=lens.Shape.BoundBox;lenslocal=np.array([(b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,b.ZMax]);target=np.array(json.loads((root/'designs/eye-tracker/mouse/anatomy.json').read_text())['eye_target_mm'])
bounds=([3.575,-3.8,-.65,5.075,.15,-1.0,0],[5.075,-1.0,.65,16,2.7,1.,4.])
def residual(p):
 pos,R=g.endpoint(p);end=g.zones(p)[-1][-1];lens=pos[0]+R@lenslocal;direction=(target-lens);dist=np.linalg.norm(direction);direction/=dist
 return np.r_[(R[:,2]-direction)*20,max(end-(g.L-1),0)*20,(pos[0,2]-6.5)*.13,(dist-14)*.12,(p[0]-5.075)*.1,max(5-pos[0,1],0)*.05]
results=[];rng=np.random.default_rng(11)
for i in range(35):
 x=rng.uniform(*np.array(bounds));res=least_squares(residual,x,bounds=bounds,max_nfev=250)
 pos,R=g.endpoint(res.x);end=g.zones(res.x)[-1][-1];ll=pos[0]+R@lenslocal;aim=np.degrees(np.arccos(np.clip(np.dot(R[:,2],(target-ll)/np.linalg.norm(target-ll)),-1,1)))
 if end<=g.L-.95 and aim<2:results.append({'parameters':res.x.tolist(),'aim_error_deg':aim,'sensor_origin_mm':pos[0].tolist(),'straight_entry_mm':g.L-end,'score':float(np.linalg.norm(res.fun))})
results.sort(key=lambda x:x['score']);(out/'candidates.json').write_text(json.dumps(results,indent=2));(out/'lens-local.json').write_text(json.dumps(lenslocal.tolist()));print('candidates',len(results));print(json.dumps(results[:3],indent=2))
