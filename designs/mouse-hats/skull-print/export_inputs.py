"""Run in the pinned FreeCAD GUI; extract the current checkpoint, never an old study."""
from pathlib import Path
import hashlib,json
import FreeCAD as App,MeshPart
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
HERE=Path(__file__).parent
m=json.loads((ROOT/'designs/mouse-hats/current/active-model.json').read_text())
p=ROOT/m['native_checkpoint']
assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256']
d=next((x for x in App.listDocuments().values() if Path(x.FileName)==p),None) or App.openDocument(str(p))
assert d.Revision.RevisionID==m['revision']
out=HERE/'inputs';out.mkdir(parents=True,exist_ok=True)
for n in ['Skull','Eye1','Eye2']:
 d.getObject(n).Mesh.write(str(out/(n+'.stl')))
assert d.Baseplate.Shape.isValid()
MeshPart.meshFromShape(Shape=d.Baseplate.Shape,LinearDeflection=.02,AngularDeflection=.12,Relative=False).write(str(out/'Baseplate.stl'))
(HERE/'lineage.json').write_text(json.dumps(dict(revision=m['revision'],checkpoint=m['native_checkpoint'],checkpoint_sha256=m['native_sha256'],units='mm',inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.stl')}),indent=2))
print(str(out))
