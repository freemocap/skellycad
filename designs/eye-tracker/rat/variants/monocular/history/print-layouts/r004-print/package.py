from pathlib import Path
import json,hashlib,zipfile,shutil
ROOT=Path.cwd();HERE=ROOT/'designs/eye-tracker/rat/print-r04';OUT=ROOT/'generated/eye-tracker/rat/print-r04'
shutil.copy2(HERE/'README.md',OUT/'README.md');shutil.copy2(ROOT/'generated/eye-tracker/rat/skull-print-r02/LICENSE-source.txt',OUT/'LICENSE-source.txt')
files=list((OUT/'anatomy').glob('*'))+list((OUT/'hardware').glob('*'))
files += [OUT/n for n in ['README.md','LICENSE-source.txt','anatomy-validation.json','hardware-validation.json','hardware-mesh-validation.json','RAT-R04-complete-assembly.FCStd','RAT-R04-anatomy-print.FCStd','RAT-R04-hardware-print.FCStd','anatomy-preview.png','label-preview.png']]
manifest={'revision':'RAT R04','units':'mm','source_review':'designs/eye-tracker/rat/targeted-r03/review.json','status':'Mesh-validated print candidate; U1 project has not been sliced or physically printed','files':{p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));(HERE/'print-pack.json').write_text(json.dumps(manifest,indent=2));files.append(OUT/'manifest.json')
archive=OUT/'RAT-R04-print-pack.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None;assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest['files'].items())
print(archive,archive.stat().st_size)
