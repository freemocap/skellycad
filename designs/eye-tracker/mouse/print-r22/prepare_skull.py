from pathlib import Path
import sys,json,hashlib,numpy as np,trimesh,manifold3d as mf
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
R=Path.cwd();O=R/'generated/eye-tracker/mouse/print-r22';O.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'generated/eye-tracker/mouse/skull-landmarks-study-r01/python-deps'));import nibabel as nib
P=R/'designs/eye-tracker/mouse/skull-landmarks-study-r01';source=P/'sources/35_mic_23strain_mus_template_UCHAR-label.nii.gz';im=nib.load(source);v=np.asarray(im.dataobj);a=v==1
labels,n=ndi.label(a);counts=np.bincount(labels.ravel());counts[0]=0;bone=labels==counts.argmax();del labels
# Atlas main.R identifies label 15 as endocranial space [@magaMouseCTAtlasRepository].
endo=v==15;work=bone|endo;del v
for y in range(work.shape[1]):
 section=work[:,y,:];closed=ndi.binary_closing(section,iterations=8);work[:,y,:]=section|ndi.binary_fill_holes(closed)
 print('section',y,flush=True) if y%200==0 else None
work=ndi.binary_fill_holes(np.pad(work,2));print('filled voxels',work.sum(),'bone',bone.sum(),flush=True)
assert np.all(work[2:-2,2:-2,2:-2][endo]);assert np.all(work[2:-2,2:-2,2:-2][bone])
# Remove any remaining disconnected dust before surface extraction.
lab,nc=ndi.label(work);c=np.bincount(lab.ravel());c[0]=0;work=lab==c.argmax();del lab
vv,ff,_,_=marching_cubes(ndi.gaussian_filter(work.astype(np.float32),.75),.5,allow_degenerate=False);vv=nib.affines.apply_affine(im.affine,vv-2)*[-1,-1,1]
m=trimesh.Trimesh(vv,ff);m.fix_normals(multibody=False)
if m.volume<0:m.invert()
x=mf.Manifold(mf.Mesh64(np.array(m.vertices,dtype=np.float64),np.array(m.faces,dtype=np.uint64)));assert x.status()==mf.Error.NoError;x=x.simplify(.025);z=x.to_mesh64();m=trimesh.Trimesh(np.array(z.vert_properties)[:,:3],np.array(z.tri_verts));T=np.array(json.loads((P/'validation.json').read_text())['matrix_atlas_lps_to_assembly']);m.apply_transform(T);print('surface check',m.is_watertight,m.is_winding_consistent,m.volume,flush=True);m.fix_normals(multibody=False);m.invert() if m.volume<0 else None;assert m.is_volume;m.export(O/'skull-print-world.stl')
report={'source':source.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'parent_print':'R21','method':'largest bone component + atlas endocranial label 15; coronal sections close 8 source voxels and fill holes; 3D fill enclosed cavities; retain largest volume','section_closing_distance_source_mm':8*float(im.header.get_zooms()[0]),'surface_smoothing_sigma_source_voxels':.75,'simplification_tolerance_source_mm':.025,'braincase_label_voxels':int(endo.sum()),'filled_voxels':int(work.sum()),'braincase_completely_filled':bool(np.all(work[2:-2,2:-2,2:-2][endo])),'watertight':bool(m.is_watertight),'volume_mm3':float(m.volume),'faces':len(m.faces),'transform':T.tolist()};assert report['braincase_completely_filled'];(O/'skull-derivative.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
# Source-space section comparison: no hollow braincase or nasal honeycomb.
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axs=plt.subplots(2,3,figsize=(11,7))
for j,y in enumerate([280,520,620]):
 axs[0,j].imshow(bone[:,y,:].T,origin='lower',cmap='gray');axs[0,j].set_title('R21 bone: section '+str(y));axs[1,j].imshow(work[2:-2,y+2,2:-2].T,origin='lower',cmap='gray');axs[1,j].set_title('R22 solid print')
 for ax in axs[:,j]:ax.set_xlim(100,420);ax.set_ylim(120,370)
fig.tight_layout();fig.savefig(O/'solidification-sections.png')



check=trimesh.load_mesh(O/'skull-print-world.stl');shells=check.split();assert check.is_volume and len(shells)==1
report.update(exported_stl_shells=len(shells),exported_stl_watertight=bool(check.is_watertight),enclosed_cavity_shells=int(sum(s.volume<0 for s in shells)));(O/'skull-derivative.json').write_text(json.dumps(report,indent=2))
