"""Verify U1 settings, per-part slot assignments and embedded plate placement."""
from pathlib import Path
import json,zipfile,hashlib,xml.etree.ElementTree as ET,numpy as np,trimesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-eye-bridge-r02';O=R/'generated/eye-tracker/rat/print-eye-bridge-r02';new=O/'anatomy/RAT-R32-EB02-Snapmaker-U1.3mf';old=R/'generated/eye-tracker/rat/print-r27/anatomy/RAT-R27-Snapmaker-U1.3mf';NS={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(old) as z:settings0=json.loads(z.read('Metadata/project_settings.config'))
with zipfile.ZipFile(new) as z:
 assert z.testzip() is None;settings=json.loads(z.read('Metadata/project_settings.config'));assert settings==settings0;root=ET.fromstring(z.read('3D/3dmodel.model'));config=ET.fromstring(z.read('Metadata/model_settings.config'));assert not any(n.lower().endswith('.gcode') for n in z.namelist())
assert root.attrib['unit']=='millimeter';assert settings['printer_model']=='Snapmaker U1';slots={}
for part in config.findall('./object/part'):
 props={v.get('key'):v.get('value') for v in part.findall('metadata')};slots[props['name']]=int(props['extruder'])
assert slots=={'Skull-and-bridge':1,'Sclera':3,'Cornea':2,'Baseplate':4}
report={'printer_settings_unchanged':True,'printer_settings_id':settings['printer_settings_id'],'layer_height_mm':settings['layer_height'],'nozzles_mm':settings['nozzle_diameter'],'filament_slots':slots,'filament_profiles':settings['filament_settings_id'],'parts':{},'baseplate_world_pose_verified':False,'unsliced':True}
for node in root.findall('./c:resources/c:object',NS):
 mesh=node.find('c:mesh',NS)
 if mesh is None:continue
 name=node.attrib['name'];v=[[float(a.get(k)) for k in ['x','y','z']] for a in mesh.find('c:vertices',NS)];f=[[int(a.get(k)) for k in ['v1','v2','v3']] for a in mesh.find('c:triangles',NS)];m=trimesh.Trimesh(v,f,process=True);stl=trimesh.load_mesh(O/'anatomy'/(name+'.stl'));assert m.is_volume and np.allclose(m.bounds,stl.bounds,atol=1e-5) and abs(m.volume-stl.volume)<.01;report['parts'][name]={'volume_mm3':float(m.volume),'watertight':True}
shift=np.array(json.loads((O/'anatomy-validation.json').read_text())['common_print_translation_mm']);base=trimesh.load_mesh(O/'anatomy/Baseplate.stl');base.apply_translation(-shift);world=trimesh.load_mesh(O/'baseplate-world.stl');assert np.allclose(base.bounds,world.bounds,atol=1e-5) and abs(base.volume-world.volume)<.001;report['baseplate_world_pose_verified']=True
oldbase=trimesh.load_mesh(R/'generated/eye-tracker/rat/print-r27/baseplate-world.stl');oldbase.apply_translation([0,0,-2]);assert np.allclose(oldbase.bounds,world.bounds,atol=1e-5);report['baseplate_lowered_from_r27_mm']=2
(O/'u1-validation.json').write_text(json.dumps(report,indent=2));print('U1_SETTINGS_AND_GEOMETRY_PASS')
