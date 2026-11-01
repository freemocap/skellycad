from pathlib import Path
import json,zipfile,hashlib,shutil,py_compile
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-r32-l02';O=R/'generated/eye-tracker/rat/print-r32-l02';OLD=R/'generated/eye-tracker/rat/print-r32';P=O/'source';P.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();previous=json.loads((OLD/'manifest.json').read_text())
for name,h in previous['files'].items():
 if name.startswith('anatomy/'):assert sha(O/name)==h,name
for folder in ['hardware','anatomy']:
 checks=json.loads((O/(folder+'-native-mesh-validation.json')).read_text());assert all(c['closed'] and c['self_intersections']==0 for c in checks.values())
for f in S.glob('*.py'):py_compile.compile(str(f),doraise=True);shutil.copy2(f,P/f.name)
shutil.copy2(S/'README.md',O/'README.md');shutil.copy2(OLD/'manifest.json',P/'layout01-manifest.json');shutil.copy2(OLD/'source/lineage.json',P/'anatomy-lineage.json')
files=list((O/'hardware').glob('*.stl'))+list((O/'anatomy').glob('*'))+list(P.glob('*'))+[O/n for n in ['README.md','LICENSE-source.txt','hardware-validation.json','hardware-mesh-validation.json','hardware-native-mesh-validation.json','anatomy-validation.json','anatomy-native-mesh-validation.json','skull-derivative.json','u1-validation.json','preview-validation.json','layout-validation.json','RAT-R32-anatomy-print.FCStd','RAT-R32-hardware-print.FCStd','anatomy-preview.png','hardware-preview.png','hardware-top.png']]
manifest={'revision':'RAT R32 L02','units':'mm','source_review':previous['source_review'],'status':'Unsliced trial-print layout; clips flat in XY on Z=0','anatomy_unchanged_from_layout01':True,'main_mechanism_unchanged':True,'main_files':previous['main_files'],'files':{f.relative_to(O).as_posix():sha(f) for f in files}}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));(S/'print-pack.json').write_text(json.dumps(manifest,indent=2));files.append(O/'manifest.json');p=O/'RAT-R32-L02-print-pack.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(O).as_posix())
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for name,h in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h
print('LAYOUT02_PACK_VERIFIED',len(files),p.stat().st_size)
