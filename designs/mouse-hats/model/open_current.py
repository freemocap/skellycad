"""Open the canonical saved assembly with its Python feature modules available."""
from pathlib import Path
import runpy
import FreeCAD as App

api=runpy.run_path(str(Path(__file__).with_name('build_mount.py')))
api['load_modules']()
import current_view
path=api['ROOT']/'generated/mouse-hats/current/CURRENT.FCStd'
doc=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve()==path.resolve()),None)
if doc is None:doc=App.openDocument(str(path))
App.setActiveDocument(doc.Name)
if App.GuiUp:
    import FreeCADGui as Gui
    doc.ViewSelector.Proxy.onChanged(doc.ViewSelector,'Layout')
    Gui.Selection.clearSelection();Gui.Selection.addSelection(doc.ViewSelector)
