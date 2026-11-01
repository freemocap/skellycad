"""Create an Orca U1 project with explicit part/tool assignments and TPU profile."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,hashlib
ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
OUT=ROOT/'generated/eye-tracker/shared/camera-dummy-r03'
PROFILE=Path('C:/Program Files/Snapmaker_Orca/resources/profiles/Snapmaker')
N='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
def resolved(kind,name):
 p=PROFILE/kind/(name+'.json');v=json.loads(p.read_text(encoding='utf-8'))
 base=resolved(kind,v['inherits']) if v.get('inherits') else {}
 base.update(v);return base
with zipfile.ZipFile(OUT/'CAMERA-DUMMY-R03-four-materials.3mf') as z:data={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(ROOT/'designs/mouse-hats/skull-print/inputs/orca-source-project.3mf') as z:
 settings=json.loads(z.read('Metadata/project_settings.config'))
tpu=resolved('filament','Generic TPU')
skip={'compatible_printers','compatible_prints','inherits','name','type','from','instantiation','setting_id','filament_id','description','version'}
for k,v in tpu.items():
 if k in skip:continue
 if isinstance(v,list) and len(v)==1 and isinstance(settings.get(k),list):
  old=settings[k]
  if len(old)==4:old[3]=v[0]
  elif len(old)==8:old[6:8]=[v[0],v[0]]
 elif k not in settings and isinstance(v,list) and len(v)==1:
  # Do not invent PLA values for settings missing from the source project.
  continue
settings['filament_type']=['PLA','PLA','PLA','TPU']
settings['filament_colour']=['#FF201A','#202024','#F0F0E6','#FFCC05']
settings['filament_settings_id'][3]='Generic TPU'
settings['filament_ids'][3]=tpu['filament_id']
# Explicit assignments, independent of 3MF base-material preview colors.
root=ET.fromstring(data['3D/3dmodel.model']);ET.register_namespace('',N)
for key,val in [('Application','Snapmaker_Orca-2.4.0'),('BambuStudio:3mfVersion','1')]:
 el=ET.Element('{'+N+'}metadata',{'name':key});el.text=val;root.insert(0,el)
root.find('{'+N+'}build/{'+N+'}item').set('transform','1 0 0 0 1 0 0 0 1 135 95 0')
names=['Red_PLA_boards','Black_PLA_lens','White_PLA_connector_LEDs','Yellow_TPU_ribbon']
cfg=ET.Element('config');ob=ET.SubElement(cfg,'object',{'id':'5'})
ET.SubElement(ob,'metadata',{'key':'name','value':'CAMERA DUMMY R03 - U1 four tools'})
for i,name in enumerate(names,1):
 part=ET.SubElement(ob,'part',{'id':str(i),'subtype':'normal_part'})
 for k,v in [('name',name),('extruder',str(i)),('matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')]:ET.SubElement(part,'metadata',{'key':k,'value':v})
plate=ET.SubElement(cfg,'plate');ET.SubElement(plate,'metadata',{'key':'plater_id','value':'1'});inst=ET.SubElement(plate,'model_instance')
for k,v in [('object_id','5'),('instance_id','0'),('identify_id','1')]:ET.SubElement(inst,'metadata',{'key':k,'value':v})
data['3D/3dmodel.model']=ET.tostring(root)
data['Metadata/model_settings.config']=ET.tostring(cfg)
data['Metadata/project_settings.config']=json.dumps(settings).encode()
out=OUT/'CAMERA-DUMMY-R03-Snapmaker-U1.3mf'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in data.items():z.writestr(n,b)
with zipfile.ZipFile(out) as z:
 c=ET.fromstring(z.read('Metadata/model_settings.config'));s=json.loads(z.read('Metadata/project_settings.config'))
 ids=[p.find("metadata[@key='extruder']").get('value') for p in c.findall('object/part')]
 assert ids==['1','2','3','4']
 assert s['filament_type']==['PLA','PLA','PLA','TPU'] and len(set(s['filament_colour']))==4
 assert s['nozzle_temperature'][6:8]==['240','240']
 assert s['printer_settings_id']=='Snapmaker U1 (0.4 nozzle)'
 # The packaging fix must not change any of the mesh geometry.
 old=ET.fromstring(data['3D/3dmodel.model'])
 with zipfile.ZipFile(OUT/'CAMERA-DUMMY-R03-four-materials.3mf') as original:
  before=ET.fromstring(original.read('3D/3dmodel.model'))
 for a,b in zip(old.findall('.//{'+N+'}mesh'),before.findall('.//{'+N+'}mesh')):assert ET.tostring(a)==ET.tostring(b)
report={'passed':True,'part_tools':dict(zip(names,ids)),'filament_types':s['filament_type'],'filament_colors':s['filament_colour'],'TPU_profile':'Installed Snapmaker Generic TPU preset; spool tuning unverified','printer':s['printer_settings_id'],'geometry_unchanged':True,'gui_verified':False,'sliced':False,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(OUT/'u1-project-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
