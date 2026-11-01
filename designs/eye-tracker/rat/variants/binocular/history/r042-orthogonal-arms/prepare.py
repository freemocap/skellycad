"""Seed a fresh R42 build from the hash-pinned R41 complete assembly."""
from pathlib import Path
import hashlib, json, shutil, zipfile
R=Path.cwd(); S=Path(__file__).resolve().parent
O=R/'generated/eye-tracker/rat/orthogonal-arms-r42'
cfg=json.loads((S/'recipe.json').read_text())
source=R/cfg['source_complete_assembly']['native_checkpoint']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_complete_assembly']['native_sha256']
assert not O.exists(), 'Preserve the existing output directory before starting a fresh build.'
with zipfile.ZipFile(source) as z:
 assert z.testzip() is None and 'Document.xml' in z.namelist()
O.mkdir(parents=True)
for name in ['source.FCStd','04-arms.FCStd','04-arms-working.FCStd']:
 shutil.copy2(source,O/name)
for p in source.parent.glob('*.brep'):
 shutil.copy2(p,O/p.name)
(O/'04-arms.json').write_text('{}')
print('R41 complete assembly verified; R42 inputs prepared.')
