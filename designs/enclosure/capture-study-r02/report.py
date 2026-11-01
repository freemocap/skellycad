"""Coverage plots, robustness screens and sensor substitutions for the selected layout."""
from pathlib import Path
import copy
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from geometry import evaluate, grid, summary
from optimize import measure, regions, save_json

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[2]/'generated/enclosure/capture-study-r02'
settings=json.loads((HERE/'study.json').read_text())
cams=json.loads((OUT/'selected-layout.json').read_text())['cameras']
points=regions(25)
robustness={}
for i,c in enumerate(cams):
    robustness['without_'+c['id']]={k:summary(v) for k,v in measure(cams[:i]+cams[i+1:],settings,points).items()}
# A generic occluder, deliberately not species anatomy. Exclude its interior targets.
box=[[200,220,0],[300,280,70]]
outside={k:p[~((p>=box[0])&(p<=box[1])).all(axis=1)] for k,p in points.items()}
obstructed=dict(settings,obstacles=[box])
robustness['synthetic_central_box']={k:summary(v) for k,v in measure(cams,obstructed,outside).items()}
robustness['synthetic_central_box']['box_mm']=box
save_json(OUT/'robustness.json',robustness)

catalog=json.loads((HERE/'sensor-options.json').read_text())['options']
substitutions=[]
for side in catalog[:2]:
    c=copy.deepcopy(cams)
    for i in range(5):
        option=side if i<4 else catalog[2]
        # Preserve horizontal field of view; aspect changes affect vertical coverage.
        c[i]['focal_mm']*=option['sensor_mm'][0]/c[i]['sensor_mm'][0]
        c[i]['sensor_mm']=option['sensor_mm'];c[i]['pixels']=option['pixels']
    label=side['id']+'-with-ar0234-square-top'
    save_json(OUT/(label+'.json'),{'cameras':c,'status':'Hypothetical lens matching; focal length is derived, not selected SKU'})
    substitutions.append({'id':label,'corner_focal_mm':c[0]['focal_mm'],'top_focal_mm':c[4]['focal_mm'],
        'metrics':{k:summary(v) for k,v in measure(c,settings,points,True).items()}})
save_json(OUT/'sensor-substitutions.json',substitutions)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,axes=plt.subplots(2,3,figsize=(15,9),layout='constrained')
for row,z in enumerate((0,100)):
    p=grid(12.5,floor=True);p[:,2]=z
    m=evaluate(cams,p,settings)
    maps=[(m['count'],'Visible cameras','viridis',0,5),
          (m['pair_count']>0,'Qualified pair: ≥20°, 3 mm feature ≥3 px','RdYlGn',0,1),
          (m['second_density'],'Second-best view: pixels/mm','magma',0,4)]
    for ax,(values,title,cmap,vmin,vmax) in zip(axes[row],maps):
        im=ax.imshow(np.asarray(values).reshape(40,40).T,origin='lower',extent=(0,500,0,500),cmap=cmap,vmin=vmin,vmax=vmax)
        ax.set(title=f'{title}\nz = {z} mm',xlabel='x (mm)',ylabel='y (mm)',aspect='equal')
        for c in cams[:4]:ax.plot(*c['position_mm'][:2],'wo',ms=4,mec='k')
        fig.colorbar(im,ax=ax,shrink=.8)
fig.suptitle('CAPTURE R02 • ideal pinhole study • camera-body occlusion included\nEmpty-space coverage; animal, tether, calibration and timing errors excluded',fontsize=15)
fig.savefig(OUT/'coverage.png',dpi=150);plt.close(fig)
results=json.loads((OUT/'results.json').read_text())['metrics']
fig,axes=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
names=['baseline','floor-priority','cube-priority'];x=np.arange(3)
for ax,metric,title in zip(axes,['qualified_pair_pct','visible_ge3_pct'],['Qualified triangulation pair','At least three visible cameras']):
    for j,region in enumerate(('floor','lower','cube')):
        ax.bar(x+(j-1)*.24,[results[n][region][metric] for n in names],.24,label=region)
    ax.set(xticks=x,xticklabels=['Reference layout','Floor/lower priority','Full-cube priority'],ylim=(0,105),ylabel='Sampled coverage (%)',title=title)
    ax.legend(frameon=False);ax.grid(axis='y',alpha=.2)
fig.savefig(OUT/'comparison.png',dpi=160);plt.close(fig)
print(json.dumps({'robustness':robustness,'sensor_substitutions':substitutions},indent=2))
