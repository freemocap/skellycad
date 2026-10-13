"""Show the print-in-place unit plus installed clip; cap/baseplate references hidden."""
from pathlib import Path
import sys
import FreeCAD as App
import FreeCADGui as Gui

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/'model'))
import holder_features,clip_features,retention_features
import attachment_arm_features,arm_finish_features,stem_blend_features
path=ROOT/'generated/mouse-hats/print-test/r01/print-in-place-review.FCStd'
doc=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve()==path.resolve()),None)
if doc:App.closeDocument(doc.Name)
doc=App.openDocument(str(path));doc.Label='PRINT TEST R01 — carrier, holder and extended clip'
for obj in doc.Objects:obj.ViewObject.Visibility=False
for name,color in [('Carrier',(.25,.78,.88)),('Holder',(.8,.55,.85)),('ClipReference',(1.,.72,.25))]:
    obj=doc.getObject(name);obj.ViewObject.Visibility=True;obj.ViewObject.ShapeColor=color
    obj.ViewObject.LineColor=(.12,.18,.2);obj.ViewObject.Deviation=.03
normal=App.Vector(1,.5,1);normal.normalize();up=App.Vector(0,1,0)
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(up.cross(normal),up,normal,'ZXY').Q)
Gui.activeDocument().activeView().fitAll();doc.save()
