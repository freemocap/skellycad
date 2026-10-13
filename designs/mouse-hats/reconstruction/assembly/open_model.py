"""Open the linked assembly with custom part modules available; style links only."""
import runpy
from pathlib import Path
import FreeCAD as App

api = runpy.run_path(str(Path(__file__).with_name('build.py')))
api['load_modules']()
path = api['FILE'].resolve()
doc = next((d for d in App.listDocuments().values()
            if d.FileName and Path(d.FileName).resolve() == path), None)
if doc is None:
    doc = App.openDocument(str(path))
if App.GuiUp:
    import FreeCADGui as Gui
    for name,color,transparency in [
        ('Baseplate',(0.65,0.45,0.9),0.35),
        ('Tray',(0.2,0.8,0.9),0.0),
        ('Cap',(0.35,0.85,0.45),0.65),
        ('Socket',(0.95,0.7,0.2),0.25),
        ('Holder',(0.45,0.65,0.95),0.0),
        ('Clip',(0.95,0.35,0.65),0.0)]:
        view=doc.getObject(name).ViewObject
        view.OverrideMaterial=True
        material=view.ShapeMaterial
        material.DiffuseColor=color
        material.Transparency=transparency
        view.ShapeMaterial=material
        view.Visibility=True
    App.setActiveDocument(doc.Name)
    Gui.activeDocument().activeView().viewIsometric()
    Gui.activeDocument().activeView().fitAll()
    Gui.activeDocument().activeView().saveImage(str(api['OUT']/'linked-assembly.png'),1200,900,'Current')
    doc.save()
