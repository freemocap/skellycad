from pathlib import Path
import sys,json,hashlib,numpy as np,trimesh
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
ROOT=Path.cwd(); STUDY=ROOT/'designs/eye-tracker/mouse/skull-landmarks-study-r01'; OUT=ROOT/'generated/eye-tracker/mouse/skull-landmarks-study-r01'; SRC=STUDY/'sources'
sys.path.insert(0,str(OUT/'python-deps'));import nibabel as nib
active=json.loads((ROOT/'designs/eye-tracker/mouse/active-model.json').read_text());assert hashlib.sha256((ROOT/active['native_checkpoint']).read_bytes()).hexdigest()==active['native_sha256']
anatomy=json.loads((ROOT/'designs/eye-tracker/mouse/anatomy.json').read_text());assert hashlib.sha256((ROOT/anatomy['mesh_checkpoint']['path']).read_bytes()).hexdigest()==anatomy['mesh_checkpoint']['sha256']
manifest=json.loads((STUDY/'sources.json').read_text());
for item in manifest['files']:assert hashlib.sha256((SRC/item['file']).read_bytes()).hexdigest()==item['sha256']
im=nib.load(SRC/'35_mic_23strain_mus_template_UCHAR-label.nii.gz');mask=np.asanyarray(im.dataobj)==1
v,f,_,_=marching_cubes(np.pad(mask,1).astype(np.uint8),.5);v=nib.affines.apply_affine(im.affine,v-1)*[-1,-1,1]
a=trimesh.Trimesh(v,f,process=True);full_count=len(a.faces);a=a.simplify_quadric_decimation(face_count=30000);a.export(OUT/'atlas-skull-lps.stl')
lo=trimesh.load(ROOT/'designs/eye-tracker/mouse/references/skull/Skull.stl');source_path=ROOT/'designs/eye-tracker/mouse/references/skull/Skull.stl'
# Explicit visual starting orientation: atlas anterior -Y/dorsal +Z -> assembly anterior +X/dorsal +Y.
R=np.array([[0,-1,0],[0,0,1],[-1,0,0]],float);T=np.eye(4);T[:3,:3]=R;T[:3,3]=lo.bounds.mean(axis=0)-R@a.bounds.mean(axis=0)
np.random.seed(2718);points,_=trimesh.sample.sample_surface(a,12000);target,_=trimesh.sample.sample_surface(lo,24000);tree=cKDTree(target)
for iteration in range(60):
 p=trimesh.transform_points(points,T);dist,ids=tree.query(p);keep=dist<np.quantile(dist,.85)
 delta,_,_=trimesh.registration.procrustes(p[keep],target[ids[keep]],reflection=False,translation=True,scale=True)
 candidate=delta@T;s=np.cbrt(np.linalg.det(candidate[:3,:3]));assert .8<s<1.25
 T=candidate
registered=a.copy();registered.apply_transform(T);registered.export(OUT/'atlas-skull-registered.stl')
landmarks=json.loads((SRC/'45_LM-skull.mrk.json').read_text())['markups'][0]['controlPoints'];p=np.array([x['position'] for x in landmarks]);tp=trimesh.transform_points(p,T)
# Source numerical IDs retained. Anatomical names below are explicitly tentative visual interpretations, not decoded author labels.
names={'1':'Nasale candidate','13':'Bregma candidate','16':'Lambda candidate','19':'Posterior interparietal midline candidate','21':'Opisthion candidate','51':'Nasion candidate'}
near,distance,face=trimesh.proximity.closest_point(lo,tp)
rows=[]
for i,x in enumerate(landmarks):rows.append({'id':'MAGA_LM_'+x['label'],'source_label':x['label'],'name':names.get(x['label'],'Atlas landmark '+x['label']),'name_status':'tentative anatomical interpretation' if x['label'] in names else 'source numeric ID; anatomical name unresolved','atlas_lps_mm':p[i].tolist(),'transferred_assembly_mm':tp[i].tolist(),'nearest_surface_mm':near[i].tolist(),'surface_distance_mm':float(distance[i]),'status':'similarity-transferred estimate; not independently landmark-validated'})
landmark_doc={'units':'mm','source_frame':'atlas LPS','target_frame':'Recovered R10 assembly XYZ','transformation':'proper similarity; 85% trimmed nearest-point ICP; no reflection or nonrigid deformation','landmarks':rows};(STUDY/'landmarks.json').write_text(json.dumps(landmark_doc,indent=2))
# independent samples and nearest triangles, both directions (surface disagreement, not target registration error)
np.random.seed(314159);sp,_=trimesh.sample.sample_surface(registered,2500);tp2,_=trimesh.sample.sample_surface(lo,2500)
report={'source_active_checkpoint':active['revision'],'source_active_sha256':active['native_sha256'],'source_anatomy_sha256':anatomy['mesh_checkpoint']['sha256'],'existing_skull_path':str(source_path.relative_to(ROOT)),'existing_skull_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'atlas_faces_before_decimation':full_count,'atlas_faces':len(a.faces),'existing_faces':len(lo.faces),'atlas_watertight':bool(a.is_watertight),'matrix_atlas_lps_to_assembly':T.tolist(),'uniform_scale':float(np.cbrt(np.linalg.det(T[:3,:3]))),'registration_landmark_target_error_mm':None,'landmark_target_error_reason':'No independently measured target landmarks exist. Surface residual is not landmark error.','coordinate_roundtrip_max_mm':float(np.max(np.abs(trimesh.transform_points(trimesh.transform_points(p,T),np.linalg.inv(T))-p)))}
for key,mesh,pts in [('atlas_to_existing',lo,sp),('existing_to_atlas',registered,tp2)]:
 _,d,_=trimesh.proximity.closest_point(mesh,pts);report[key+'_surface_mm']={'median':float(np.median(d)),'p95':float(np.percentile(d,95)),'max':float(np.max(d)),'samples':len(d)}
(STUDY/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(13,6))
for ax,(i,j),title in zip(axes,[(0,2),(0,1)],['Dorsal projection','Lateral projection']):
 ax.scatter(lo.vertices[::4,i],lo.vertices[::4,j],s=.4,c='#777777',alpha=.4,label='Existing skull')
 ax.scatter(registered.vertices[:,i],registered.vertices[:,j],s=.3,c='#16a5ad',alpha=.3,label='Registered atlas')
 for row,point in zip(rows,tp):
  if row['source_label'] in names:ax.scatter(point[i],point[j],s=22,c='#cc3366');ax.annotate(row['name'],(point[i],point[j]),xytext=(4,8),textcoords='offset points',fontsize=8)
 ax.set_aspect('equal');ax.set_title(title);ax.set_xlabel('Assembly X (mm)');ax.set_ylabel(('Z' if j==2 else 'Y')+' (mm)')
axes[0].legend(loc='lower left');fig.suptitle('Exploratory similarity registration — candidate anatomical names, not verified sutures');fig.tight_layout();fig.savefig(STUDY/'registration-review.png',dpi=160)
