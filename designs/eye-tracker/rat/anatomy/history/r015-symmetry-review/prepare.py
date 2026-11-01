from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.optimize import least_squares
R=Path.cwd(); S=R/'designs/eye-tracker/rat/symmetry-review-r15'; O=R/'generated/eye-tracker/rat/symmetry-review-r15'; O.mkdir(parents=True,exist_ok=True)
for file in [S.parent/'active-model.json',S.parent/'registered-eyes-r14/review.json']:
 a=json.loads(file.read_text());assert hashlib.sha256((R/a['native_checkpoint']).read_bytes()).hexdigest()==a['native_sha256']
source=R/'generated/eye-tracker/rat/skull-registration-r12/rat-skull-high-res-refined-atlas-frame-r12.stl'
m=trimesh.load_mesh(source);v=m.vertices
np.random.seed(15);samples,_=trimesh.sample.sample_surface(m,40000)
tree=cKDTree(np.vstack([v,samples]))
def plane(p):
 n=np.array([p[0],1.,p[1]]);n/=np.linalg.norm(n);return n,p[2]
def distances(p,q):
 n,d=plane(p);mir=q-2*(q@n-d)[:,None]*n
 return tree.query(mir)[0]
def solve(q):
 fit=least_squares(lambda p:distances(p,q),[0,0,0],bounds=([-.15,-.15,-2],[.15,.15,2]),loss='soft_l1',f_scale=.4,max_nfev=100,diff_step=1e-3)
 n,d=plane(fit.x)
 return {'parameters':fit.x.tolist(),'normal':n.tolist(),'offset_mm':float(d),'tilt_from_Y_deg':float(np.rad2deg(np.arccos(n[1]))),'success':bool(fit.success),'before_mm':np.percentile(distances([0,0,0],q),[50,90,95]).tolist(),'after_mm':np.percentile(distances(fit.x,q),[50,90,95]).tolist()}
fits={'whole':solve(samples[::3]),'dorsal':solve(samples[(samples[:,2]>-6)&(samples[:,0]<25)][::2])}
n,d=plane(fits['whole']['parameters']);mir=m.copy();mir.vertices=v-2*(v@n-d)[:,None]*n;mir.faces=mir.faces[:,::-1];mir.export(O/'mirror-about-fitted-plane.stl')
rows=[];pairs=[]
def add(id,name,p,offset,color):
 rows.append({'id':id,'name':name,'position_mm':p.tolist(),'label_offset_mm':offset,'color':color,'evidence':'Local geometric surface reference, not an author-labeled anatomical landmark'})
# Rostral nasal-tip candidates: anterior extremes of left and right halves in dorsal rostrum.
for sign,side in [(1,'Left'),(-1,'Right')]:
 q=v[(v[:,0]>25)&(v[:,2]>-9)&(v[:,1]*sign>0)&(abs(v[:,1])<3)];p=q[np.argmax(q[:,0])]
 add(side+'NasalTip',side+' nasal tip - surface extreme',p,[5,sign*5,3],(1,.45,.05))
pairs.append(['LeftNasalTip','RightNasalTip'])
for name,x,y,z in [('NasalRoof',22,2,None),('PosteriorRoof',-8,5,None),('FrontArch',12,None,-10),('RearArch',-3,None,-10)]:
 for sign,side in [(1,'Left'),(-1,'Right')]:
  start=[x,sign*y,10] if y is not None else [x,sign*30,z]
  direction=[0,0,-1] if y is not None else [0,-sign,0]
  hits,_,_=m.ray.intersects_location([start],[direction]);assert len(hits),(name,side)
  p=hits[np.argmin(np.linalg.norm(hits-np.array(start),axis=1))]
  label={'NasalRoof':'nasal roof','PosteriorRoof':'rear skull roof','FrontArch':'front arch section','RearArch':'rear arch section'}[name]
  add(side+name,side+' '+label,p,[0,sign*9,4],(.2,.65,.2) if y is not None else (.6,.25,.9))
 pairs.append(['Left'+name,'Right'+name])
pair_results=[]
for left,right in pairs:
 a=np.array(next(r['position_mm'] for r in rows if r['id']==left));b=np.array(next(r['position_mm'] for r in rows if r['id']==right));mid=(a+b)/2
 pair_results.append({'ids':[left,right],'midpoint_mm':mid.tolist(),'midpoint_offset_from_current_plane_mm':float(mid[1]),'reflected_pair_distance_current_mm':float(np.linalg.norm(a*np.array([1,-1,1])-b))})
report={'units':'mm','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Area-sampled reflected-point nearest-neighbor fit; robust soft-L1 plane optimization; sampled distances, not homologous-landmark residuals','percentile_order':[50,90,95],'fits':fits,'pairs':pair_results,'landmarks':rows,'geometry_changed':False}
(S/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({'fits':fits,'pairs':pair_results},indent=2))
