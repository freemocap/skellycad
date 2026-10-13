from pathlib import Path
import json,hashlib
import FreeCAD as App,FreeCADGui as Gui,Part
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
s=json.loads((HERE/'settings.json').read_text());p=ROOT/s['source_checkpoint']
assert hashlib.sha256(p.read_bytes()).hexdigest()==s['source_sha256']
src=App.openDocument(str(p));x=s['seat_x_mm']
# Remove only the protruding part of the old ledge; preserve the plate beneath it.
outside=Part.makeBox(100,100,100,App.Vector(x,-30,-50))
removed=src.SideLedge.Shape.common(outside)
ledge=Part.makeBox(s['new_projection_mm']+s['embedded_depth_mm'],s['vertical_length_mm'],s['new_width_mm'],App.Vector(x-s['embedded_depth_mm'],s['new_bottom_y_mm'],s['center_z_mm']-s['new_width_mm']/2))
def revised(shape):return shape.cut(removed).fuse(ledge).removeSplitter()
carrier=revised(src.Carrier.Shape);carrier.check(True)
assert carrier.isValid() and len(carrier.Solids)==1
report={'revision':'MH-T3-EYE-R10','units':'mm, mm3','source_sha256':s['source_sha256'],'carrier_valid':True,'carrier_solids':1,'ledge_cap_gap_mm':ledge.distToShape(src.Cap.Shape)[0],'ledge_pcb_gap_mm':ledge.distToShape(src.ApproxPCB.Shape)[0],'holder_gap_mm':carrier.distToShape(src.Holder.Shape)[0]}
for n in ['Holder','Cap','Clip','Baseplate','ApproxPCB']:
 report[n+'_overlap_mm3']=carrier.common(src.getObject(n).Shape).Volume
 assert abs(report[n+'_overlap_mm3']-src.Carrier.Shape.common(src.getObject(n).Shape).Volume)<1e-6
assert abs(report['holder_gap_mm']-.3331646522386679)<1e-6
assert src.Carrier.Shape.cut(carrier).cut(removed).Volume<1e-6
assert carrier.cut(src.Carrier.Shape).cut(ledge).Volume<1e-6
for n in ['UpperCatch','UpperRail']:assert src.getObject(n).Shape.cut(carrier).Volume<1e-6
doc=App.newDocument('SideLedgeR10');doc.Label='MH-T3-EYE-R10 - lower thicker side ledge'
for old in src.Objects:
 if old.TypeId=='Part::Feature':
  o=doc.addObject('Part::Feature',old.Name);o.Shape=carrier if old.Name=='Carrier' else ledge if old.Name=='SideLedge' else revised(old.Shape) if old.Name=='T3ProtectedTray' else old.Shape.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
 elif old.TypeId=='Mesh::Feature':
  o=doc.addObject('Mesh::Feature',old.Name);o.Mesh=old.Mesh.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
info=doc.addObject('App::FeaturePython','Revision');info.addProperty('App::PropertyString','RevisionID');info.RevisionID='MH-T3-EYE-R10'
doc.recompute();App.setActiveDocument(doc.Name);Gui.activeDocument().activeView().viewRight();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(ROOT/'designs/mouse-hats/current/checkpoints/MH-T3-EYE-R10.FCStd'))
(HERE/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
