"""R08: short vertical ledge at the user-marked far-hole outer edge."""
from pathlib import Path
import json,hashlib
import FreeCAD as App,FreeCADGui as Gui,Part
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
s=json.loads((HERE/'settings.json').read_text());p=ROOT/s['source_checkpoint']
assert hashlib.sha256(p.read_bytes()).hexdigest()==s['source_sha256']
src=App.openDocument(str(p));a=s['ledge_dimensions_xyz_mm']
ledge=Part.makeBox(*a,App.Vector(*s['ledge_origin_mm']))
carrier=src.Carrier.Shape.fuse(ledge).removeSplitter();carrier.check(True)
assert carrier.isValid() and len(carrier.Solids)==1
assert src.Carrier.Shape.cut(carrier).Volume<1e-6
report={'revision':'MH-T3-EYE-R08','units':'mm, mm3','source_sha256':s['source_sha256'],'carrier_valid':True,'carrier_solids':1,'added_volume_mm3':carrier.Volume-src.Carrier.Shape.Volume,'ledge_pcb_gap_mm':ledge.distToShape(src.ApproxPCB.Shape)[0],'ledge_cap_gap_mm':ledge.distToShape(src.Cap.Shape)[0]}
for n in ['Holder','Clip','Baseplate','ApproxPCB','Cap']:
 report[n+'_overlap_mm3']=carrier.common(src.getObject(n).Shape).Volume
 assert abs(report[n+'_overlap_mm3']-src.Carrier.Shape.common(src.getObject(n).Shape).Volume)<1e-6
for n in ['UpperCatch','UpperRail']:assert src.getObject(n).Shape.cut(carrier).Volume<1e-6
report['holder_gap_mm']=carrier.distToShape(src.Holder.Shape)[0]
assert abs(report['holder_gap_mm']-.33316465223866576)<1e-6
doc=App.newDocument('SideLedgeR08');doc.Label='MH-T3-EYE-R08 - B2 with vertical side ledge'
for old in src.Objects:
 if old.TypeId=='Part::Feature':
  o=doc.addObject('Part::Feature',old.Name);o.Shape=carrier if old.Name=='Carrier' else old.Shape.fuse(ledge).removeSplitter() if old.Name=='T3ProtectedTray' else old.Shape.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
 elif old.TypeId=='Mesh::Feature':
  o=doc.addObject('Mesh::Feature',old.Name);o.Mesh=old.Mesh.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
o=doc.addObject('Part::Feature','SideLedge');o.Shape=ledge;o.Label='Vertical side ledge - integrated into Carrier';o.Visibility=False
info=doc.addObject('App::FeaturePython','Revision');info.addProperty('App::PropertyString','RevisionID');info.RevisionID='MH-T3-EYE-R08'
doc.recompute();App.setActiveDocument(doc.Name)
Gui.activeDocument().activeView().viewRight();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(ROOT/'designs/mouse-hats/current/checkpoints/MH-T3-EYE-R08.FCStd'))
(HERE/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
