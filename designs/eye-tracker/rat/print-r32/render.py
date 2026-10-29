"""Save native print reviews and render previews in an isolated GUI."""
from pathlib import Path
import json,zipfile,os,traceback
import FreeCAD as A,FreeCADGui as G,Mesh
from PySide import QtCore,QtWidgets
from PySide6 import QtTest
R=Path.cwd();O=R/'generated/eye-tracker/rat/print-r32';G.showMainWindow();G.getMainWindow().hide();app=QtWidgets.QApplication.instance();app.setQuitOnLastWindowClosed(False)
def verify(path):
 with zipfile.ZipFile(path) as z:assert 'Document.xml' in z.namelist() and z.testzip() is None
def run():
 try:
  anatomy=A.newDocument('RAT_R32_anatomy_print');anatomy.Label='RAT R32 - U1 four-color skull with lowered baseplate'
  for name,col in [('Skull-and-bridge',(1.,.05,.05)),('Sclera',(.97,.97,.97)),('Cornea',(.1,.1,.1)),('Baseplate',(1.,.85,.02))]:
   ob=anatomy.addObject('Mesh::Feature',name.replace('-','_'));ob.Label=name;ob.Mesh=Mesh.Mesh(str(O/'anatomy'/(name+'.stl')));ob.ViewObject.ShapeColor=col
  # Mesh shaded display avoids distracting triangulation edges.
  for ob in anatomy.Objects:
   if 'Flat Lines' in ob.ViewObject.listDisplayModes():ob.ViewObject.DisplayMode='Flat Lines'
   if 'Flat Lines' in ob.ViewObject.listDisplayModes() and 'Shaded' in ob.ViewObject.listDisplayModes():ob.ViewObject.DisplayMode='Shaded'
  A.setActiveDocument(anatomy.Name);anatomy.recompute();v=G.activeDocument().activeView();v.viewAxonometric();QtTest.QTest.qWait(700);v.fitAll();G.updateGui();p=O/'RAT-R32-anatomy-print.FCStd';anatomy.saveAs(str(p));verify(p);v.saveImage(str(O/'anatomy-preview.png'),1400,1100,'White')
  hardware=A.openDocument(str(O/'RAT-R32-hardware-print.FCStd'));A.setActiveDocument(hardware.Name)
  for ob in hardware.Objects:ob.ViewObject.ShapeColor=(.60,.65,.70) if ob.Name=='CarrierAndTwoHolders' else (.95,.65,.15);ob.ViewObject.DisplayMode='Flat Lines';ob.Visibility=True
  hardware.recompute();v=G.activeDocument().activeView();v.viewAxonometric();QtTest.QTest.qWait(700);v.fitAll();G.updateGui();hardware.save();verify(hardware.FileName);v.saveImage(str(O/'hardware-preview.png'),1600,1100,'White')
  (O/'preview-validation.json').write_text(json.dumps({'native_files_verified':True,'anatomy_materials':4,'hardware_print_shells':5,'isolated_session':True},indent=2))
  # The process owns only these saved review documents; exit closes this isolated session.
  os._exit(0)
 except Exception:traceback.print_exc();os._exit(1)
QtCore.QTimer.singleShot(100,run);app.exec()


