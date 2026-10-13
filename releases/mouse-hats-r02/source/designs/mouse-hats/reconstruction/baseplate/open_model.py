"""Load the scripted feature before opening/recomputing the saved baseplate."""
from pathlib import Path
import sys
import FreeCAD as App
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0,str(HERE))
import baseplate_features
doc=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/baseplate/01-baseplate-candidate.FCStd'))
doc.Baseplate.touch();doc.recompute();doc.Baseplate.Shape.check(True)
if App.GuiUp:
    import FreeCADGui as Gui
    doc.Baseplate.ViewObject.Proxy=0;doc.Baseplate.Visibility=True
    Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(App.Vector(0,0,1),160).multiply(App.Rotation(App.Vector(1,0,0),70)).Q)
    Gui.activeDocument().activeView().fitAll()
