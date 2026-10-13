"""Round-trip the published STEP in a fresh FreeCAD process."""
from pathlib import Path
import json
import FreeCAD as App
import Import
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'releases/mouse-hats-r02'
doc=App.newDocument('RoundTrip');Import.insert(str(OUT/'MouseHats_R02.step'),doc.Name)
native=App.openDocument(str(OUT/'MouseHats_R02.FCStd'))
expected=json.loads((OUT/'parts-geometry.json').read_text())
report=[]
for row in expected:
    candidates=[o for o in doc.Objects if o.Label.startswith(row['part_number']) and hasattr(o,'Shape')]
    assert len(candidates)==1,[(o.Name,o.Label) for o in doc.Objects]
    obj=candidates[0];s=obj.Shape
    warning=None
    try:s.check(True)
    except ValueError as error:warning=str(error)
    assert s.isValid() and len(s.Solids)==1
    solid=s.Solids[0]
    bounds=[getattr(s.optimalBoundingBox(False,False),k) for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]
    dv=abs(s.Volume-row['volume_mm3']);dc=(solid.CenterOfMass-App.Vector(*row['center_mm'])).Length
    db=max(abs(a-b) for a,b in zip(bounds,[getattr(native.getObject(row['part_number'].replace('-','_')).Shape.optimalBoundingBox(False,False),k) for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]))
    assert dv<1e-4 and dc<1e-5 and db<1e-5,(row['name'],dv,dc,db)
    report.append({'part':obj.Label,'valid':True,'deep_bop_warning':warning,'solids':1,'volume_error_mm3':dv,'centroid_error_mm':dc,'bounds_error_mm':db})
assert len([o for o in doc.Objects if hasattr(o,'Shape') and o.Label.startswith('MH-')])==5
(OUT/'step-roundtrip.json').write_text(json.dumps({'schema':'AP242','units':'mm','parts':report,'second_application_check':'not performed'},indent=2)+'\n')
print(json.dumps(report,indent=2))



