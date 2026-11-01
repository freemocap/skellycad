from pathlib import Path
import hashlib,json,shutil
R=Path.cwd();H=R/'designs/eye-tracker/mouse/print-r23';O=R/'generated/eye-tracker/mouse/print-r23';P=O.with_name('print-r22')
O.mkdir(parents=True,exist_ok=True);(O/'hardware').mkdir(exist_ok=True)
active=json.loads((H.parent/'active-model.json').read_text())
assert active['revision']=='ET-MOUSE-RAISED-TARGET-R19'
assert hashlib.sha256((R/active['native_checkpoint']).read_bytes()).hexdigest()==active['native_sha256']
manifest=json.loads((H.with_name('print-r22')/'print-pack.json').read_text())
for name,digest in manifest['files'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
for name in ['baseplate-world.stl','Eye1Sclera.stl','Eye1Cornea.stl','Eye2Sclera.stl','Eye2Cornea.stl']:
    shutil.copy2(P/name,O/name)
for file in (P/'hardware').glob('*.stl'):
    shutil.copy2(file,O/'hardware'/file.name.replace('R22','R23'))
for name in ['hardware-validation.json','hardware-mesh-validation.json']:
    shutil.copy2(P/name,O/name)
lineage={'revision':'MOUSE R23','parent_print_revision':'MOUSE R22','source_checkpoint':active['native_checkpoint'],
         'source_sha256':active['native_sha256'],'change':'Add co-registered atlas mandibles with three permanent 1.2 mm print connections',
         'units':'mm','hardware':'Byte-identical R22 meshes, renamed R23',
         'parent_input_hashes':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['skull-print-world.stl','baseplate-world.stl','Eye1Sclera.stl','Eye1Cornea.stl','Eye2Sclera.stl','Eye2Cornea.stl']}}
(H/'lineage.json').write_text(json.dumps(lineage,indent=2));print('R19 and R22 verified; inputs ready.')
