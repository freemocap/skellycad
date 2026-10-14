from pathlib import Path
import json,numpy as np,trimesh
from scipy.spatial.transform import Rotation
ROOT=Path.cwd();ST=ROOT/'designs/eye-tracker/mouse/registered-eyes-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/registered-eyes-study-r01'
landmarks=json.loads((ROOT/'designs/eye-tracker/mouse/skull-landmarks-study-r01/landmarks.json').read_text())['landmarks'];byid={r['source_label']:np.array(r['transferred_assembly_mm']) for r in landmarks}
unit=lambda v:v/np.linalg.norm(v)
x=unit(byid['13']-byid['16']);y=np.array([0.,0,-1]);y=unit(y-x*x.dot(y));z=np.cross(x,y);B=np.column_stack([x,y,z]);assert np.linalg.det(B)>.999999
# Skull forward is tilted 29 degrees down relative to the horizontal reference.
R=Rotation.from_euler('y',29,degrees=True).as_matrix()
reg=json.loads((ST/'registration.json').read_text());old=json.loads((ROOT/'designs/eye-tracker/mouse/adult-anatomy-r11/validation.json').read_text())['eyes'];rows=[]
for i,e in enumerate(reg['eyes']):
 sign=-1 if i==0 else 1;az=np.deg2rad(sign*64);el=np.deg2rad(22);dh=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
 ds=R.T@dh;d=B@ds;c=np.array(e['transferred_centroid_mm']);o=old[f'Eye{i+1}'];oc=np.array(o['frame_origin_world_mm']);od=np.array(o['axis_world'])
 row={'id':f'Eye{i+1}','atlas_label_centroid_mm':c.tolist(),'candidate_axis_world':d.tolist(),'candidate_axis_skull_frame':ds.tolist(),'old_center_mm':oc.tolist(),'old_axis_world':od.tolist(),'centroid_displacement_from_old_mm':float(np.linalg.norm(c-oc)),'axis_difference_deg':float(np.degrees(np.arccos(np.clip(d.dot(od),-1,1)))),'center_status':'atlas label centroid used only as a provisional envelope anchor; not a confirmed globe center','axis_status':'conditional on tentative bregma/lambda frame and spherical interpretation of published azimuth/elevation'};rows.append(row)
 T=np.eye(4);T[:3,:3]=Rotation.align_vectors([d],[[0,0,1]])[0].as_matrix();T[:3,3]=c
 for region in ['sclera','cornea']:
  m=trimesh.load(ROOT/f'generated/eye-tracker/adult-eyes-r01/mouse-{region}.stl');m.apply_transform(T);m.export(OUT/f'candidate-eye-{i+1}-{region}.stl')
report={'units':'mm','bregma_id':'13, tentative','lambda_id':'16, tentative','skull_basis_columns_X_forward_Y_left_Z_dorsal':B.tolist(),'horizon_to_skull_rotation':R.T.tolist(),'nominal_head_pitch_deg':-29,'horizon_eye_azimuth_deg':64,'horizon_eye_elevation_deg':22,'sources':['oommenStahl2008MouseOrientation'],'eyes':rows,'approved_for_assembly':False}
(ST/'comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
skull=trimesh.load(ROOT/'designs/eye-tracker/mouse/references/skull/Skull.stl');fig,axes=plt.subplots(1,2,figsize=(14,6))
for ax,(i,j),title in zip(axes,[(0,2),(0,1)],['Dorsal: placement and direction','Lateral: placement and direction']):
 ax.scatter(skull.vertices[::5,i],skull.vertices[::5,j],s=.4,c='gray',alpha=.3)
 for k,row in enumerate(rows):
  for label,c,d,color in [('Existing',row['old_center_mm'],row['old_axis_world'],'#5555bb'),('Candidate',row['atlas_label_centroid_mm'],row['candidate_axis_world'],'#d97912')]:
   c=np.array(c);d=np.array(d);ax.quiver(c[i],c[j],d[i]*4,d[j]*4,angles='xy',scale_units='xy',scale=1,color=color,label=label if k==0 else None)
  m=trimesh.load(OUT/f'candidate-eye-{k+1}-sclera.stl');ax.scatter(m.vertices[::100,i],m.vertices[::100,j],s=1,c='#d97912',alpha=.4)
 for lid in ['13','16']:
  c=byid[lid];ax.scatter(c[i],c[j],c='#ba2460',s=22);ax.annotate(('Bregma?' if lid=='13' else 'Lambda?'),(c[i],c[j]),xytext=(0,15),textcoords='offset points',fontsize=9)
 ax.margins(.15);ax.set_aspect('equal');ax.set_title(title,pad=22);ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly '+('Z' if j==2 else 'Y')+' (mm)');ax.legend()
fig.suptitle('Stage 2: conditional adult-eye envelope and gaze comparison — placement is not yet validated');fig.tight_layout();fig.savefig(OUT/'eye-comparison.png',dpi=150)
# All atlas IDs remain inspectable; each view retains source identity, without invented names.
fig,axes=plt.subplots(1,2,figsize=(16,9))
for ax,(i,j),title in zip(axes,[(0,2),(0,1)],['Dorsal landmark index','Lateral landmark index']):
 ax.scatter(skull.vertices[::5,i],skull.vertices[::5,j],s=.4,c='gray',alpha=.25)
 for row in landmarks:
  c=np.array(row['transferred_assembly_mm']);ax.scatter(c[i],c[j],s=10,c='#ad245a');ax.annotate(row['source_label'],(c[i],c[j]),xytext=(3,5),textcoords='offset points',fontsize=8)
 ax.margins(.15);ax.set_aspect('equal');ax.set_title(title,pad=22);ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly '+('Z' if j==2 else 'Y')+' (mm)')
fig.suptitle('45 transferred atlas landmarks — numeric source IDs; anatomical dictionary unresolved');fig.tight_layout();fig.savefig(OUT/'landmarks-all.png',dpi=170)
