from pathlib import Path
import json,hashlib
import FreeCAD as A,Part
r=Path.cwd();out=r/'generated/eye-tracker/mouse/seated-tip-r07'
m=json.loads((r/'designs/eye-tracker/mouse/active-model.json').read_text());assert hashlib.sha256((r/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
p=json.loads((r/'designs/eye-tracker/mouse/joined-arms-r06/print-test.json').read_text());assert hashlib.sha256((r/p['native_checkpoint']).read_bytes()).hexdigest()==p['native_sha256']
d=A.openDocument(str(r/p['native_checkpoint']));original=d.FinishedCarrier.Shape
cfg=json.loads((r/'generated/eye-tracker/mouse/restored-arms-r05/validation.json').read_text())['arms']['UpperSupport'];c=A.Vector(*cfg['socket_center_mm']);n=A.Vector(*cfg['socket_axis']);v=A.Vector(*cfg['arm']['radial_direction']);t=v.cross(n);t.normalize()
# Localized top taper: meet collar's 5.4 mm axial top at radial 3.1 mm.
points=[(1.5,5.4),(3.1,5.4),(5.6,7.0),(5.6,12),(1.5,12)]
verts=[c+v*x+n*z-t*3 for x,z in points];wire=Part.makePolygon(verts+[verts[0]]);cutter=Part.Face(wire).extrude(t*6)
shape=original.cut(cutter).removeSplitter();shape.limitTolerance(1e-6);shape.check(True);assert shape.isValid() and len(shape.Solids)==1
print('removed',original.Volume-shape.Volume,flush=True)
shape.exportBrep(str(out/'finished.brep'))
report={'method':'Local terminal top taper to collar top','collar_top_height_mm':5.4,'taper_start_radial_mm':3.1,'taper_end_radial_mm':5.6,'taper_end_height_mm':7.0,'removed_volume_mm3':original.Volume-shape.Volume,'baseline_checkpoint':p['native_checkpoint'],'baseline_sha256':p['native_sha256']}
(out/'tip-correction.json').write_text(json.dumps(report,indent=2));(out/'fillets.json').write_text(json.dumps(p['validation']['junction_finishing']))
