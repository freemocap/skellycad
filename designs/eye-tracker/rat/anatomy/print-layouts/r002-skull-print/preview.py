from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import trimesh,numpy as np
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'generated/eye-tracker/rat/skull-print-r02'
src=trimesh.load(ROOT/'designs/eye-tracker/rat/references/skull/aligned-r01/rat-skull-standard-aligned-r01.stl')
old=trimesh.load(ROOT/'generated/eye-tracker/rat/skull-print-r01/rat-skull-solid-r01.stl')
new=trimesh.load(OUT/'rat-skull-detailed-solid-r02.stl');fused=trimesh.load(OUT/'rat-skull-mandible-fused-r02.stl')
fig=plt.figure(figsize=(18,11),facecolor='#faf8f4')
for i,(m,title,elev,azim) in enumerate([(src,'Original anatomy',80,-90),(old,'R01: global smoothing',80,-90),(new,'R02: original surface + internal fill',80,-90),(fused,'R02: fused skull and mandible',23,-65)]):
 ax=fig.add_subplot(2,3,i+1,projection='3d');ax.plot_trisurf(m.vertices[:,0],m.vertices[:,1],m.vertices[:,2],triangles=m.faces,color='#c5b28f',linewidth=0,shade=True,rasterized=True)
 ax.set_xlim(-24,24);ax.set_ylim(-12,12);ax.set_zlim(-19,7);ax.set_box_aspect([48,24,26]);ax.view_init(elev=elev,azim=azim);ax.set_axis_off();ax.set_title(title)
for index,axis,value,title in [(5,1,0,'Midline: original vs filled R02'),(6,0,-10,'Braincase and jaw section')]:
 ax=fig.add_subplot(2,3,index);dims=[i for i in range(3) if i!=axis];n=np.eye(3)[axis]
 for m,col,label in [(src,'#a7adb5','Original'),(fused,'#a94f27','R02')]:
  s=trimesh.intersections.mesh_plane(m,n,n*value)
  ax.add_collection(LineCollection(s[:,:,dims],colors=col,linewidths=1,label=label))
 ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.25);ax.set_title(title);ax.legend();ax.set_xlabel('mm')
fig.tight_layout();fig.savefig(OUT/'comparison-r02.png',dpi=150)
