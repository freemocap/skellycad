from pathlib import Path
import json,numpy as np
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.patches import Circle
R=Path.cwd();S=R/'designs/eye-tracker/mouse/landmark-eyes-r04';O=R/'generated/eye-tracker/mouse/landmark-eyes-r04';v=np.load(O/'eye-tissue-crop.npy');poses=json.loads((S/'placement.json').read_text())['eyes'];picks=json.loads((S/'tissue-rim-picks.json').read_text())['eyes']
fig,axs=plt.subplots(2,3,figsize=(15,10))
for row,(x,y,z) in enumerate([(153,150,107),(231,155,98)]):
 planes=[(v[:,:,z-70],(11.5,27,20,11),'XY',x*.1,y*.1,[0,1],2,z*.1),(v[:,x-115,:,:],(7,14,20,11),'ZY',z*.1,y*.1,[2,1],0,x*.1),(v[y-110,:,:,:].transpose(1,0,2),(11.5,27,14,7),'XZ',x*.1,z*.1,[0,2],1,y*.1)]
 for col,(ax,(im,ext,title,h,k,ij,fixed,coord)) in enumerate(zip(axs[row],planes)):
  ax.imshow(im,extent=ext);c=np.array(poses[row]['center_source_index_mm']);rad=poses[row]['fitted_source_radius_mm'];cut=np.sqrt(max(0,rad**2-(c[fixed]-coord)**2));ax.add_patch(Circle(c[ij],cut,fill=False,color='#00ffff',lw=1.5));pts=np.array(picks[row]['planes'][col]['points_uv_mm']);ax.scatter(pts[:,0],pts[:,1],s=18,c='#ffcf20',edgecolors='black',linewidths=.4)
  ax.set_xlim(h-2.3,h+2.3);ax.set_ylim(k+2.3,k-2.3);ax.set_title(f'Eye {row+1}: {title}');ax.set_xlabel('Source index mm');ax.set_ylabel('Source index mm')
fig.suptitle('Yellow: visually picked outer-rim candidates | Cyan: fitted sphere used to estimate center\nSparse approximate tracing, not a validated full segmentation; adult CAD eye dimensions remain unchanged');fig.tight_layout();fig.savefig(O/'tissue-center-fit.png',dpi=160)
