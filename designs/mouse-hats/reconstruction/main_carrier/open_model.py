"""Open the saved model with its tolerance-union feature available for edits."""
from pathlib import Path
import sys
import FreeCAD as App
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0,str(HERE))
import carrier_features
doc=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/main-carrier/01-tray-mount-candidate.FCStd'))
doc.TrayAndStemUnion.touch();doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.activeDocument().activeView().viewIsometric()
    Gui.activeDocument().activeView().fitAll()
