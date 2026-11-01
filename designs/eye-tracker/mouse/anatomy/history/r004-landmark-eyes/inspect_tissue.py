from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
R=Path.cwd();O=R/'generated/eye-tracker/mouse/landmark-eyes-r04';O.mkdir(parents=True,exist_ok=True)
source=R/'generated/eye-tracker/mouse/registered-eyes-study-r01/source-cryo_data/cryo_data/average01_380x992x208_slices_tif'
v=np.stack([np.array(Image.open(source/f'average01_380x992x208_slices{k:04d}.tif'))[110:200,115:270] for k in range(70,140)],axis=2);np.save(O/'eye-tissue-crop.npy',v)
fig,axs=plt.subplots(2,3,figsize=(15,10))
for row,(x,y,z) in enumerate([(153,150,107),(231,155,98)]):
 planes=[(v[:,:,z-70],(11.5,27,20,11),'XY',x*.1,y*.1),(v[:,x-115,:,:],(7,14,20,11),'ZY',z*.1,y*.1),(v[y-110,:,:,:].transpose(1,0,2),(11.5,27,14,7),'XZ',x*.1,z*.1)]
 for ax,(im,ext,title,h,k) in zip(axs[row],planes):
  ax.imshow(im,extent=ext);ax.set_xlim(h-2.3,h+2.3);ax.set_ylim(k+2.3,k-2.3);ax.set_xticks(np.arange(np.floor(h-2),np.ceil(h+2),.5));ax.set_yticks(np.arange(np.floor(k-2),np.ceil(k+2),.5));ax.grid(alpha=.25);ax.set_title(f'Eye {row+1} {title} (index mm)')
fig.tight_layout();fig.savefig(O/'orthogonal-tissue.png',dpi=170)
