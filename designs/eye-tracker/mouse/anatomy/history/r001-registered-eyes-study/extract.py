from pathlib import Path
import json,hashlib,zipfile
ROOT=Path.cwd();ST=ROOT/'designs/eye-tracker/mouse/registered-eyes-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/registered-eyes-study-r01'
for row in json.loads((ST/'sources.json').read_text())['files']:
 p=ST/'sources'/row['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];dest=OUT/('source-'+p.stem);dest.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():assert (dest/name).resolve().is_relative_to(dest.resolve())
  z.extractall(dest)
