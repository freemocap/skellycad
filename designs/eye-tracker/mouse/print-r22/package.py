from pathlib import Path
import json,hashlib,zipfile,shutil,trimesh
R=Path.cwd();H=R/'designs/eye-tracker/mouse/print-r22';O=R/'generated/eye-tracker/mouse/print-r22';S=O/'source';S.mkdir(exist_ok=True)
report={}
for p in (O/'hardware').glob('*.stl'):
 m=trimesh.load_mesh(p);shells=m.split();assert m.is_volume and all(s.is_volume for s in shells)
 assert len(shells)==(2 if 'carrier-and-holder' in p.name else 1)
 report[p.name]={'watertight':bool(m.is_watertight),'positive_shells':len(shells),'bounds_mm':m.bounds.tolist(),'volume_mm3':float(m.volume)}
(O/'hardware-mesh-validation.json').write_text(json.dumps(report,indent=2))
shutil.copy2(H/'README.md',O/'README.md')
shutil.copy2(H/'lineage.json',S/'lineage.json')
P=R/'designs/eye-tracker/mouse/skull-landmarks-study-r01'
for name in ['LICENSE','main.R','35_mic_23strain_mus_template_UCHAR-label.nii.gz']:shutil.copy2(P/'sources'/name,S/name)
shutil.copy2(P/'validation.json',S/'atlas-registration.json')
for p in H.glob('*.py'):shutil.copy2(p,S/p.name)
shutil.copy2(R/'designs/eye-tracker/mouse/raised-target-r19/review.json',S/'R19-review.json')
files=list((O/'anatomy').glob('*'))+list((O/'hardware').glob('*'))+list(S.glob('*'))
files += [O/n for n in ['README.md','anatomy-validation.json','hardware-validation.json','hardware-mesh-validation.json','skull-derivative.json','solidification-sections.png']]
for n in ['MOUSE-R22-anatomy-print.FCStd','anatomy-preview.png']:
 if (O/n).exists():files.append(O/n)
manifest={'revision':'MOUSE R22','units':'mm','source_checkpoint':'ET-MOUSE-RAISED-TARGET-R19','status':'Mesh-validated unsliced print candidate; physical fit untested','files':{p.relative_to(O).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));(H/'print-pack.json').write_text(json.dumps(manifest,indent=2));files.append(O/'manifest.json')
a=O/'MOUSE-R22-print-pack.zip'
with zipfile.ZipFile(a,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(O).as_posix())
with zipfile.ZipFile(a) as z:
 assert z.testzip() is None
 assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest['files'].items())
print(a,a.stat().st_size,report)
