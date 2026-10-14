from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
ROOT=Path.cwd();ST=ROOT/'designs/eye-tracker/mouse/registered-eyes-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/registered-eyes-study-r01';a=np.load(OUT/'labels.npy')
fig,axes=plt.subplots(2,3,figsize=(13,8))
for ax,k in zip(axes.flat,[90,95,100,105,110,115]):
 im=np.array(Image.open(OUT/f'source-cryo_data/cryo_data/average01_380x992x208_slices_tif/average01_380x992x208_slices{k:04d}.tif'))
 ax.imshow(im[105:195,120:265],extent=[12,26.5,19.5,10.5]);mask=(a[120:265,105:195,k]==3).T
 if mask.any():ax.contour(np.arange(120,265)*.1,np.arange(105,195)*.1,mask,levels=[.5],colors=['#00ffff'],linewidths=1)
 ax.set_title(f'Slice {k} / z={k*.1:.1f} mm');ax.set_xlabel('Voxel-index X (mm)');ax.set_ylabel('Voxel-index Y (mm)')
fig.suptitle('Source check: cyan = Digimouse eye label; white internal regions resemble crystalline lenses');fig.tight_layout();fig.savefig(OUT/'eye-label-slices.png',dpi=160)
