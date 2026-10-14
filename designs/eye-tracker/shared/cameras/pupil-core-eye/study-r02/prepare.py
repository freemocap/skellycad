import json,hashlib,copy
from pathlib import Path
p=Path('designs/eye-tracker/shared/cameras/pupil-core-eye')
r=p/'study-r02'
d=json.loads((p/'study-r01/blender-scene.json').read_text());scene={o['name']:o for o in d['objects']}
params={'units':'mm','confirmed_by_user':True,'measurement_source':'caliper-sketch.jpg','sketch_sha256':hashlib.sha256((r/'caliper-sketch.jpg').read_bytes()).hexdigest(),'main_pcb':{'length':30.85,'width':9},'ribbon':{'length':32.85,'width':4},'camera_head':{'width':6,'lower_length':10,'neck_length':2,'led_section_length':3,'neck_width':4,'neck_width_status':'Sketch interpretation; not separately confirmed'},'assumptions':{'board_thickness':.25,'ribbon_thickness':.15,'lens_thread_pitch':None,'connector_part_number':None,'safe_minimum_bend_radius':None},'lens_nominal_diameter':4,'source_blend_sha256':d['source_sha256']}
(r/'measurements.json').write_text(json.dumps(params,indent=2)+'\n')
# Recover centered source board datums; correct each measured region independently.
pcb=scene['PCB']['vertices'];cx=(min(v[0] for v in pcb)+max(v[0] for v in pcb))/2
xmin=min(v[0] for v in pcb);xmax=max(v[0] for v in pcb);ymin=min(v[1] for v in pcb);ymax=max(v[1] for v in pcb)
for v in pcb:v[0]=(v[0]-cx)*9/(xmax-xmin);v[1]=(v[1]-ymax)*30.85/(ymax-ymin)
for v in scene['JST-4pin']['vertices']:v[0]-=cx;v[1]+=(-30.85-ymin)
rib=scene['ribbon']['vertices'];rx0=min(v[0] for v in rib);rx1=max(v[0] for v in rib);ry0=min(v[1] for v in rib);ry1=max(v[1] for v in rib)
for v in rib:v[0]=(v[0]-(rx0+rx1)/2)*4/(rx1-rx0);v[1]=(v[1]-ry0)*32.85/(ry1-ry0)
head=scene['camera-pcb']['vertices'];hc=(min(v[0] for v in head)+max(v[0] for v in head))/2
levels=sorted(set(v[1] for v in head));targets=[32.85,42.85,44.85,47.85]
def map_y(y):
 i=next((i for i in range(3) if y<=levels[i+1]),2)
 return targets[i]+(y-levels[i])/(levels[i+1]-levels[i])*(targets[i+1]-targets[i])
for i,v in enumerate(head):v[0]=(-3 if v[0]<hc else 3) if i<8 else (-2 if v[0]<hc else 2);v[1]=map_y(v[1])
# Move component envelopes by their centers; do not rescale unmeasured hardware.
for name in ['M4-lens','IR-LED','IR-LED.001']:
 obj=scene[name];cy=sum(v[1] for v in obj['vertices'])/len(obj['vertices']);dy=map_y(cy)-cy
 for v in obj['vertices']:v[0]-=hc;v[1]+=dy
for o in scene.values():o['dimensions']=[max(v[i] for v in o['vertices'])-min(v[i] for v in o['vertices']) for i in range(3)]
(r/'calibrated-scene.json').write_text(json.dumps({'units':'mm','status':'User-confirmed plan dimensions; other geometry inherited or assumed','objects':list(scene.values())},indent=2)+'\n')
print('Caliper parameters and calibrated scene saved')
