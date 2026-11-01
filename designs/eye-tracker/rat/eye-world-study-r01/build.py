"""Independent, non-printable eye/world placement studies from frozen R43."""
from pathlib import Path
import sys, json, hashlib, zipfile
import numpy as np
import FreeCAD as A, Part, Mesh, FreeCADGui as G
from PySide import QtWidgets, QtCore
from pivy import coin

R=Path(__file__).resolve().parents[4]
S=Path(__file__).resolve().parent
O=R/'generated/eye-tracker/rat/eye-world-study-r01'
O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker'))
from shared.camera import add_camera
src=json.loads((S.parent/'lowered-cameras-r43/review.json').read_text())
source=R/src['native_checkpoint']
assert hashlib.sha256(source.read_bytes()).hexdigest()==src['native_sha256']
cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text())
T=np.array(cfg['mount_to_skull']); old=np.array(cfg['sides']['Left']['head'])
ll=np.array([.08845911870242962,5.719524249669308,1.607691279838762])
def matrix(t):return A.Matrix(*np.asarray(t).ravel().tolist())
def move(s,t):return s.transformed(matrix(t))
def world(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
def asset(n):
 s=Part.Shape();s.read(str(source.parent/(n+'.brep')));return s
if hasattr(G,'showMainWindow'): G.showMainWindow()
G.getMainWindow().hide()
def build():
 report={'units':'mm','source':{k:src[k] for k in ['revision','native_checkpoint','native_sha256']},'purpose':'Placement and suspension concepts only; no printable hardware or solved world ribbon','candidates':[]}
 for name,y in [('A-centered',0.),('B-offset',10.)]:
  d=A.openDocument(str(source));d.Label='RAT eye + world '+name+' - CONCEPT ONLY'
  for o in d.Objects:o.Visibility=o.TypeId=='App::Part'
  for n in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea','Baseplate','Righteye_primary_Holder','Righteye_primary_Clip']:d.getObject(n).Visibility=True
  def feature(n,sh,color):
   o=d.addObject('Part::Feature',n);o.Shape=sh;o.ViewObject.ShapeColor=color;o.Visibility=True
   o.addProperty('App::PropertyBool','PrintReady').PrintReady=False
   return o
  # Preserve the eye-side finished junctions; remove the converted side's supports.
  trimmed=world(d.FinishedCarrier).cut(Part.makeBox(150,100,150,A.Vector(-60,0,-60))).fuse(world(d.CentralCarrier)).removeSplitter()
  assert trimmed.isValid()
  feature('ConceptCarrier',trimmed,(.65,.68,.72))
  for o in d.RightCamera.PhysicalParts:o.Visibility=True
  d.RightCamera.OpticalAxis.Visibility=True
  # Keep the selected complete camera and its optical datum together, then adapt
  # the two rigid boards separately. Yellow wire is a route hypothesis, not ribbon.
  cam=add_camera(d,name='WorldCamera')
  H=np.eye(4);H[:3,:3]=np.array([[0,0,1],[1,0,0],[0,1,0]])
  lens=np.array([12.,y,12.]);H[:3,3]=lens-H[:3,:3]@ll
  D=H@np.linalg.inv(old)
  shapes={n:move(asset('Left'+n),T if n in ['PCB','JST_4pin'] else D) for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']}
  cam.PhysicalParts[0].Shape=Part.makeCompound([shapes['PCB'],shapes['camera_pcb']])
  cam.PhysicalParts[1].Shape=shapes['M4_lens']
  cam.PhysicalParts[2].Shape=Part.makeCompound([shapes[n] for n in ['JST_4pin','IR_LED','IR_LED_001']])
  cam.PhysicalParts[3].Visibility=False
  cam.OpticalAxis.Origin=A.Vector(*lens);cam.OpticalAxis.Direction=A.Vector(1,0,0)
  sensor=(D@np.r_[np.array(list(d.LeftCamera.OpticalAxis.SensorCenter)),1])[:3]
  cam.OpticalAxis.SensorCenter=A.Vector(*sensor)
  cam.SensorFrame.Placement=A.Placement(A.Vector(*sensor),A.Rotation(matrix(H)))
  cam.OpticalAxis.Shape=Part.makeLine(A.Vector(*lens),A.Vector(*(lens+[18,0,0])))
  cam.OpticalAxis.ViewObject.LineColor=(0.,.7,.9)
  # Deliberately simple top stem and vertical socket envelopes, not mating parts.
  bb=shapes['camera_pcb'].BoundBox
  tray=Part.makeBox(1.2,bb.YLength+1.2,bb.ZLength+1.2,A.Vector(bb.XMin-1.3,bb.YMin-.6,bb.ZMin-.6))
  top=bb.ZMax+.6; sx=bb.XMin-.7
  stem=Part.makeCylinder(1.1,3.,A.Vector(sx,y,top))
  ball=Part.makeSphere(2.,A.Vector(sx,y,top+3.))
  feature('WorldTrayAndTopStemEnvelope',tray.fuse(stem).fuse(ball),(.25,.48,.76))
  socket=Part.makeCylinder(3.2,4.,A.Vector(sx,y,top+1.5)).cut(Part.makeCylinder(2.2,4.,A.Vector(sx,y,top+1.5)))
  feature('VerticalSocketEnvelope',socket,(.8,.45,.17))
  # Proposed attachment directions are reference wires pending route approval.
  roof=top+4.
  bridge=feature('SocketSupportDirections',Part.makeCompound([Part.makeLine(A.Vector(4,y-3,19),A.Vector(sx,y-2.8,roof)),Part.makeLine(A.Vector(4,y+3,19),A.Vector(sx,y+2.8,roof))]),(.8,.45,.17))
  bridge.ViewObject.LineColor=(.8,.45,.17);bridge.ViewObject.LineWidth=4
  start=(T@np.array(cfg['sides']['Left']['board_transform'])@np.array([0,0,0,1]))[:3]
  # Actual sensor ribbon entry is head origin; main exit from retained ribbon.
  import importlib.util
  sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
  import ribbon_geometry as rg
  start=(T@np.array(cfg['sides']['Left']['board_transform'])@np.r_[rg.BASE,1])[:3]
  end=H[:3,3]
  pts=[start,np.array([start[0],start[1]+6,start[2]]),np.array([9,start[1]+6,9]),np.array([9,y,8]),end]
  curve=Part.BSplineCurve();curve.interpolate([A.Vector(*p) for p in pts])
  wire=feature('RibbonRouteHypothesis',curve.toShape(),(1.,.7,0.))
  wire.ViewObject.LineColor=(1.,.65,0.);wire.ViewObject.LineWidth=4
  wire.Label='Ribbon route idea ONLY - length, folds and clearance unsolved'
  # Hide old left module and all its descendants, including its solved eye ribbon.
  d.LeftCamera.Visibility=False
  for o in d.LeftCamera.Group:o.Visibility=False
  d.recompute();p=O/(name+'.FCStd');d.saveAs(str(p))
  with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
  v=G.activeDocument().activeView();v.viewAxonometric();v.fitAll();v.getCameraNode().nearDistance.setValue(.01);v.getCameraNode().farDistance.setValue(10000)
  G.updateGui();QtWidgets.QApplication.processEvents();v.saveImage(str(O/(name+'.png')),1400,1050,'White')
  v.viewTop();v.fitAll();G.updateGui();v.saveImage(str(O/(name+'-top.png')),1400,1050,'White');v.viewAxonometric();v.fitAll();d.save()
  report['candidates'].append({'id':name,'lens_world_mm':lens.tolist(),'axis_world':[1,0,0],'socket_axis_world':[0,0,1],'native':str(p.relative_to(R)),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'ribbon_guide_length_mm':wire.Shape.Length,'ribbon_stock_length_mm':32.85,'ribbon_solved':False,'arm_seating_validated':False,'anatomy_clearance_validated':False,'physical_fit_verified':False})
  A.closeDocument(d.Name)
 (O/'study.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))

def run():
 try:build()
 except Exception:
  import traceback
  traceback.print_exc()
 finally:
  for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
  QtWidgets.QApplication.instance().quit()
if __name__ == '__main__':
 QtCore.QTimer.singleShot(500,run)
 QtWidgets.QApplication.instance().exec_()

