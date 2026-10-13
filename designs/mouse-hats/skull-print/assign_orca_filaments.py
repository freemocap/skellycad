"""Add native per-part filament assignments to the user's saved Orca project.
The input was saved with Snapmaker Orca from the corrected cornea-r02 model.
Retains printer, process, filament profiles, geometry and placement verbatim.
"""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,json,hashlib
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-print'
source=Path(__file__).parent/'inputs/orca-source-project.3mf'
dest=OUT/'MH-T3-EYE-R03-skull-Snapmaker-Orca.3mf'
# Existing spool colors in this user's project: red, black, white, yellow.
assignments=[('Skull',1),('Eyes',3),('Cornea',2),('Mount',4)]
with zipfile.ZipFile(source) as z:
 data={n:z.read(n) for n in z.namelist()}
cfg=ET.fromstring(data['Metadata/model_settings.config'])
obj=cfg.find('object');parts=obj.findall('part');assert len(parts)==4
for part,(name,slot) in zip(parts,assignments):
 part.find("metadata[@key='name']").set('value',name)
 old=part.find("metadata[@key='extruder']")
 if old is None:old=ET.SubElement(part,'metadata',{'key':'extruder'})
 old.set('value',str(slot))
data['Metadata/model_settings.config']=ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for name,content in data.items():z.writestr(name,content)
with zipfile.ZipFile(source) as a,zipfile.ZipFile(dest) as b:
 assert all(a.read(n)==b.read(n) for n in a.namelist() if n!='Metadata/model_settings.config')
 settings=json.loads(b.read('Metadata/project_settings.config'));assert len(settings['filament_colour'])==4
 result=dict(file=dest.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),assignments=dict(assignments),filament_colors=settings['filament_colour'],geometry_and_project_settings_unchanged=True)
(Path(__file__).parent/'orca-filament-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
