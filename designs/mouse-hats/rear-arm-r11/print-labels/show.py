"""Preview permanent labels on the exterior tray backs."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/rear-arm-r11/labeled'
doc=App.newDocument('R11EmbossedLabels');doc.Label='R11 A-E - embossed identity review'
colors=[(.25,.7,.85),(.32,.78,.5),(.92,.64,.28),(.65,.5,.84),(.87,.42,.48)]
for i,key in enumerate('ABCDE'):
 src=App.openDocument(str(OUT/('R11'+key+'-labeled.FCStd')))
 group=doc.addObject('App::Part','Option'+key);group.Label='R11'+key+' - embossed on back'
 for name in ['Carrier','Holder']:
  ob=doc.addObject('Part::Feature',key+name);ob.Shape=src.getObject(name).Shape.copy();group.addObject(ob);ob.ViewObject.ShapeColor=colors[i] if name=='Carrier' else (.65,.65,.72);ob.ViewObject.LineColor=(.1,.1,.1)
 group.Placement.Base=App.Vector(0,28 if i<3 else 0,(i-1)*52 if i<3 else (i-3.5)*52)
App.setActiveDocument(doc.Name);doc.recompute()
up=App.Vector(0,1,0);normal=App.Vector(-1,0,0)
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(up.cross(normal),up,normal,'ZXY').Q)
Gui.activeDocument().activeView().fitAll();doc.saveAs(str(OUT/'label-review.FCStd'))
