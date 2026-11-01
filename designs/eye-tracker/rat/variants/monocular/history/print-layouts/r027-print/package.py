from pathlib import Path
import json,hashlib,zipfile,shutil,trimesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-r27';O=R/'generated/eye-tracker/rat/print-r27';P=O/'source';P.mkdir(exist_ok=True)
shutil.copy2(S/'README.md',O/'README.md');shutil.copy2(R/'generated/eye-tracker/rat/skull-print-r02/LICENSE-source.txt',O/'LICENSE-source.txt')
for f in S.glob('*.py'):shutil.copy2(f,P/f.name)
review=json.loads((S.parent/'aligned-tip-r27/review.json').read_text());assert hashlib.sha256((R/review['native_checkpoint']).read_bytes()).hexdigest()==review['native_sha256'];shutil.copy2(S.parent/'aligned-tip-r27/review.json',P/'R27-review.json')
reports=['clip-validation.json','anatomy-validation.json','anatomy-mesh-validation.json','hardware-validation.json','hardware-mesh-validation.json','skull-derivative.json']
lineage={'source':review,'units':'mm','anatomical_inputs':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in O.glob('Rat*.stl')},'baseplate_input_sha256':hashlib.sha256((O/'baseplate-world.stl').read_bytes()).hexdigest(),'four_PLA_colors_confirmed_by_user':True,'bridge_diameter_mm':2.25,'bridge_material':'skull','baseplate_pose':'unchanged R27, common print translation only'};(P/'lineage.json').write_text(json.dumps(lineage,indent=2));(S/'lineage.json').write_text(json.dumps(lineage,indent=2))
for f in (O/'hardware').glob('*.stl'):
 m=trimesh.load_mesh(f);assert m.is_volume;assert len(m.split())==(2 if 'carrier-and-holder' in f.name else 1),f.name
for f in (O/'anatomy').glob('*.stl'):assert trimesh.load_mesh(f).is_volume
files=list((O/'anatomy').glob('*'))+list((O/'hardware').glob('*'))+list(P.glob('*'))+[O/n for n in reports+['README.md','LICENSE-source.txt','RAT-R27-clip-C01.FCStd','clip-preview.png','RAT-R27-anatomy-print.FCStd','RAT-R27-hardware-print.FCStd','label-preview.png','anatomy-preview.png','solidification-sections.png']]
manifest={'revision':'RAT R27','units':'mm','source_review':review,'status':'Mesh-validated unsliced print candidate; physical fit not yet tested','files':{f.relative_to(O).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2));(S/'print-pack.json').write_text(json.dumps(manifest,indent=2));files.append(O/'manifest.json')
a=O/'RAT-R27-print-pack.zip'
with zipfile.ZipFile(a,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,f.relative_to(O).as_posix())
with zipfile.ZipFile(a) as z:
 assert z.testzip() is None
 assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest['files'].items())
print(a,a.stat().st_size,flush=True)
