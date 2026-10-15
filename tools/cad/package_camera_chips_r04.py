from pathlib import Path
import zipfile,xml.etree.ElementTree as ET
import trimesh
R=Path.cwd();O=R/'generated/eye-tracker/shared/camera-interlock-075-r04'
src=R/'generated/eye-tracker/shared/camera-interlock-075-r02/CAMERA-U1-0.750mm-INTERLOCK-3TEETH-PLA-TPU95AHF.3mf'
with zipfile.ZipFile(src) as z:data={n:z.read(n) for n in z.namelist()}
N='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',N)
root=ET.fromstring(data['3D/3dmodel.model']);mesh=root.find('{'+N+'}resources/{'+N+"}object[@id='2']/{"+N+'}mesh')
vs=mesh.find('{'+N+'}vertices');ts=mesh.find('{'+N+'}triangles');offset=len(vs)
chips=trimesh.load_mesh(O/'Black_PLA_chips.stl');assert chips.is_volume
for xyz in chips.vertices:ET.SubElement(vs,'{'+N+'}vertex',dict(zip(['x','y','z'],[format(v,'.10g') for v in xyz])))
for tri in chips.faces:ET.SubElement(ts,'{'+N+'}triangle',dict(zip(['v1','v2','v3'],[str(int(i)+offset) for i in tri])))
data['3D/3dmodel.model']=ET.tostring(root)
cfg=ET.fromstring(data['Metadata/model_settings.config']);cfg.find("object/metadata[@key='name']").set('value','Camera 0.75 mm - three-tooth joints and cosmetic chips')
cfg.find("object/part[@id='2']/metadata[@key='name']").set('value','2 Black PLA - lens and PCB chips')
assert [p.find("metadata[@key='extruder']").get('value') for p in cfg.findall('object/part')]==['1','2','3','4']
data['Metadata/model_settings.config']=ET.tostring(cfg)
out=O/'CAMERA-U1-0.750mm-3TEETH-PHOTO-CHIPS-PLA-TPU95AHF.3mf'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for name,b in data.items():z.writestr(name,b)
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(out)
