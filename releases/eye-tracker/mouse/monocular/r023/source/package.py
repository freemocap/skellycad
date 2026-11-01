from pathlib import Path
import hashlib,json,shutil,zipfile,xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree

R=Path.cwd();H=R/'designs/eye-tracker/mouse/print-r23';O=R/'generated/eye-tracker/mouse/print-r23';P=O.with_name('print-r22')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
active=json.loads((H.parent/'active-model.json').read_text())
assert digest(R/active['native_checkpoint'])==active['native_sha256']
old=json.loads((P/'anatomy-validation.json').read_text());new=json.loads((O/'anatomy-validation.json').read_text())
assert old['world_to_anatomical_print_frame']==new['world_to_anatomical_print_frame']
shift=np.array(new['common_print_translation_mm'])-np.array(old['common_print_translation_mm'])
report={'units':'mm','common_translation_change_mm':shift.tolist(),'preserved_regions':{},'hardware':{},'print_regions':{}}
for name in ['Sclera','Cornea','Baseplate']:
    before=trimesh.load_mesh(P/'anatomy'/(name+'.stl'));after=trimesh.load_mesh(O/'anatomy'/(name+'.stl'));after.apply_translation(-shift)
    distances=[cKDTree(a.vertices).query(b.vertices)[0].max() for a,b in [(before,after),(after,before)]]
    assert max(distances)<1e-5 and before.faces.shape==after.faces.shape
    report['preserved_regions'][name]={'max_vertex_difference_mm':float(max(distances)),'faces_unchanged':True}
for file in (O/'hardware').glob('*.stl'):
    assert digest(file)==digest(P/'hardware'/file.name.replace('R23','R22'))
    m=trimesh.load_mesh(file);assert m.is_volume
    report['hardware'][file.name]={'identical_to_R22':True,'watertight':True,'shells':len(m.split())}
for name in ['Skull-and-bridge','Sclera','Cornea','Baseplate','mouse-eyes','mouse-eyes-embedded-baseplate']:
    m=trimesh.load_mesh(O/'anatomy'/(name+'.stl'));assert m.is_volume
    shells=len(m.split(only_watertight=False))
    if name in ['Skull-and-bridge','mouse-eyes','mouse-eyes-embedded-baseplate']:assert shells==1
    report['print_regions'][name]={'watertight':True,'shells':shells}
with zipfile.ZipFile(O/'anatomy/MOUSE-R23-Snapmaker-U1.3mf') as z:
    assert z.testzip() is None
    config=ET.fromstring(z.read('Metadata/model_settings.config'))
    slots=[int(p.find("metadata[@key='extruder']").get('value')) for p in config.findall('./object/part')]
    assert slots==[1,3,2,4]
    settings=json.loads(z.read('Metadata/project_settings.config'));assert 'U1' in settings['printer_settings_id']
    report['filament_slots']=slots;report['printer_settings_id']=settings['printer_settings_id']
report['max_material_overlap_mm3']=max(new['overlap_mm3'].values());assert report['max_material_overlap_mm3']<1e-5
(O/'preservation-validation.json').write_text(json.dumps(report,indent=2))
shutil.copy2(H/'README.md',O/'README.md')
S=O/'source';S.mkdir(exist_ok=True)
for file in H.glob('*.py'):shutil.copy2(file,S/file.name)
shutil.copy2(H/'lineage.json',S/'lineage.json')
study=H.parent/'skull-landmarks-study-r01'
for name in ['LICENSE','main.R','35_mic_23strain_mus_template_UCHAR-label.nii.gz']:
    shutil.copy2(study/'sources'/name,S/name)
shutil.copy2(study/'validation.json',S/'atlas-registration.json')
shutil.copy2(H.parent/'landmark-eyes-r04/placement.json',S/'accepted-eye-placement.json')
for file in O.glob('*-mandible-world.stl'):shutil.copy2(file,S/file.name)
shutil.copy2(O/'print-connections-world.stl',S/'print-connections-world.stl')
files=sorted((O/'anatomy').glob('*'))+sorted((O/'hardware').glob('*'))+sorted(S.glob('*'))
files += [O/n for n in ['README.md','anatomy-validation.json','hardware-validation.json','hardware-mesh-validation.json',
                       'mandible-extraction.json','jaw-connections.json','preservation-validation.json',
                       'anatomy-preview.png','jaw-side-view.png','jaw-front-view.png','jaw-registration-review.png']]
assert all(p.is_file() for p in files)
manifest={'revision':'MOUSE R23','units':'mm','source_checkpoint':active['revision'],
          'status':'Mesh-validated connected-jaw print candidate; unsliced and physical fit untested',
          'files':{p.relative_to(O).as_posix():digest(p) for p in files}}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));(H/'print-pack.json').write_text(json.dumps(manifest,indent=2))
archive=O/'MOUSE-R23-print-pack.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in files+[O/'manifest.json']:z.write(file,file.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,h in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
print(json.dumps(report,indent=2));print('PACK VERIFIED',archive,archive.stat().st_size)
