from pathlib import Path
import json
import FreeCAD as App, FreeCADGui as Gui, Mesh
from PySide import QtWidgets
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'generated/eye-tracker/rat/skull-print-r02'
Gui.showMainWindow();Gui.getMainWindow().hide()
doc=App.newDocument('RatSkullPrintR02');doc.Label='Rat skull R02 - preserved anatomy'
items=[('FusedSkullJaw','rat-skull-mandible-fused-r02.stl','PRINT - fused skull and mandible',True),('DetailedSkull','rat-skull-detailed-solid-r02.stl','PRINT - detailed solid skull only',False),('SeparateJaw','rat-mandible-original-detail-r02.stl','Optional separate jaw - original detail',False)]
for name,file,label,visible in items:
 obj=doc.addObject('Mesh::Feature',name);obj.Mesh=Mesh.Mesh(str(OUT/file));obj.Label=label;obj.ViewObject.ShapeColor=(.82,.77,.65);obj.ViewObject.Visibility=visible
obj=doc.addObject('Mesh::Feature','OriginalReference');obj.Mesh=Mesh.Mesh(str(ROOT/'designs/eye-tracker/rat/references/skull/aligned-r01/rat-skull-standard-aligned-r01.stl'));obj.Label='REFERENCE - original scan';obj.ViewObject.Visibility=False
obj=doc.addObject('Mesh::Feature','PreviousR01');obj.Mesh=Mesh.Mesh(str(ROOT/'generated/eye-tracker/rat/skull-print-r01/rat-skull-solid-r01.stl'));obj.Label='REFERENCE - smoothed R01';obj.ViewObject.Visibility=False
doc.recompute();QtWidgets.QApplication.instance().processEvents();doc.saveAs(str(OUT/'rat-skull-detailed-r02.FCStd'));App.closeDocument(doc.Name)
doc=App.openDocument(str(OUT/'rat-skull-detailed-r02.FCStd'))
report=json.loads((OUT/'validation.json').read_text())
for name,file,_,_ in items:assert doc.getObject(name).Mesh.CountFacets==report['outputs'][file[:-4]]['triangles']
App.closeDocument(doc.Name);print('Native comparison saved and reopened successfully')
