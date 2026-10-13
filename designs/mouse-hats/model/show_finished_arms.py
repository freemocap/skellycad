"""GUI loader: complete cyan carrier; new junction fillet faces highlighted gold."""
from pathlib import Path
import sys
import FreeCAD as App
import FreeCADGui as Gui

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0, str(HERE))
import attachment_arm_features, arm_finish_features

path = ROOT/'generated/mouse-hats/arms/finished/finished-arm-carrier.FCStd'
doc = next((d for d in App.listDocuments().values()
            if d.FileName and Path(d.FileName).resolve() == path.resolve()), None)
if doc is None:
    doc = App.openDocument(str(path))
App.setActiveDocument(doc.Name)
for obj in doc.Objects:
    obj.ViewObject.Visibility = False
final = doc.JunctionFillets
final.ViewObject.Visibility = True
final.ViewObject.DisplayMode = 'Flat Lines'
final.ViewObject.ShapeColor = (.25, .78, .88)
final.ViewObject.LineColor = (.12, .18, .2)
final.ViewObject.Deviation = .05
colors = []
for face in final.Shape.Faces:
    surface = face.Surface
    radius = getattr(surface, 'Radius', getattr(surface, 'MinorRadius', -1))
    is_finish = (type(surface).__name__ in ('Cylinder', 'Toroid')
                 and any(abs(radius-r.Value) < 1e-6 for r in
                         (final.TrayRootRadius, final.SocketRootRadius)))
    colors.append((1.0, .68, .18) if is_finish else (.25, .78, .88))
final.ViewObject.DiffuseColor = colors
Gui.Selection.clearSelection()
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
doc.save()
