from pathlib import Path
import sys,json,hashlib,numpy as np,trimesh
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
from skimage.filters import threshold_otsu
sys.path.insert(0,'generated/eye-tracker/mouse/skull-landmarks-study-r01/python-deps');import nibabel as n
R=Path.cwd();S=R/'designs/eye-tracker/rat/anatomy-study-r10';O=R/'generated/eye-tracker/rat/anatomy-study-r10';a=n.load(S/'sources/Ratlas-LH.nii.gz');b=n.load(S/'sources/Ratlas-LH_Brain.nii.gz');assert np.allclose(a.affine,b.affine)
v=np.asarray(a.dataobj,dtype=np.float32)-np.asarray(b.dataobj,dtype=np.float32);print('residual',v.min(),v.max(),np.percentile(v[v>0],[10,50,90]),flush=True);v=np.maximum(v,0);threshold=float(threshold_otsu(v[v>0]));print('threshold',threshold,flush=True)
# RAS to CAD: X anterior, Y animal left, Z superior, bregma origin unchanged.
T=np.array([[0,1,0,0],[-1,0,0,0],[0,0,1,0],[0,0,0,1.]])
report={'threshold':threshold,'threshold_units':'distributed image intensity, not HU','affine':a.affine.tolist(),'RAS_to_CAD':T.tolist(),'variants':{}}
for name,factor in [('low',.8),('nominal',1),('high',1.2)]:
 mask=v>threshold*factor;labels,nc=ndi.label(mask);counts=np.bincount(labels.ravel());counts[0]=0;keep=np.flatnonzero(counts>1000);mask=np.isin(labels,keep);verts,faces,_,_=marching_cubes(mask.astype(np.uint8),.5,allow_degenerate=False);verts=n.affines.apply_affine(a.affine,verts);verts=n.affines.apply_affine(T,verts);m=trimesh.Trimesh(verts,faces);m.export(O/('ratlas-skull-'+name+'.stl'));report['variants'][name]={'factor':factor,'bounds_mm':m.bounds.tolist(),'faces':len(faces),'retained_voxels':int(mask.sum()),'components_before_filter':int(nc),'retained_components':len(keep)};print(name,report['variants'][name],flush=True)
(S/'extraction.json').write_text(json.dumps(report,indent=2))
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,3,figsize=(13,5))
for ax,z in zip(axs,[219,205,190]):
 ax.imshow(v[:,:,z].T,origin='lower',cmap='gray',vmin=0,vmax=1e9);ax.set_title(f'Skull residual, voxel Z={z}')
fig.tight_layout();fig.savefig(O/'skull-roof-sections.png')
