"""Show the complete board, its upward escape and the correct top edge."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/pcb-retention-study'
# Keep rejected concepts available as history, explicitly marked.
for d in App.listDocuments().values():
 if d.Name.startswith('PCBRetentionConcepts'):d.Label='REJECTED - cropped PCB corner catches'
doc=App.openDocument(str(OUT/'whole-board-review.FCStd'))
for o in doc.Objects:
 if not hasattr(o,'Shape'):continue
 o.ViewObject.Visibility=True;o.ViewObject.LineColor=(.12,.16,.18)
 if o.Name=='Carrier':o.ViewObject.ShapeColor=(.27,.64,.78)
 elif o.Name=='WholePCB':o.ViewObject.ShapeColor=(.22,.7,.32);o.ViewObject.Transparency=12
 elif o.Name=='UpperEdgeTarget':o.ViewObject.ShapeColor=(1.0,.62,.08)
 elif o.Name.startswith('EscapeArrow'):o.ViewObject.ShapeColor=(1.0,.16,.12)
 elif o.Name=='ConnectorEnvelope':o.ViewObject.ShapeColor=(.94,.94,.88)
 elif o.Name=='ComponentEnvelope':o.ViewObject.ShapeColor=(.18,.18,.2);o.ViewObject.Transparency=65;o.ViewObject.Visibility=False
 elif o.Name in ['CapReference','BaseplateReference']:o.ViewObject.ShapeColor=(.75,.75,.78);o.ViewObject.Transparency=80;o.ViewObject.Visibility=False
 else:o.ViewObject.ShapeColor=(.64,.43,.76)
for name,text,point in [('MotionLabel','UPWARD ESCAPE',App.Vector(9,24,-2)),('BoardLabel','Whole PCB: 30 x 10 x 0.25 mm (approx.)',App.Vector(9,3,-3)),('TargetLabel','TOP EDGE TO CAPTURE',App.Vector(9,20,-8))]:
 o=doc.getObject(name) or doc.addObject('App::Annotation',name);o.LabelText=[text];o.Position=point;o.ViewObject.TextColor=(.95,.95,.95);o.ViewObject.FontSize=14;o.ViewObject.Visibility=True
App.setActiveDocument(doc.Name);doc.recompute()
normal=App.Vector(1,0,0);up=App.Vector(0,1,0)
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(up.cross(normal),up,normal,'ZXY').Q)
Gui.activeDocument().activeView().fitAll();doc.save()

