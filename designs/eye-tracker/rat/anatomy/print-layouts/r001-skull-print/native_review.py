from pathlib import Path
import FreeCAD as App, FreeCADGui as Gui, Mesh
from PySide import QtWidgets
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'generated/eye-tracker/rat/skull-print-r01'
Gui.showMainWindow();Gui.getMainWindow().hide()
doc=App.newDocument('RatSkullPrintR01');doc.Label='Rat skull - solid braincase R01'
for name,filename in [('SolidSkull','rat-skull-solid-r01.stl'),('SeparateJaw','rat-mandible-clean-r01.stl')]:
 obj=doc.addObject('Mesh::Feature',name);obj.Mesh=Mesh.Mesh(str(OUT/filename));obj.ViewObject.ShapeColor=(.82,.77,.65);obj.ViewObject.LineColor=(.2,.2,.2)
 obj.Label='Solid braincase - print skull' if name=='SolidSkull' else 'Clean jaw - separate print'
 obj.ViewObject.Visibility=name=='SolidSkull'
doc.recompute();QtWidgets.QApplication.instance().processEvents()
doc.saveAs(str(OUT/'rat-skull-solid-r01.FCStd'))
App.closeDocument(doc.Name)
check=App.openDocument(str(OUT/'rat-skull-solid-r01.FCStd'))
assert check.SolidSkull.Mesh.CountFacets==116044
assert check.SeparateJaw.Mesh.CountFacets==33868
print('Native review saved and reopened successfully')
App.closeDocument(check.Name)

