from pathlib import Path
import sys,json,hashlib,numpy as np,trimesh
from skimage.measure import marching_cubes
R=Path.cwd();S=R/'designs/eye-tracker/mouse/skull-landmarks-study-r01';O=R/'generated/eye-tracker/mouse/landmark-review-r02';O.mkdir(exist_ok=True,parents=True)
sys.path.insert(0,str(R/'generated/eye-tracker/mouse/skull-landmarks-study-r01/python-deps'));import nibabel as nib
for f in json.loads((S/'sources.json').read_text())['files']:assert hashlib.sha256((S/'sources'/f['file']).read_bytes()).hexdigest()==f['sha256']
im=nib.load(S/'sources/35_mic_23strain_mus_template_UCHAR-label.nii.gz');a=np.asanyarray(im.dataobj)==1
v,f,_,_=marching_cubes(np.pad(a,1).astype(np.uint8),.5);v=nib.affines.apply_affine(im.affine,v-1)*[-1,-1,1]
m=trimesh.Trimesh(v,f);original=len(m.faces);m=m.simplify_quadric_decimation(face_count=180000);m.fix_normals();T=np.array(json.loads((S/'validation.json').read_text())['matrix_atlas_lps_to_assembly']);m.apply_transform(T);m.export(O/'detailed-reference.stl')
(O/'reference.json').write_text(json.dumps({'source_faces':original,'display_faces':len(m.faces),'transform':T.tolist(),'reference_only':True,'source':'magaMouseCTAtlasRepository'},indent=2));print(original,len(m.faces))
