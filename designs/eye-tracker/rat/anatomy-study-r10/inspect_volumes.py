from pathlib import Path
import sys,numpy as np,json,hashlib
sys.path.insert(0,'generated/eye-tracker/mouse/skull-landmarks-study-r01/python-deps');import nibabel as n
p=Path('designs/eye-tracker/rat/anatomy-study-r10');out=Path('generated/eye-tracker/rat/anatomy-study-r10');out.mkdir(parents=True,exist_ok=True)
r={}
for f in (p/'sources').glob('*.nii.gz'):
 im=n.load(f);v=np.asarray(im.dataobj);r[f.name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'shape':im.shape,'affine':im.affine.tolist(),'orientation':n.aff2axcodes(im.affine),'min':float(v.min()),'max':float(v.max()),'percentiles':np.percentile(v[v>0],[1,20,50,80,95,99]).tolist()};print(f.name,r[f.name],flush=True)
im=n.load(p/'sources/Ratlas-LH.nii.gz');v=np.asarray(im.dataobj);import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axes=plt.subplots(3,4,figsize=(13,10))
for ax in range(3):
 for j,f in enumerate([.25,.4,.55,.7]):
  s=np.take(v,int(v.shape[ax]*f),axis=ax);axes[ax,j].imshow(s.T,origin='lower',cmap='gray',vmin=0,vmax=np.percentile(v[v>0],98));axes[ax,j].set_title(f'axis {ax} fraction {f}')
fig.tight_layout();fig.savefig(out/'atlas-sections.png');(p/'volume-audit.json').write_text(json.dumps(r,indent=2))
