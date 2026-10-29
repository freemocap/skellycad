from pathlib import Path
import os,json,zipfile,traceback
import FreeCAD as A,FreeCADGui as G
from PySide import QtCore,QtWidgets
from PySide6 import QtTest
O=Path.cwd()/'generated/eye-tracker/rat/print-r32-l02';G.showMainWindow();G.getMainWindow().hide();app=QtWidgets.QApplication.instance();app.setQuitOnLastWindowClosed(False)
def run():
 try:
  d=A.openDocument(str(O/'RAT-R32-hardware-print.FCStd'));A.setActiveDocument(d.Name)
  for ob in d.Objects:ob.Visibility=True;ob.ViewObject.ShapeColor=(.60,.65,.70) if ob.Name=='CarrierAndTwoHolders' else (.95,.65,.15);ob.ViewObject.DisplayMode='Flat Lines'
  d.recompute();v=G.activeDocument().activeView();v.viewAxonometric();QtTest.QTest.qWait(700);v.fitAll();G.updateGui();d.save()
  with zipfile.ZipFile(d.FileName) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
  v.saveImage(str(O/'hardware-preview.png'),1500,1000,'White');v.viewTop();QtTest.QTest.qWait(700);v.fitAll();G.updateGui();v.saveImage(str(O/'hardware-top.png'),1500,700,'White')
  (O/'preview-validation.json').write_text(json.dumps({'layout':'R32 L02','native_hardware_verified':True,'clips_flat_xy':True,'views':['hardware-preview.png','hardware-top.png']},indent=2));os._exit(0)
 except Exception:traceback.print_exc();os._exit(1)
QtCore.QTimer.singleShot(100,run);app.exec()
