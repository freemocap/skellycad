from pathlib import Path
import numpy as np,trimesh,json
HERE=Path(__file__).resolve().parent
def design(v):
 x,y,z=v.T
 return np.column_stack([x*x,y*y,z*z,2*x*y,2*x*z,2*y*z,2*x,2*y,2*z,np.ones(len(v))])
def residual(v,q):
 A=np.array([[q[0],q[3],q[4]],[q[3],q[1],q[5]],[q[4],q[5],q[2]]])
 return abs(design(v)@q)/np.maximum(np.linalg.norm(2*(v@A+q[6:9]),axis=1),1e-12)
def fit(v):
 D=design(v);rng=np.random.default_rng(42);best=None;count=0
 for _ in range(3000):
  _,_,vh=np.linalg.svd(D[rng.choice(len(v),9,replace=False)],full_matrices=True);q=vh[-1];inlier=residual(v,q)<2e-5
  if inlier.sum()>count:count=inlier.sum();best=q
 for _ in range(3):
  inlier=residual(v,best)<2e-5;_,_,vh=np.linalg.svd(D[inlier],full_matrices=False);best=vh[-1]
 return best,residual(v,best)<2e-5
results={}
for name in ['Eye1','Eye2']:
 m=trimesh.load_mesh(HERE/'inputs'/(name+'.stl'));center=m.vertices.mean(axis=0);v=m.vertices-center
 q,mask=fit(v);q2,mask2=fit(v[~mask]);r1=residual(v,q);r2=residual(v,q2)
 labels=np.argmin(np.column_stack([r1,r2]),axis=1)
 print(name,'body',mask.sum(),'remaining',(~mask).sum(),'second',mask2.sum(),'residual max',np.minimum(r1,r2).max())
 for p in [q,q2]:
  A=np.array([[p[0],p[3],p[4]],[p[3],p[1],p[5]],[p[4],p[5],p[2]]]);c=-np.linalg.solve(A,p[6:9]);k=c@A@c-p[9];w,U=np.linalg.eigh(A/k)
  print('center',c+center,'radii',1/np.sqrt(w),'axes',U)
 tri=m.faces;body=(r1[tri]<2e-5).all(axis=1);cornea=(r2[tri]<2e-5).all(axis=1)
 print('faces body/cornea/neither/both',body.sum(),cornea.sum(),(~(body|cornea)).sum(),(body&cornea).sum())
 results[name]=dict(center=center.tolist(),body_quadric=q.tolist(),cornea_quadric=q2.tolist(),body_vertices=int(mask.sum()),cornea_vertices=int(mask2.sum()),max_residual_mm=float(np.minimum(r1,r2).max()),body_faces=np.flatnonzero(body).tolist(),cornea_faces=np.flatnonzero(cornea).tolist(),unassigned_faces=np.flatnonzero(~(body|cornea)).tolist())
(HERE/'cornea-fit.json').write_text(json.dumps(results,indent=2))
