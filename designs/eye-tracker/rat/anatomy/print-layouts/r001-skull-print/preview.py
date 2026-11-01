from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import trimesh, numpy as np
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'generated/eye-tracker/rat/skull-print-r01'
source=trimesh.load(ROOT/'designs/eye-tracker/rat/references/skull/aligned-r01/rat-skull-standard-aligned-r01.stl')
new=trimesh.load(OUT/'rat-skull-solid-r01.stl')
fig=plt.figure(figsize=(14,10),facecolor='#faf8f4')
for j,(m,title) in enumerate([(source,'Original skull and jaw'),(new,'Print revision: solid braincase, jaw separate')]):
 ax=fig.add_subplot(2,2,j+1,projection='3d')
 ax.plot_trisurf(m.vertices[:,0],m.vertices[:,1],m.vertices[:,2],triangles=m.faces,color='#c5b28f',linewidth=0,shade=True,rasterized=True)
 ax.set_box_aspect([47,24,25]);ax.set_xlim(-24,24);ax.set_ylim(-12,12);ax.set_zlim(-19,7);ax.view_init(elev=28,azim=-65);ax.set_title(title);ax.set_axis_off()
for ax,(axis,value,title) in zip([fig.add_subplot(223),fig.add_subplot(224)],[(1,0,'Midline section: filled braincase'),(0,-10,'Cross-section through braincase')]):
 n=np.eye(3)[axis];o=n*value;dims=[i for i in range(3) if i!=axis]
 for m,col,label in [(source,'#a8adb4','Original'),(new,'#b04d23','Print revision')]:
  segments=trimesh.intersections.mesh_plane(m,n,o)
  ax.add_collection(LineCollection(segments[:,:,dims],colors=col,linewidths=1.2,label=label))
 ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.25);ax.set_title(title);ax.legend();ax.set_xlabel('mm')
fig.tight_layout();fig.savefig(OUT/'comparison.png',dpi=130)
