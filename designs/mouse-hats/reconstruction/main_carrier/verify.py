"""Independent reopen, geometry, edit and scoped-reference checks."""
from pathlib import Path
import json,sys,runpy
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/main-carrier'
sys.path.insert(0,str(HERE))
import carrier_features

fresh=runpy.run_path(str(HERE/'build.py'))['main'](save=False)
fresh_volume=fresh.PCBTrayAndMount.Shape.Volume
App.closeDocument(fresh.Name)

doc=App.openDocument(str(OUT/'01-tray-mount-candidate.FCStd'))
doc.TrayAndStemUnion.touch();doc.recompute()
r=doc.PCBTrayAndMount.Shape.copy();r.check(True)
assert len(r.Solids)==1
assert abs(r.Volume-fresh_volume)<1e-7
s=Part.read(str(ROOT/'generated/mouse-hats/inspection/carrier-source.brep'))
s.check(True)
roi=Part.makeBox(50,50,40,App.Vector(-10,-10,-30)) # z <= 10, excludes old arm/root
reference=s.common(roi).removeSplitter();rebuilt=r.common(roi).removeSplitter()
missing=reference.cut(rebuilt,0.001);excess=rebuilt.cut(reference,0.001)
for name,shape in [('reference',reference),('rebuilt',rebuilt),('missing',missing),('excess',excess)]:
    print(name,shape.Volume,len(shape.Solids),flush=True)
    if shape.Solids:shape.check(True)
whole_extra=r.cut(s,0.001)
report=dict(units='mm',scope='PCB tray and mounting stem; old arm intentionally omitted',
    candidate_volume_mm3=r.Volume,candidate_faces=len(r.Faces),solid_count=len(r.Solids),
    deeper_geometry_check='passed',boolean_tolerance_mm=0.001,
    lower_region_z_max_mm=10,lower_reference_volume_mm3=reference.Volume,
    lower_missing_volume_mm3=missing.Volume,lower_excess_volume_mm3=excess.Volume,
    whole_candidate_excess_volume_mm3=whole_extra.Volume,
    full_carrier_parity=False,physical_fit_validated=False,edit_checks=[])
for name,delta in [('VentRadius',0.1),('VentSpacing',1)]:
    old=getattr(doc.Dimensions,name).Value
    setattr(doc.Dimensions,name,old+delta);doc.recompute()
    edited=doc.PCBTrayAndMount.Shape
    edited.check(True);assert len(edited.Solids)==1
    assert edited.cut(r,0.001).Volume+r.cut(edited,0.001).Volume>0.1
    report['edit_checks'].append(dict(property=name,original_mm=old,tested_mm=old+delta))
    setattr(doc.Dimensions,name,old);doc.recompute()
doc.PCBTrayAndMount.Shape.check(True)
assert abs(doc.PCBTrayAndMount.Shape.Volume-r.Volume)<1e-7
report['independent_reopen_recompute_edit_restore']='passed'
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
