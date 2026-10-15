from pathlib import Path
import json,hashlib,numpy as np,trimesh
from scipy.spatial import cKDTree
R=Path.cwd();S=R/'designs/eye-tracker/rat/skull-registration-r12';O=R/'generated/eye-tracker/rat/skull-registration-r12';O.mkdir(parents=True,exist_ok=True)
for p in [S.parent/'active-model.json',S.parent/'clean-reference-r11/review.json']:
 a=json.loads(p.read_text());assert hashlib.sha256((R/a['native_checkpoint']).read_bytes()).hexdigest()==a['native_sha256']
P=S.parent/'references/skull/aligned-r01';source=P/'rat-skull-high-res-refined-aligned-r01.stl';m=trimesh.load_mesh(source);atlas=trimesh.load_mesh(R/'generated/eye-tracker/rat/clean-reference-r11/ratlas-clean-reference.stl')
def roof(m):
 v=m.vertices;bins=np.floor(v[:,:2]/.5).astype(int);order=np.argsort(v[:,2])[::-1];_,idx=np.unique(bins[order],axis=0,return_index=True);p=v[order[idx]];return p[p[:,2]>p[:,2].max()-8]
p=roof(m);q=roof(atlas);tree=cKDTree(q);print('roof ranges',p.min(0),p.max(0),q.min(0),q.max(0),flush=True)
def solve(t):
 T=np.eye(4);T[:3,3]=t
 for _ in range(100):
  x=p@T[:3,:3].T+T[:3,3];dist,ix=tree.query(x);keep=dist<np.quantile(dist,.85);a=x[keep];b=q[ix[keep]];ac=a.mean(0);bc=b.mean(0);u,_,vt=np.linalg.svd((a-ac).T@(b-bc));rot=vt.T@u.T
  if np.linalg.det(rot)<0:vt[-1]*=-1;rot=vt.T@u.T
  D=np.eye(4);D[:3,:3]=rot;D[:3,3]=bc-rot@ac;T=D@T
  if np.linalg.norm(D-np.eye(4))<1e-6:break
 x=p@T[:3,:3].T+T[:3,3];d=tree.query(x)[0];return float(np.mean(np.sort(d)[:int(.85*len(d))]**2)),T,d
runs=[solve([x,0,z]) for x in [0,3,6] for z in [-4,-6,-8]];runs.sort(key=lambda r:r[0]);score,T,d=runs[0];print('best',score,T,np.percentile(d,[50,90,95]),flush=True)
report={'units':'mm','source':source.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Rigid trimmed ICP on dorsal height envelopes, 0.5 mm XY bins, top 8 mm, 85 percent correspondences retained; nine translation seeds','scale':1.,'source_to_atlas':T.tolist(),'rotation_determinant':float(np.linalg.det(T[:3,:3])),'roof_nearest_vertex_mm':dict(zip(['median','p90','p95'],map(float,np.percentile(d,[50,90,95])))),'status':'Proposed geometric registration; awaiting user visual review; roof fit does not independently validate orbital anatomy','files':{}}
for f in P.glob('rat-skull-*-aligned-r01.stl'):
 mm=trimesh.load_mesh(f);mm.apply_transform(T);dest=O/f.name.replace('-aligned-r01','-atlas-frame-r12');mm.export(dest);report['files'][dest.name]={'source':f.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
mm=m.copy();mm.apply_transform(T);rows=json.loads((S.parent/'clean-reference-r11/landmarks.json').read_text());points=np.array([r['position_mm'] for r in rows]);near,dist,tri=trimesh.proximity.closest_point(mm,points)
for row,pp,dd in zip(rows,near,dist):row['existing_mesh_nearest_surface_mm']=pp.tolist();row['surface_gap_mm']=float(dd)
(S/'landmarks.json').write_text(json.dumps(rows,indent=2));(S/'registration.json').write_text(json.dumps(report,indent=2));print('landmark gaps',[(r['id'],r['surface_gap_mm']) for r in rows])
