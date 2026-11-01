"""Register measured camera rigid ends to accepted mouse hardware; inspect fit."""
from pathlib import Path
import sys,json,hashlib,shutil,math
import FreeCAD as A,Part
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CAM=ROOT/'designs/eye-tracker/shared/cameras/pupil-core-eye'
sys.path.insert(0,str(CAM/'study-r01'))
import camera_study as c
OUT=ROOT/'generated/eye-tracker/mouse/camera-fit-r01'
V=A.Vector

def build():
 OUT.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((HERE.parent/'active-model.json').read_text())
 checkpoint=ROOT/manifest['native_checkpoint']
 assert hashlib.sha256(checkpoint.read_bytes()).hexdigest()==manifest['native_sha256']
 target=OUT/'mouse-camera-fit-r01.FCStd';shutil.copyfile(checkpoint,target)
 doc=A.openDocument(str(target));doc.Label='Mouse camera fit R01 - measured sensor + JST SH'
 holder=doc.getObject('eye_primary_Holder');clip=doc.getObject('eye_primary_Clip')
 scene={o['name']:o for o in json.loads((CAM/'study-r02/calibrated-scene.json').read_text())['objects']}
 # Holder's native frame: width X, PCB length Y, board lies below the plate at Z=2.
 sensor_pose=holder.Placement.multiply(A.Placement(V(4.38695887,-12.75,1.7495863743117823),A.Rotation(V(0,1,0),180)))
 # Main PCB backside at the old seat X=5.287...; slide 0.35 mm down from
 # bottom-aligned first trial to clear both upper and lower retainers.
 rotation=A.Rotation(V(0,1,0),V(0,0,1),V(1,0,0),'ZXY')
 main_pose=A.Placement(V(5.53706399647303,12.78,16.5),rotation)
 main=doc.addObject('App::Part','MeasuredMainPCB');main.Label='Measured main PCB + provisional JST SH';main.Placement=main_pose
 head=doc.addObject('App::Part','MeasuredSensorHead');head.Label='Measured sensor PCB - notch aligned to clip';head.Placement=sensor_pose
 objects=[]
 for name,item in scene.items():
  if name=='ribbon':continue
  ismain=name in ('PCB','JST-4pin')
  sh=c.rigid_shape(item,[0,0,0] if ismain else [0,32.85,0])
  if name=='JST-4pin':
   selection=json.loads((CAM/'study-r03/connector-selection.json').read_text());p=CAM/selection['asset']
   assert hashlib.sha256(p.read_bytes()).hexdigest()==selection['sha256']
   old=sh.BoundBox;sh=Part.Shape();sh.read(str(p));b=sh.BoundBox
   sh.translate(V((old.XMin+old.XMax-b.XMin-b.XMax)/2,old.YMin-b.YMin,0))
  color=(.13,.5,.24) if name in ('PCB','camera-pcb') else (.9,.87,.75) if name=='JST-4pin' else (.15,.17,.20) if name=='M4-lens' else (.75,.15,.2)
  o=c.add_shape(doc,main if ismain else head,name,sh,color);objects.append(o)
 # Show the same nominal M4 guide as R03 without asserting a stock holder identity.
 lens=next(o for o in objects if o.SourceName=='M4-lens');b=lens.Shape.BoundBox
 c.add_shape(doc,head,'M4 nominal reference',Part.makeCylinder(2,.15,V((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,b.ZMax)),(.3,.4,.55))
 # The previous cubic crossed the carrier and is rejected. Do not recreate it.
 # A replacement needs material-metric and full-solid collision validation.
 start,end=main_pose.Base,sensor_pose.Base
 for n in ['eye_primary_ApproxPCB','eye_primary_LensDatum','eye_primary_OpticalAxis','eye_primary_UpperCatch','eye_primary_UpperRail','eye_primary_SideLedge']:
  if A.GuiUp:doc.getObject(n).Visibility=False
 doc.recompute()
 hardware={key:doc.getObject(name) for key,name in manifest['parts'].items()}
 rows=[]
 for obj in objects:
  sh=obj.Shape.copy();sh.Placement=obj.getGlobalPlacement()
  for name,hw in hardware.items():
   overlap=sh.common(hw.Shape).Volume
   rows.append({'component':obj.SourceName,'hardware':name,'overlap_mm3':overlap,'distance_mm':sh.distToShape(hw.Shape)[0]})
 collisions=[v for v in rows if v['overlap_mm3']>1e-6]
 board=next(o for o in objects if o.SourceName=='camera-pcb');boardshape=board.Shape.copy();boardshape.Placement=board.getGlobalPlacement()
 report={'source_checkpoint':manifest['native_checkpoint'],'source_sha256':manifest['native_sha256'],'units':'mm and mm3','head_pose':{'translation':list(sensor_pose.Base),'quaternion_xyzw':list(sensor_pose.Rotation.Q)},'main_pose':{'translation':list(main_pose.Base),'quaternion_xyzw':list(main_pose.Rotation.Q)},'sensor_side_clearance_mm':.1,'sensor_front_to_clip_gap_mm':1.7495863743117823-1.5,'sensor_back_on_tray':boardshape.distToShape(holder.Shape)[0]<1e-6,'ribbon_status':'unresolved; rejected cubic removed','endpoint_distance_mm':(end-start).Length,'checks':rows,'collisions':collisions,'limitations':'Assumed board thickness 0.25 mm. Static seated pose does not prove clip insertion, grip or physical fit. No ribbon is displayed until a replacement passes validation. The user has demonstrated physical fit; routing failures concern this model.'}
 (OUT/'fit-report.json').write_text(json.dumps(report,indent=2))
 if A.GuiUp:
  for o in hardware.values():o.Visibility=True
  clip.ViewObject.Transparency=65
  import FreeCADGui as G
  G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui()
  G.activeDocument().activeView().saveImage(str(OUT/'assembly.png'),1400,1000,'White')
 doc.recompute();doc.save()
 print(json.dumps({'collisions':collisions,'ribbon_status':'unresolved; rejected cubic removed','ribbon_displayed':False},indent=2))
 return doc
if __name__=='__main__':build()
