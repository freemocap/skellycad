"""Five separately labeled candidates; comparison translations are display only."""
from pathlib import Path
import sys,json
import FreeCAD as App
import FreeCADGui as Gui
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'print-test-r03',HERE.parent/'print-test']:sys.path.insert(0,str(p))
import options_sweep,options_carrier_features,socket_revision_features
OUT=ROOT/'generated/mouse-hats/rear-arm-r11'
s=json.loads((HERE/'settings.json').read_text())
ref=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r03/print-in-place-review.FCStd'))
doc=App.newDocument('LowerDepartureOptions');doc.Label='R11 - choose A / B / C / D / E'
locations={'A':(-44,32),'B':(0,32),'C':(44,32),'D':(-22,-4),'E':(22,-4)}
colors={'A':(.25,.7,.85),'B':(.32,.78,.5),'C':(.92,.64,.28),'D':(.65,.5,.84),'E':(.87,.42,.48)}
for key,variant in s['variants'].items():
 source=App.openDocument(str(OUT/('r11'+key.lower()+'-carrier.FCStd')))
 group=doc.addObject('App::Part','Option'+key);group.Label=key+' - '+variant['label']
 for name,shape,color in [('Carrier',source.RibbonClearanceCarrier.Shape,colors[key]),('Holder',ref.Holder.Shape,(.65,.65,.72)),('Clip',ref.ClipReference.Shape,(.8,.6,.55))]:
  ob=doc.addObject('Part::Feature',key+name);ob.Shape=shape.copy();group.addObject(ob);ob.ViewObject.ShapeColor=color;ob.ViewObject.LineColor=(.12,.16,.19)
 x,y=locations[key];group.Placement.Base=App.Vector(x,y,0)
 label=doc.addObject('App::Annotation','Label'+key);label.LabelText=[key+' - '+variant['label']];label.Position=App.Vector(x-12,y-11,0);label.ViewObject.TextColor=(.95,.95,.95);label.ViewObject.FontSize=16;label.ViewObject.Visibility=True
App.setActiveDocument(doc.Name);doc.recompute();Gui.activeDocument().activeView().viewTop();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(OUT/'five-arm-options.FCStd'))
