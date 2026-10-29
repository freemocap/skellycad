"""Package verified R32 trial-print files, provenance and reproduction scripts."""
from pathlib import Path
import json,hashlib,zipfile,shutil,py_compile
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-r32';O=R/'generated/eye-tracker/rat/print-r32';P=O/'source';P.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((S.parent/'compact-binocular-r32/review.json').read_text());assert sha(R/review['native_checkpoint'])==review['native_sha256']
for group in ['hardware','anatomy']:
 data=json.loads((O/(group+'-native-mesh-validation.json')).read_text());assert data and all(v['closed'] and not v['self_intersections'] for v in data.values())
u1=json.loads((O/'u1-validation.json').read_text());assert u1['printer_settings_unchanged'] and u1['baseplate_world_pose_verified']
for p in O.glob('*.FCStd'):
 with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
shutil.copy2(S/'README.md',O/'README.md');shutil.copy2(S/'lineage.json',P/'lineage.json');shutil.copy2(S.parent/'compact-binocular-r32/review.json',P/'R32-review.json')
for name in ['recipe.json','central-validation.json','comparison.json']:shutil.copy2(S.parent/'compact-binocular-r32'/name,P/('assembly-'+name))
for f in S.glob('*.py'):py_compile.compile(str(f),doraise=True);shutil.copy2(f,P/f.name)
with zipfile.ZipFile(O/'anatomy/RAT-R32-Snapmaker-U1.3mf') as z:(P/'inherited-u1-settings.json').write_bytes(z.read('Metadata/project_settings.config'))
reports=['hardware-validation.json','hardware-mesh-validation.json','hardware-native-mesh-validation.json','anatomy-validation.json','anatomy-native-mesh-validation.json','u1-validation.json','preview-validation.json','skull-derivative.json']
files=list((O/'anatomy').glob('*'))+list((O/'hardware').glob('*.stl'))+list(P.glob('*'))+[O/n for n in reports+['README.md','LICENSE-source.txt','RAT-R32-anatomy-print.FCStd','RAT-R32-hardware-print.FCStd','anatomy-preview.png','hardware-preview.png']]
manifest={'revision':'RAT R32','units':'mm','source_review':review,'status':'Verified unsliced trial-print pack; physical fit and strength untested','main_files':{'u1_anatomy':'anatomy/RAT-R32-Snapmaker-U1.3mf','all_hardware':'hardware/RAT-R32-all-hardware.stl'},'files':{f.relative_to(O).as_posix():sha(f) for f in files}}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));(S/'print-pack.json').write_text(json.dumps(manifest,indent=2));files.append(O/'manifest.json');archive=O/'RAT-R32-print-pack.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,h in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h,name
print('PACKAGED_AND_VERIFIED',archive,len(files),'files',archive.stat().st_size,'bytes')
