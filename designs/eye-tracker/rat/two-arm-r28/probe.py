from pathlib import Path
import sys,json,hashlib
import FreeCAD as A
R=Path.cwd();sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
records=json.loads((R/'designs/eye-tracker/rat/two-arm-r28/review-inputs.json').read_text())['inputs'];ds=[]
for r in [records[0],records[2]]:
 p=R/r['source_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['source_sha256'];ds.append(A.openDocument(str(p)))
a,b=ds;rib=world(a.RibbonCandidate)
for n in ['UpperSupport','RearRibbonGuard']:
 s=world(b.getObject(n));print(n,'ribbon overlap',s.common(rib).Volume,'gap',s.distToShape(rib)[0],flush=True)
