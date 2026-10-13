"""Export only the hash-verified assembly selected by active-model.json."""
from pathlib import Path
import hashlib,json
import FreeCAD as App,Part,MeshPart
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
HERE=Path(__file__).parent
m=json.loads((HERE/'active-model.json').read_text());p=ROOT/m['native_checkpoint']
assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256'],'Current checkpoint hash mismatch'
d=App.openDocument(str(p));assert d.Revision.RevisionID==m['revision']
assert d.UpperCatch.Shape.cut(d.Carrier.Shape).Volume<1e-6,'PCB catch missing'
assert d.UpperRail.Shape.cut(d.Carrier.Shape).Volume<1e-6,'T3 cap engagement rail missing'
assert d.Carrier.Shape.common(d.ApproxPCB.Shape).Volume<1e-6
assert d.Carrier.Shape.common(d.Holder.Shape).Volume<1e-6
out=ROOT/m['print_directory'];out.mkdir(parents=True,exist_ok=True)
report={'revision':m['revision'],'native_sha256':m['native_sha256'],'units':'mm','linear_deflection_mm':.03,'angular_deflection_rad':.15,'files':{}}
for name,parts in [('carrier-and-holder',[d.Carrier,d.Holder]),('matching-cap',[d.Cap]),('camera-clip',[d.Clip]),('baseplate',[d.Baseplate])]:
 for o in parts:assert o.Shape.isValid() and len(o.Shape.Solids)==1 and 'Invalid' not in o.State
 shape=Part.makeCompound([o.Shape for o in parts]) if len(parts)>1 else parts[0].Shape
 mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
 file=m['revision']+'-'+name+'.stl';mesh.write(str(out/file))
 report['files'][file]={'expected_shells':len(parts),'native_volumes_mm3':[o.Shape.Volume for o in parts]}
(out/'export.json').write_text(json.dumps(report,indent=2));print(str(out))
