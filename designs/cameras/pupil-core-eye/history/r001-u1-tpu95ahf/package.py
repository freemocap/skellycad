"""Package the selected, unchanged R08 geometry for four U1 tools."""
from pathlib import Path
import json,zipfile,hashlib,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[6];S=Path(__file__).resolve().parent
O=R/'generated/eye-tracker/shared/camera-u1-tpu95ahf-r01';O.mkdir(parents=True,exist_ok=True)
M=json.loads((S.parent/'active-model.json').read_text())
for rec in [M['native_checkpoint'],*M['parts'].values(),*M['exports'].values()]:
 assert hashlib.sha256((R/rec['path']).read_bytes()).hexdigest()==rec['sha256']
source=M['exports']['CAMERA-DUMMY-R08-Snapmaker-U1.3mf']
with zipfile.ZipFile(R/source['path']) as z:data={n:z.read(n) for n in z.namelist()}
P=Path('C:/Program Files/Snapmaker_Orca/resources/profiles/Snapmaker/filament')
def resolve(name):
 v=json.loads((P/(name+'.json')).read_text(encoding='utf-8'))
 b=resolve(v['inherits']) if v.get('inherits') else {};b.update(v);return b
profile_name='Snapmaker TPU 95A HF @U1 0.4 nozzle'
tpu=resolve(profile_name);settings=json.loads(data['Metadata/project_settings.config'])
skip={'compatible_printers','compatible_prints','inherits','name','type','from','instantiation','setting_id','filament_id','description','version'}
for k,v in tpu.items():
 if k in skip or not isinstance(v,list) or len(v)!=1:continue
 old=settings.get(k)
 if isinstance(old,list) and len(old)==4:old[3]=v[0]
 elif isinstance(old,list) and len(old)==8:old[6:8]=[v[0],v[0]]
settings['filament_settings_id'][3]=profile_name
settings['filament_ids'][3]=tpu['filament_id']
settings['filament_type']=['PLA','PLA','PLA',tpu['filament_type'][0]]
settings['filament_colour']=['#FF201A','#202024','#FFFFFF','#FFCC05']
settings['layer_height']='0.125';settings['initial_layer_print_height']='0.125'
cfg=ET.fromstring(data['Metadata/model_settings.config'])
names=['1 Red PLA - both PCBs','2 Black PLA - lens assembly','3 White PLA - JST connector and IR LEDs','4 Yellow TPU 95A HF - ribbon']
for i,part in enumerate(cfg.findall('object/part')):
 part.find("metadata[@key='name']").set('value',names[i])
 assert part.find("metadata[@key='extruder']").get('value')==str(i+1)
data['Metadata/model_settings.config']=ET.tostring(cfg)
data['Metadata/project_settings.config']=json.dumps(settings).encode()
out=O/'CAMERA-R08-U1-Red-Black-White-TPU95AHF.3mf'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in data.items():z.writestr(n,b)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 with zipfile.ZipFile(R/source['path']) as original:assert z.read('3D/3dmodel.model')==original.read('3D/3dmodel.model')
assert settings['nozzle_temperature'][6:8]==['230','230']
assert settings['printer_settings_id']=='Snapmaker U1 (0.4 nozzle)'
report={'source':source,'geometry_unchanged':True,'materials':names,'TPU_profile':profile_name,'layer_height_mm':.125,'first_layer_height_mm':.125,'substrate_mm':.25,'sliced':False,'physical_print_verified':False,'project':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(S/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
