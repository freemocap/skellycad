"""Translate the joint to align the centered holder normal with the existing eye target."""
from pathlib import Path
import sys,json,math
import FreeCAD as App,FreeCADGui as Gui,Part,Mesh
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
HERE=Path(__file__).parent;OUT=ROOT/'generated/mouse-hats/skull-neutral-r01';OUT.mkdir(parents=True,exist_ok=True)
for p in [HERE,HERE.parent/'model',HERE.parent/'rear-arm-r11']:sys.path.insert(0,str(p))
from neutral_carrier_features import RearwardNeutral
src=App.getDocument('r11b_carrier');old=src.RibbonClearanceCarrier
ref=App.getDocument('print_in_place_review2')
sp=HERE.parent/'skull-placement'
aim=json.loads((sp/'aim-study.json').read_text());placement=json.loads((sp/'placement.json').read_text())
hp=json.loads((ROOT/'generated/mouse-hats/print-test/r01/holder-pose.json').read_text())
hparams=json.loads((HERE.parent/'reconstruction/camera_holder/parameters.json').read_text())
axis=App.Vector(*json.loads(src.RearArm.DesignJSON)['socket_axis'])
neck=ref.Holder.Placement.Rotation.multVec(App.Vector(*hparams['neck_axis_up']))
q=App.Rotation(neck,axis);ball=App.Vector(*hp['ball_center_mm']);lens=App.Vector(*aim['original_lens_assembly_mm'])
centered_lens=ball+q.multVec(lens-ball)
optical=q.multVec(ref.Holder.Placement.Rotation.multVec(App.Vector(0,0,-1)))
target=App.Vector(*aim['target_mm'])
shift=target-centered_lens-optical*(target-centered_lens).dot(optical)
posterior=App.Vector(*placement['stl_to_assembly']['rotation_row_vector'][0])
projected_posterior=posterior-optical*posterior.dot(optical)
posterior_only=shift.dot(projected_posterior)/projected_posterior.dot(projected_posterior)
settings=dict(units='mm and degrees',joint_shift_assembly_mm=list(shift),posterior_axis_assembly=list(posterior),posterior_only_best_shift_mm=posterior_only,posterior_only_miss_mm=(shift-projected_posterior*posterior_only).Length,target_mm=list(target),lens_local_mm=json.loads((sp/'settings.json').read_text())['lens_plate_center_local_mm'],neutral_correction_deg=q.Angle*180/math.pi,neutral_definition='Holder neck axis parallel to socket axis; preserve accepted ball center and radius clearance. Plate normal differs from neck axis by 0.007 degrees.',target_note=aim['target_note'])
(HERE/'settings.json').write_text(json.dumps(settings,indent=2))
doc=App.newDocument('SkullNeutralR01');doc.Label='R01 — posterior joint / centered holder aimed at eye'
def snap(name,shape,color=(.55,.55,.55),visible=False):
 o=doc.addObject('Part::Feature',name);o.Shape=shape.copy();o.ViewObject.ShapeColor=color;o.Visibility=visible;return o
for name,source in [('JunctionFillets',src.JunctionFillets),('Base',old.Base),('Tray',old.Tray),('Socket',old.Socket)]:snap(name,source.Shape)
for name,source in [('RearArm',old.RearArm),('TopArm',old.TopArm)]:
 o=snap(name,source.Shape);o.addProperty('App::PropertyString','DesignJSON');o.DesignJSON=source.DesignJSON
obj=doc.addObject('Part::FeaturePython','NeutralCarrier')
r03=json.loads((HERE.parent/'print-test-r03/settings.json').read_text())
RearwardNeutral(obj,doc.Base,doc.Tray,doc.Socket,doc.RearArm,doc.TopArm,r03,list(ball))
for prop in ['SweepJSON','ExtraDrop','AttachmentAngle','RootForward','RootUp','OuterBulge','BandExtra']:
 setattr(obj,prop,getattr(old,prop))
obj.JointShift=shift;obj.ViewObject.Proxy=0;obj.ViewObject.ShapeColor=(.2,.75,.8)
doc.recompute()
if obj.Shape.isNull():raise RuntimeError('Carrier build failed; inspect report before use')
transform=App.Placement(ball+shift-q.multVec(ball),q)
hs=ref.Holder.Shape.copy();hs.Placement=transform.multiply(hs.Placement)
holder=snap('CenteredHolder',hs,(.62,.45,.8),True)
cs=ref.ClipReference.Shape.copy();cs.Placement=transform.multiply(cs.Placement)
snap('CenteredClip',cs,(.85,.65,.2),True)
snap('OriginalR11BCarrier',old.Shape,(.55,.55,.55))
snap('OriginalHolder',ref.Holder.Shape,(.55,.55,.55))
snap('TaperedBaseplate',App.getDocument('tapered_baseplate').TaperedBaseplate.Shape,(.85,.65,.2),True)
snap('CapReference',ref.CapReference.Shape)
for name,file,color in [('Skull','placed-skull-repaired.stl',(.82,.79,.67)),('Eye1','placed-reference-1.stl',(.3,.65,.9)),('Eye2','placed-reference-2.stl',(.3,.65,.9))]:
 o=doc.addObject('Mesh::Feature',name);o.Mesh=Mesh.Mesh(str(ROOT/'generated/mouse-hats/skull-placement'/file));o.ViewObject.ShapeColor=color
new_lens=centered_lens+shift
line=snap('OpticalAxis',Part.makeLine(new_lens,target),(1.,.1,.1),True);line.ViewObject.LineColor=(1.,.1,.1);line.ViewObject.LineWidth=4
snap('LensDatum',Part.makeSphere(.25,new_lens),(1.,.2,.1),True)
snap('EyeTarget',Part.makeSphere(.25,target),(1.,.7,.05),True)
for name in ['CenteredHolder','CenteredClip','LensDatum','OpticalAxis']:
 o=doc.getObject(name)
 for i,axis_name in enumerate('xyz'):
  offset=o.Placement.Base[i]-shift[i]
  o.setExpression('Placement.Base.'+axis_name,f'NeutralCarrier.JointShift.{axis_name} + ({offset:.17g})')
doc.recompute();obj.Shape.check(True)
def common(a,b):return a.copy().common(b.copy(),.001).Volume
report=dict(settings,valid=obj.Shape.isValid(),solids=len(obj.Shape.Solids),carrier_volume_mm3=obj.Shape.Volume,holder_overlap_mm3=common(obj.Shape,hs),holder_gap_mm=obj.Shape.distToShape(hs)[0],clip_overlap_mm3=common(obj.Shape,cs),baseplate_overlap_mm3=common(obj.Shape,doc.TaperedBaseplate.Shape),cap_overlap_mm3=common(obj.Shape,doc.CapReference.Shape),aim_error_deg=optical.getAngle(target-new_lens)*180/math.pi,neck_socket_angle_deg=q.multVec(neck).getAngle(axis)*180/math.pi)
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
doc.recompute();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll();doc.saveAs(str(OUT/'neutral-joint-study.FCStd'))
print(json.dumps(report,indent=2))
