"""Open the complete blended carrier without the rejected pad or overlays."""
from pathlib import Path
import sys
import FreeCAD as App
import FreeCADGui as Gui

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0,str(HERE))
import attachment_arm_features,arm_finish_features,stem_blend_features
path=ROOT/'generated/mouse-hats/arms/stem-blend/stem-blended-carrier.FCStd'
doc=next((d for d in App.listDocuments().values()
          if d.FileName and Path(d.FileName).resolve()==path.resolve()),None)
if doc is None:doc=App.openDocument(str(path))
App.setActiveDocument(doc.Name)
for obj in doc.Objects:obj.ViewObject.Visibility=False
final=doc.BlendedCarrier
final.ViewObject.Visibility=True
final.ViewObject.ShapeColor=(.25,.78,.88)
final.ViewObject.LineColor=(.12,.18,.2)
final.ViewObject.Deviation=.03
normal=App.Vector(-1,.7,1);normal.normalize();up=App.Vector(0,1,0)
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(up.cross(normal),up,normal,'ZXY').Q)
Gui.activeDocument().activeView().fitAll()
doc.save()
