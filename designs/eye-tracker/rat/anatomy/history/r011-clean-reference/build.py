from pathlib import Path
import sys,json,hashlib,numpy as np,trimesh
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
R=Path.cwd();S=R/'designs/eye-tracker/rat/clean-reference-r11';P=S.parent/'anatomy-study-r10';O=R/'generated/eye-tracker/rat/clean-reference-r11';O.mkdir(parents=True,exist_ok=True)
for path in [S.parent/'active-model.json',P/'review.json']:
 a=json.loads(path.read_text());assert hashlib.sha256((R/a['native_checkpoint']).read_bytes()).hexdigest()==a['native_sha256']
for row in json.loads((P/'sources.json').read_text())['files']:assert hashlib.sha256((P/'sources'/row['file']).read_bytes()).hexdigest()==row['sha256']
sys.path.insert(0,str(R/'generated/eye-tracker/mouse/skull-landmarks-study-r01/python-deps'));import nibabel as n
a=n.load(P/'sources/Ratlas-LH.nii.gz');b=n.load(P/'sources/Ratlas-LH_Brain.nii.gz');v=np.maximum(np.asarray(a.dataobj,dtype=np.float32)-np.asarray(b.dataobj,dtype=np.float32),0);v=ndi.gaussian_filter(v,.6);threshold=json.loads((P/'extraction.json').read_text())['threshold'];labels,nc=ndi.label(v>threshold);counts=np.bincount(labels.ravel());counts[0]=0;keep=np.isin(labels,np.flatnonzero(counts>1000));v[~ndi.binary_dilation(keep,iterations=2)]=0
verts,faces,_,_=marching_cubes(np.pad(v,1),threshold,step_size=2,allow_degenerate=False);verts=n.affines.apply_affine(a.affine,verts-1);T=np.array(json.loads((P/'extraction.json').read_text())['RAS_to_CAD']);verts=n.affines.apply_affine(T,verts);m=trimesh.Trimesh(verts,faces);m.fix_normals(multibody=True);m.export(O/'ratlas-clean-reference.stl');edges=m.edges_unique_length;assert edges.max()<.27
rows=json.loads((P/'landmarks.json').read_text());
for row in rows:row['user_review']='Visually accepted 2026-10-14; original coordinate and evidence status retained'
(S/'landmarks.json').write_text(json.dumps(rows,indent=2))
report={'method':'Gaussian smooth source intensity sigma 0.6 voxel; continuous-intensity marching cubes step 2; no mesh decimation or mesh smoothing','sigma_source_mm':.045,'display_sampling_mm':.15,'max_edge_mm':float(edges.max()),'faces':len(m.faces),'watertight':bool(m.is_watertight),'landmark_coordinates_unchanged':True,'status':'Anatomical display reference, not print export','old_display_max_edge_mm':7.442293304,'old_display_edges_above_2mm':4480,'unsmoothed_decimated_max_edge_mm':2.67756361,'new_edges_above_2mm':int((edges>2).sum()),'sha256':hashlib.sha256((O/'ratlas-clean-reference.stl').read_bytes()).hexdigest()};(S/'validation.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
