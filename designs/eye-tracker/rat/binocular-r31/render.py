"""Render and save R31 in an isolated hidden GUI, then close its document."""
from pathlib import Path
import json,sys,zipfile,traceback,os,threading
import FreeCAD as A,FreeCADGui as G
from PySide import QtCore,QtWidgets
from PySide6 import QtTest
R=Path.cwd();S=R/'designs/eye-tracker/rat/binocular-r31';O=R/'generated/eye-tracker/rat/binocular-r31';G.showMainWindow();G.getMainWindow().hide();app=QtWidgets.QApplication.instance();app.setQuitOnLastWindowClosed(False);code=1

def run():
 global code
 try:
  d=A.openDocument(str(O/'ET-RAT-BINOCULAR-R31.FCStd'));A.setActiveDocument(d.Name)
  for o in d.Objects:
   o.Visibility=o.TypeId=='App::Part'
  for n in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea','FinishedCarrier','Baseplate']:
   o=d.getObject(n);o.Visibility=True
   if n=='RatDesignSkull':o.ViewObject.ShapeColor=(.85,.81,.65)
   elif n.endswith('Sclera'):o.ViewObject.ShapeColor=(.95,.95,.93)
   elif n.endswith('Cornea'):o.ViewObject.ShapeColor=(.1,.6,.85)
   else:o.ViewObject.ShapeColor=(.62,.66,.70)
  for side in ['Right','Left']:
   cam=d.getObject(side+'Camera')
   for ob,col in zip(cam.PhysicalParts,[(.9,.12,.1),(.12,.12,.14),(.94,.94,.9),(1.,.8,.02)]):ob.Visibility=True;ob.ViewObject.ShapeColor=col;ob.ViewObject.DisplayMode='Flat Lines' if 'boards' in ob.Name else 'Shaded'
   cam.OpticalAxis.Visibility=True;cam.OpticalAxis.ViewObject.LineColor=(0.,.65,.95);cam.OpticalAxis.ViewObject.LineWidth=3
   for name in ['eye_primary_Holder','eye_primary_Clip']:
    o=d.getObject(side+name);o.Visibility=True;o.ViewObject.ShapeColor=(.25,.48,.76) if side=='Right' else (.75,.42,.2)
  d.Label='Rat R31 - uncapped binocular review';d.recompute();G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui();d.save()
  def capture():
   global code
   try:
    v=G.activeDocument().activeView()
    for name,method in [('overview',v.viewAxonometric),('top',v.viewTop),('front',v.viewFront),('rear',v.viewRear)]:method();QtTest.QTest.qWait(700);v.fitAll();G.updateGui();v.saveImage(str(O/(name+'.png')),1600,1200,'White')
    v.viewAxonometric();v.fitAll();G.updateGui();d.save()
    with zipfile.ZipFile(d.FileName) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
    (O/'display-validation.json').write_text(json.dumps({'saved':True,'visible':[o.Name for o in d.Objects if o.Visibility],'views':['overview','top','front','rear']},indent=2));watchdog=threading.Timer(10,lambda:os._exit(0));watchdog.daemon=True;watchdog.start();A.closeDocument(d.Name);watchdog.cancel();code=0;print('REVIEW_SAVED_AND_CLOSED',flush=True)
   except Exception:traceback.print_exc()
   finally:os._exit(code)
  QtCore.QTimer.singleShot(1000,capture)
 except Exception:traceback.print_exc();app.quit()
QtCore.QTimer.singleShot(100,run);app.exec_();sys.exit(code)



