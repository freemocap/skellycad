"""Export only R02 carrier and centered holder, retaining their print-in-place pose."""
raise RuntimeError('Superseded: this study lacks T3 PCB retention. Use designs/mouse-hats/current/export_print.py and active-model.json.')
from pathlib import Path
import json
import FreeCAD as App,Part,MeshPart
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-neutral-r02'
doc=next(d for d in App.listDocuments().values() if d.FileName.replace('\\','/').endswith('skull-neutral-r02/ribbon-space-study.FCStd'))
parts=[doc.NeutralCarrier,doc.CenteredHolder]
for o in parts:
 assert 'Invalid' not in o.State and o.Shape.isValid() and len(o.Shape.Solids)==1,o.Name
assert parts[0].Shape.common(parts[1].Shape,.001).Volume<1e-8
gap=parts[0].Shape.distToShape(parts[1].Shape)[0]
mesh=MeshPart.meshFromShape(Shape=Part.makeCompound([o.Shape for o in parts]),LinearDeflection=.03,AngularDeflection=.15,Relative=False)
path=OUT/'R02-ribbon-space-carrier-and-holder.stl';mesh.write(str(path))
report=dict(file=path.name,units='mm',parts=[o.Name for o in parts],linear_deflection_mm=.03,angular_deflection_radians=.15,native_gap_mm=gap,native_volumes_mm3=[o.Shape.Volume for o in parts],note='Two shells in assembled print-in-place pose. Skull, eyes, clip, cap, baseplate and aiming guides excluded. Physical fit unverified.')
(OUT/'print-export.json').write_text(json.dumps(report,indent=2))
print(path)
