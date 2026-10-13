"""Show a live clearance candidate and fixed checkpoint comparison close-up."""
from pathlib import Path
import runpy
import FreeCAD as App
import FreeCADGui as Gui
import Part

api=runpy.run_path(str(Path(__file__).with_name('build_mount.py')))
api['load_modules']()
doc=App.openDocument(str(api['OUT']/'mount-fit.FCStd'))
for obj in doc.Objects:
    obj.Visibility=False
doc.Baseplate.PocketClearance=0
doc.recompute()
doc.Baseplate.ViewObject.Proxy=0
doc.Baseplate.ViewObject.ShapeColor=(0.65,0.45,0.9)
doc.Baseplate.ViewObject.Transparency=45
doc.Baseplate.Visibility=True
# The stem is fixed under this control. Its section is an inspection snapshot.
section=doc.addObject('Part::Feature','StemInspectionSection')
section.Label='Fixed stem section — inspection only'
section.Shape=doc.PCBTrayAndMount.Shape.common(Part.makeBox(30,35,10.2,App.Vector(-10,-10,-5.1)))
section.ViewObject.ShapeColor=(0.2,0.8,0.9)
section.Visibility=True
baseline_file=api['ROOT']/'generated/mouse-hats/reconstruction/baseplate/01-baseplate-candidate.FCStd'
old=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve()==baseline_file.resolve()),None)
if old is None: old=App.openDocument(str(baseline_file))
reference=doc.addObject('Part::Feature','CheckpointBaseplate')
reference.Label='Checkpoint baseplate — fixed comparison, offset left'
reference.Shape=old.Baseplate.Shape.copy()
reference.Placement.Base.x-=18
reference.ViewObject.ShapeColor=(0.9,0.7,0.3)
reference.Visibility=True
doc.Label='Mount interface review — original fit, zero added clearance'
App.setActiveDocument(doc.Name)
Gui.Selection.clearSelection()
Gui.Selection.addSelection(doc.Baseplate)
view=Gui.activeDocument().activeView()
view.setCameraOrientation(App.Rotation(App.Vector(0,0,1),160).multiply(App.Rotation(App.Vector(1,0,0),70)).Q)
view.fitAll()
doc.recompute()
doc.saveAs(str(api['OUT']/'mount-fit-review.FCStd'))
view.saveImage(str(api['OUT']/'mount-fit-review.png'),1200,800,'Current')
