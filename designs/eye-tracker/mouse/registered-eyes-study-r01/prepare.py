from pathlib import Path
import sys,json,hashlib,numpy as np,trimesh
from scipy import ndimage
from skimage.measure import marching_cubes
ROOT=Path.cwd(); STUDY=ROOT/'designs/eye-tracker/mouse/registered-eyes-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/registered-eyes-study-r01';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'generated/eye-tracker/mouse/skull-landmarks-study-r01/python-deps'));import nibabel as nib
im=nib.load(OUT/'source-atlas/atlas/atlas_380x992x208.hdr');a=np.asanyarray(im.dataobj).squeeze()
print(im.shape,im.header.get_zooms(),im.affine,flush=True)
# Provider explicitly specifies 0.1 mm isotropic; work in voxel-index axes until anatomical axes are verified.
for label in [2,3]:
 coords=np.argwhere(a==label);print(label,len(coords),coords.min(0),coords.max(0),flush=True)
l,n=ndimage.label(a==3)
for i in range(1,n+1):
 c=np.argwhere(l==i)
 if len(c)<50:continue
 print('eye',i,len(c),c.mean(0),flush=True)
 v,f,_,_=marching_cubes((l==i).astype(np.uint8),.5,spacing=(.1,.1,.1));trimesh.Trimesh(v,f).export(OUT/f'eye-{i}.stl')
np.save(OUT/'labels.npy',a)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,3,figsize=(15,6))
for ax,k in zip(axes,range(3)):
 ax.imshow(np.max((a==2).astype(int)+2*(a==3),axis=k).T,origin='lower');ax.set_title(f'Projection along voxel axis {k}')
fig.tight_layout();fig.savefig(OUT/'source-projections.png',dpi=150)

