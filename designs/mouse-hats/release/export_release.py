"""Export the clean assembly in FreeCAD GUI; preserve user preferences."""
from pathlib import Path
import runpy
import FreeCAD as App
import FreeCADGui as Gui
import ImportGui
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
doc=runpy.run_path(str(HERE/'build_assembly.py'))['main']()
prefs=App.ParamGet('User parameter:BaseApp/Preferences/Mod/Part/STEP')
old=prefs.GetString('Scheme');old_unit=prefs.GetInt('Unit',0)
try:
    prefs.SetString('Scheme','AP242DIS');prefs.SetInt('Unit',0)
    ImportGui.export([doc.MouseHats_R02],str(ROOT/'releases/mouse-hats-r02/MouseHats_R02.step'),
                     exportHidden=False,legacy=False,keepPlacement=True)
finally:
    prefs.SetString('Scheme',old);prefs.SetInt('Unit',old_unit)
Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
