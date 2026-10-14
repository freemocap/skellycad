from pathlib import Path
import json,hashlib,numpy as np,trimesh
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
ROOT=Path.cwd();ST=ROOT/'designs/eye-tracker/mouse/registered-eyes-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/registered-eyes-study-r01'
a=np.load(OUT/'labels.npy');mask=a[:,:260,:]==2
mask[:120,:,:]=False;mask[270:,:,:]=False
v,f,_,_=marching_cubes(np.pad(mask,1).astype(np.uint8),.5,spacing=(.1,.1,.1));v-=.1
atlas=trimesh.Trimesh(v,f).simplify_quadric_decimation(face_count=30000);atlas.export(OUT/'digimouse-head-source.stl')
previous=json.loads((ROOT/'designs/eye-tracker/mouse/skull-landmarks-study-r01/validation.json').read_text());path=ROOT/previous['existing_skull_path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==previous['existing_skull_sha256']
active=json.loads((ROOT/'designs/eye-tracker/mouse/active-model.json').read_text());assert hashlib.sha256((ROOT/active['native_checkpoint']).read_bytes()).hexdigest()==active['native_sha256']
target=trimesh.load(path)
R=np.array([[0,-1,0],[0,0,1],[-1,0,0.]])
np.random.seed(182);points,_=trimesh.sample.sample_surface(atlas,16000);q,_=trimesh.sample.sample_surface(target,25000);tree=cKDTree(q)
T=np.eye(4);T[:3,:3]=R;T[:3,3]=target.bounds.mean(0)-R@atlas.bounds.mean(0)
for i in range(100):
 p=trimesh.transform_points(points,T);dist,ids=tree.query(p);keep=dist<np.quantile(dist,.8)
 dt,_,_=trimesh.registration.procrustes(p[keep],q[ids[keep]],reflection=False,scale=True);T=dt@T
registered=atlas.copy();registered.apply_transform(T);registered.export(OUT/'digimouse-head-registered.stl')
rows=[]
for file in [OUT/'eye-1.stl',OUT/'eye-2.stl']:
 m=trimesh.load(file);m.fix_normals();source=m.center_mass.copy();vol=m.volume;m.apply_transform(T);m.export(OUT/(file.stem+'-registered.stl'))
 rows.append({'id':file.stem,'source_centroid_index_mm':source.tolist(),'transferred_centroid_mm':trimesh.transform_points(source[None,:],T)[0].tolist(),'source_volume_mm3':float(vol),'source_extents_mm':trimesh.load(file).extents.tolist()})
np.random.seed(817);p,_=trimesh.sample.sample_surface(registered,1800);_,dist,_=trimesh.proximity.closest_point(target,p)
report={'units':'mm','source_active_sha256':active['native_sha256'],'existing_skull_sha256':previous['existing_skull_sha256'],'matrix_source_index_mm_to_assembly':T.tolist(),'scale':float(np.cbrt(np.linalg.det(T[:3,:3]))),'crop':'voxel axis 1 <260 and 120<=axis0<270; removes forelimbs, includes mandible/upper neck','method':'80 percent trimmed point ICP, proper similarity, 100 iterations','surface_median_mm':float(np.median(dist)),'surface_p95_mm':float(np.percentile(dist,95)),'eyes':rows,'landmark_target_error_mm':None}
(ST/'registration.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(14,6))
for ax,(i,j),title in zip(axes,[(0,2),(0,1)],['Dorsal comparison','Lateral comparison']):
 ax.scatter(target.vertices[::5,i],target.vertices[::5,j],s=.35,c='gray',alpha=.3,label='Existing skull')
 ax.scatter(registered.vertices[::2,i],registered.vertices[::2,j],s=.35,c='#149aab',alpha=.4,label='Transferred Digimouse head')
 for row in rows:
  m=trimesh.load(OUT/(row['id']+'-registered.stl'));ax.scatter(m.vertices[:,i],m.vertices[:,j],s=1,c='#d47b09',alpha=.6)
 ax.set_aspect('equal');ax.set_title(title);ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly '+('Z' if j==2 else 'Y')+' (mm)')
axes[0].legend();fig.suptitle('Stage 1: matched atlas eye labels transferred with skull; exploratory alignment');fig.tight_layout();fig.savefig(OUT/'registration-comparison.png',dpi=150)
