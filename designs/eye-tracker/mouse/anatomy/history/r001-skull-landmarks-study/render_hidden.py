from pathlib import Path
import json,hashlib,runpy,shutil,traceback
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtWidgets,QtCore
ROOT=Path.cwd();ST=ROOT/'designs/eye-tracker/mouse/skull-landmarks-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/skull-landmarks-study-r01'
Gui.showMainWindow();Gui.getMainWindow().hide();q=QtWidgets.QApplication.instance();q.setQuitOnLastWindowClosed(False)
def finish():
 try:
  d=App.ActiveDocument
  p=OUT/'ET-MOUSE-SKULL-LANDMARKS-STUDY-R01.FCStd';d.saveAs(str(p));dest=ST/'checkpoints'/p.name;shutil.copy2(p,dest)
  r=json.loads((ST/'native-validation.json').read_text());r['sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();r['hidden_gui_styles_saved']=True;r['desktop_visual_review_completed']=False;(ST/'native-validation.json').write_text(json.dumps(r,indent=2))
 except:traceback.print_exc()
 q.quit()
def start():
 runpy.run_path(str(ST/'open.FCMacro'));QtCore.QTimer.singleShot(1500,finish)
QtCore.QTimer.singleShot(0,start);q.exec_()
