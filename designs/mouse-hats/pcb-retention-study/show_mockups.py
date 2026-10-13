"""Open a separate review tab; leave arm documents untouched."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/pcb-retention-study'
doc=App.newDocument('PCBRetentionConcepts');doc.Label='PCB retention - R1 side lip / R2 end hood - CONCEPTS'
for key,shift in [('R1',0),('R2',24)]:
 source=App.openDocument(str(OUT/(key.lower()+'-concept.FCStd')))
 group=doc.addObject('App::Part',key);group.Label=key+(' - side lip' if key=='R1' else ' - end hood')
 for name,color,trans,visible in [('TrayDetail',(.25,.65,.8),0,True),('Catch',(.98,.65,.18),0,True),('BoardEdge',(.35,.85,.4),30,True),('InsertionStart',(.7,.4,.9),65,False),('CapReference',(.8,.8,.83),80,False),('CandidateCarrier',(.25,.65,.8),0,False)]:
  ob=doc.addObject('Part::Feature',key+name);ob.Label=source.getObject(name).Label;ob.Shape=source.getObject(name).Shape.copy();group.addObject(ob)
  ob.ViewObject.ShapeColor=color;ob.ViewObject.Transparency=trans;ob.ViewObject.LineColor=(.12,.15,.18);ob.ViewObject.Visibility=visible
 group.Placement.Base=App.Vector(0,0,shift)
 label=doc.addObject('App::Annotation',key+'Label');label.LabelText=[group.Label];label.Position=App.Vector(7,4.5,-14+shift);label.ViewObject.FontSize=16;label.ViewObject.TextColor=(.9,.9,.9);label.ViewObject.Visibility=True
 App.closeDocument(source.Name)
App.setActiveDocument(doc.Name);doc.recompute()
normal=App.Vector(1,-.75,-.55);up=App.Vector(0,1,0)
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(up.cross(normal),up,normal,'ZXY').Q)
Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(OUT/'pcb-retention-concepts.FCStd'))
