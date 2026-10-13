"""Build visible height variants from frozen R11B, without touching arm sources."""
from pathlib import Path
import json,hashlib
import FreeCAD as A,Part
from height_features import HeightCarrier,HeightCap
from pcb_reference import board_shape
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file());OUT=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry';OUT.mkdir(exist_ok=True)
m=json.loads((HERE/'r11b-reference-manifest.json').read_text());src=ROOT/m['snapshot'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['sha256']
r=A.openDocument(str(src))
profiles=json.loads((HERE.parent/'reconstruction/main_carrier/profiles.json').read_text())['features'][0]['profiles_mm']
cap=json.loads((HERE.parent/'reconstruction/pcb_cap/parameters.json').read_text())
report=[]
for offset in [0,.5,1.0]:
 d=A.newDocument('HeightStudy');d.Label='Tray height +'+str(offset)+' mm - R11B STUDY'
 base=d.addObject('Part::Feature','R11BReference');base.Shape=r.Carrier.Shape.copy()
 carrier=d.addObject('Part::FeaturePython','HeightCarrier');HeightCarrier(carrier,base,profiles);carrier.TrayUpperEdgeOffset=offset
 c=d.addObject('Part::FeaturePython','HeightCap');HeightCap(c,carrier,cap)
 for name in ['Holder','ClipReference','BaseplateReference']:
  o=d.addObject('Part::Feature',name);o.Shape=r.getObject(name).Shape.copy()
 pcb=d.addObject('Part::Feature','ApproxPCB');pcb.Label='PCB envelope - slot-derived 30 x 9.2 x 0.25 mm';pcb.Shape=board_shape()
 conn=d.addObject('Part::Feature','Connector');conn.Label='Connector - illustrative footprint';conn.Shape=Part.makeBox(1.45,4.2,2.4,A.Vector(5.53706399647303,10.3,-14))
 d.recompute();carrier.Shape.check(True);c.Shape.check(True)
 assert carrier.Shape.isValid() and c.Shape.isValid()
 row={'offset_mm':offset,'carrier_added_volume_mm3':carrier.Shape.Volume-r.Carrier.Shape.Volume,'cap_volume_mm3':c.Shape.Volume,'cap_added_volume_mm3':c.Shape.Volume-r.CapReference.Shape.Volume,'carrier_cap_overlap_mm3':carrier.Shape.common(c.Shape).Volume,'holder_gap_mm':carrier.Shape.distToShape(r.Holder.Shape)[0],'carrier_solids':len(carrier.Shape.Solids),'cap_solids':len(c.Shape.Solids)}
 if offset==0:
  assert carrier.Shape.exportBrepToString()==r.Carrier.Shape.exportBrepToString()
  assert abs(c.Shape.Volume-r.CapReference.Shape.Volume)<1e-5
 report.append(row);print(row,flush=True)
 d.saveAs(str(OUT/('height-'+str(offset).replace('.','p')+'.FCStd')));A.closeDocument(d.Name)
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
