from pathlib import Path
import json,hashlib
import numpy as np,trimesh,manifold3d as mf
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
R=Path.cwd();O=R/'generated/eye-tracker/rat/print-r27';src=O/'RatDesignSkull.stl';m=trimesh.load_mesh(src);pitch=.15
print('Voxelizing current R27 skull',m.bounds,len(m.faces),flush=True)
v=m.voxelized(pitch);a=np.pad(v.matrix,5);origin=v.transform[:3,3]-5*pitch
# Seal small scan gaps, then fill the endocranial interior in transverse sections.
closed=ndi.binary_closing(a,iterations=3);work=a|closed
xs=origin[0]+np.arange(work.shape[0])*pitch;ys=origin[1]+np.arange(work.shape[1])*pitch
for i,x in enumerate(xs):
 section=work[i];filled=ndi.binary_fill_holes(ndi.binary_closing(section,iterations=4))
 # Protect the open lateral orbit; the medial cranial/nasal print core may be filled.
 allowed=np.abs(ys)<(7.0 if x<5 else 4.3)
 work[i]|=filled & allowed[:,None]
work=ndi.binary_fill_holes(work)
lab,n=ndi.label(work);counts=np.bincount(lab.ravel());counts[0]=0;largest=counts.argmax();removed=int(work.sum()-counts[largest]);work=lab==largest
field=ndi.gaussian_filter(work.astype(np.float32),.8)-.5
# A binary isosurface avoids near-coincident sliver triangles after STL float32 export.
v,f,_,_=marching_cubes((field>0).astype(np.float32),.5,spacing=(pitch,)*3)
out=trimesh.Trimesh(v+origin,f);out.invert();components=out.split();positive=[c for c in components if c.volume>0];out=max(positive,key=lambda c:c.volume)
trimesh.smoothing.filter_taubin(out,iterations=4)
out.export(O/'skull-print-world.stl');out=trimesh.load_mesh(O/'skull-print-world.stl');assert out.is_volume and out.volume>100
report={'source':'RatDesignSkull exported from hash-verified R27','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pitch_mm':pitch,'gap_closing_mm':.45,'section_closing_mm':.6,'orbit_preservation':'section fill restricted to medial abs(Y)<7 mm posterior to X=5, otherwise abs(Y)<4.3 mm','method':'voxel gap closure, constrained transverse filling, 3D cavity fill, largest connected body, exterior positive shell','discarded_disconnected_voxels':removed,'removed_cavity_shells':len(components)-len(positive),'original_bounds_mm':m.bounds.tolist(),'print_bounds_mm':out.bounds.tolist(),'watertight':bool(out.is_watertight),'volume_mm3':float(out.volume),'faces':len(out.faces),'surface_method':'binary marching cubes at 0.15 mm; four Taubin smoothing iterations; verified STL roundtrip'}
(O/'skull-derivative.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
# Save cross-section evidence for the print-only fill.
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axs=plt.subplots(2,3,figsize=(10,6))
for j,x in enumerate([-7,0,14]):
 i=int(np.argmin(abs(xs-x)));axs[0,j].imshow(a[i].T,origin='lower');axs[1,j].imshow(work[i].T,origin='lower');axs[0,j].set_title('Anatomical X='+str(x));axs[1,j].set_title('Print fill')
fig.tight_layout();fig.savefig(O/'solidification-sections.png');plt.close(fig)

