"""Exploratory body-mounted arms on complete R08. R08 remains selected for print."""
from pathlib import Path
import json,hashlib,sys,copy
import FreeCAD as App,FreeCADGui as Gui,Part
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
for p in [HERE,HERE.parent/'model',HERE.parent/'rear-arm-r11']:sys.path.insert(0,str(p))
from body_geometry import build_geometry
s=json.loads((HERE/'settings.json').read_text());p=ROOT/s['source_checkpoint']
assert hashlib.sha256(p.read_bytes()).hexdigest()==s['source_sha256']
src=App.openDocument(str(p))
carrier,arm,path=build_geometry(copy.deepcopy(s),src,HERE/'socket-source.brep')
# Retain the current B2 label instead of the tray snapshot's legacy text.
tool=Part.Shape();tool.read(str(HERE.parent/'loop-options-r05/CarrierEmboss.brep'))
outside=Part.makeBox(100,200,200,App.Vector(3.70677424482636-100,-100,-100))
carrier=carrier.cut(tool.common(outside)).removeSplitter()
label_region=Part.makeBox(100.05,5,10,App.Vector(3.70677424482636-100,10.7,-5))
carrier=carrier.fuse(src.Carrier.Shape.common(label_region)).removeSplitter()
carrier.check(True);assert carrier.isValid() and len(carrier.Solids)==1
report={'status':'visual study, not selected for printing','source_sha256':s['source_sha256'],'units':'mm, mm3','socket_attachment_height_old_mm':3.9,'socket_attachment_height_new_mm':s['body_attachment_height_mm'],'socket_attachment_radius_old_mm':2.65,'socket_attachment_radius_new_mm':s['body_attachment_radius_mm'],'carrier_valid':True,'carrier_solids':1,'rear_path_length_mm':path.Length,'motion_sweep_checked':False}
for n in ['Holder','Cap','Clip','Baseplate','ApproxPCB']:
 report[n+'_overlap_mm3']=carrier.common(src.getObject(n).Shape).Volume
 assert abs(report[n+'_overlap_mm3']-src.Carrier.Shape.common(src.getObject(n).Shape).Volume)<1e-6
for n in ['UpperCatch','UpperRail','SideLedge']:assert src.getObject(n).Shape.cut(carrier).Volume<1e-6
report['holder_gap_mm']=carrier.distToShape(src.Holder.Shape)[0]
assert abs(report['holder_gap_mm']-.33316465223866826)<1e-6
assert carrier.common(src.OpticalAxis.Shape).Length<1e-6
doc=App.newDocument('SocketBodyStudyR09');doc.Label='R09 STUDY - arms on socket body'
for old in src.Objects:
 if old.Name in ['NewRearArm','NewRearPath','PreviousBArm','PreviousBPath','EyeRibbonArms']:continue
 if old.TypeId=='Part::Feature':
  o=doc.addObject('Part::Feature',old.Name);o.Shape=carrier if old.Name=='Carrier' else old.Shape.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
 elif old.TypeId=='Mesh::Feature':
  o=doc.addObject('Mesh::Feature',old.Name);o.Mesh=old.Mesh.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
for name,sh in [('NewRearArm',arm),('NewRearPath',path),('EyeRibbonArms',carrier.cut(doc.T3ProtectedTray.Shape))]:
 o=doc.addObject('Part::Feature',name);o.Shape=sh;o.Visibility=False
info=doc.addObject('App::FeaturePython','Revision');info.addProperty('App::PropertyString','RevisionID');info.RevisionID='MH-T3-EYE-R09-STUDY'
doc.recompute();App.setActiveDocument(doc.Name);Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(HERE/'MH-T3-EYE-R09-STUDY.FCStd'))
# Side-by-side full carriers: orange prior, cyan candidate, matched holder purple.
review=App.newDocument('SocketAttachmentComparison');review.Label='R08 stem vs R09 body - comparison'
for key,shape,offset,color in [('R08',src.Carrier.Shape,0,(.85,.55,.25)),('R09',carrier,48,(.2,.75,.8))]:
 for name,sh,col in [('Carrier',shape,color),('Holder',src.Holder.Shape,(.62,.45,.8))]:
  shifted=sh.copy();shifted.translate(App.Vector(0,0,offset))
  o=review.addObject('Part::Feature',key+name);o.Shape=shifted;o.ViewObject.ShapeColor=col
review.recompute();App.setActiveDocument(review.Name);Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
review.saveAs(str(HERE/'R08-R09-comparison.FCStd'))
(HERE/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
