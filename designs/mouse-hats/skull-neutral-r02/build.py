"""Create a self-contained R02 copy while preserving R01 and the selected R11B."""
from pathlib import Path
import json,sys
import FreeCAD as App,FreeCADGui as Gui,Part
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
HERE=Path(__file__).parent;OUT=ROOT/'generated/mouse-hats/skull-neutral-r02';OUT.mkdir(parents=True,exist_ok=True)
for p in [HERE,HERE.parent/'model',HERE.parent/'rear-arm-r11',HERE.parent/'skull-neutral-r01']:sys.path.insert(0,str(p))
import neutral_carrier_features
from neutral_r02_features import RibbonSpaceNeutral
from preserved_loop import geometry
source=ROOT/'generated/mouse-hats/skull-neutral-r01/neutral-joint-study.FCStd'
# Use a distinct file path to avoid sharing the existing R01 document in memory.
import shutil
target=OUT/'ribbon-space-study.FCStd';shutil.copyfile(source,target)
doc=App.openDocument(str(target));doc.Label='R02 — neutral eye aim with preserved R11B ribbon loop'
obj=doc.NeutralCarrier;obj.Proxy=RibbonSpaceNeutral.__new__(RibbonSpaceNeutral)
obj.Label='R02 carrier — original ribbon loop, extended tray connection'
obj.Shape=Part.Shape();obj.touch();doc.recompute()
assert 'Invalid' not in obj.State and not obj.Shape.isNull(), 'Carrier recompute failed; do not use cached geometry'
obj.Shape.check(True)
assert obj.Shape.isValid() and len(obj.Shape.Solids)==1
data=json.loads(obj.RearArm.DesignJSON);s=json.loads(obj.SweepJSON)
data['arm']['root_mm'][2]+=obj.RootForward.Value
data['arm']['root_mm'][1]=s['root_lower_y_mm']+s['root_width_mm']/2;data['arm']['root_width_mm']=s['root_width_mm']
data['socket_center_mm']=list(App.Vector(*data['socket_center_mm'])+obj.JointShift)
data.update(attachment_radius_mm=2.65,socket_lead_mm=1.,socket_width_mm=obj.SocketArmWidth.Value,socket_thickness_mm=obj.SocketArmThickness.Value)
s.update(attachment_angle_deg=obj.AttachmentAngle.Value,root_forward_mm=obj.RootForward.Value,outer_bulge_mm=obj.OuterBulge.Value,root_up_mm=obj.RootUp.Value,band_extra_mm=obj.BandExtra.Value)
arm,path,details,moved,extension=geometry(data,s,obj.ExtraDrop.Value,obj.JointShift)
for name,shape in [('PreservedRearLoop',moved),('TrayExtension',extension)]:
 o=doc.addObject('Part::Feature',name);o.Shape=shape;o.ViewObject.ShapeColor=(.2,.85,.4);o.Visibility=False
def overlap(a,b):return a.copy().common(b.copy(),.001).Volume
report=dict(units='mm and mm3',method=details,joint_shift_mm=list(obj.JointShift),carrier_valid=obj.Shape.isValid(),carrier_solids=len(obj.Shape.Solids),carrier_volume_mm3=obj.Shape.Volume,holder_overlap_mm3=overlap(obj.Shape,doc.CenteredHolder.Shape),holder_gap_mm=obj.Shape.distToShape(doc.CenteredHolder.Shape)[0],clip_overlap_mm3=overlap(obj.Shape,doc.CenteredClip.Shape),baseplate_overlap_mm3=overlap(obj.Shape,doc.TaperedBaseplate.Shape),cap_overlap_mm3=overlap(obj.Shape,doc.CapReference.Shape),optical_obstruction_mm=doc.OpticalAxis.Shape.common(obj.Shape,.001).Length,original_loop_rigidly_translated=True,loop_holder_gap_mm=moved.distToShape(doc.CenteredHolder.Shape)[0],extension_holder_gap_mm=extension.distToShape(doc.CenteredHolder.Shape)[0])
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
settings=dict(units='mm',source='R01 neutral joint pose and R11B rear loop',joint_shift_mm=list(obj.JointShift),root_connection_overlap_mm=.1,root_connection_sections=17,root_connection_loft_degree=3,ribbon_loop_shape='R11B rigid translation; no compression or scaling',ribbon_dimensions='Not supplied; geometric envelope preservation, no physical cable fit claim')
(HERE/'settings.json').write_text(json.dumps(settings,indent=2))
obj.ViewObject.ShapeColor=(.2,.75,.8);obj.Visibility=True
doc.recompute();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll();doc.save()
print(json.dumps(report,indent=2))

