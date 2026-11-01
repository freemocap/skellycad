from pathlib import Path
import json,numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path.cwd();out=root/'generated/eye-tracker/adult-eyes-r01'
fig,axs=plt.subplots(1,2,figsize=(10,6),layout='constrained')
for ax,sp in zip(axs,['mouse','rat']):
 for region,col in [('sclera','#ddddcd'),('cornea','#397d9c')]:
  m=trimesh.load_mesh(out/f'{sp}-{region}.stl');v=m.vertices
  sel=v[(abs(v[:,1])<1e-6)&(v[:,0]>=0)]
  # Disk center vertices are internal, omit except at true pole.
  sel=sel[(sel[:,0]>1e-7)|np.isclose(sel[:,2],m.bounds[:,2].min())|np.isclose(sel[:,2],m.bounds[:,2].max())]
  unique={float(z):float(x) for z,x in sorted([(z,max(vv[0] for vv in sel if vv[2]==z)) for z in set(sel[:,2])])}
  z=np.array(sorted(unique));r=np.array([unique[k] for k in z]);ax.fill_betweenx(z,-r,r,color=col,alpha=.85,label='Revised '+region)
 if sp=='mouse':
  z=np.linspace(-1.26,1.6337757,1000)
  body=1.5*np.sqrt(np.maximum(0,1-(z/1.26)**2));cap=.75*np.sqrt(np.maximum(0,1-((z-1.0037757)/.63)**2));r=np.maximum(body,cap)
 else:
  z=np.linspace(-3.040094,3.250906,1000);r=np.where(z<=1.140906,3.205*np.sqrt(np.maximum(0,1-((z+.20591137)/2.83418267)**2)),2.929742787*np.sqrt(np.maximum(0,1-((z-.35600113)/2.89490482)**2)))
 ax.plot(r,z,'--',color='#414141',lw=1.4,label='Previous exterior');ax.plot(-r,z,'--',color='#414141',lw=1.4)
 ax.axvline(0,color='#29a344',lw=.9);ax.set_aspect('equal');ax.set_title(sp.title()+' eye');ax.set_xlabel('Transverse position (mm)');ax.set_ylabel('Anterior +Z (mm)');ax.grid(alpha=.2)
axs[0].legend(loc='lower left',fontsize=8)
fig.suptitle('Revised adult eye envelopes\nSolid: revised profile   Dashed: previous profile',fontsize=13)
fig.savefig(out/'profile-comparison.png',dpi=160)
