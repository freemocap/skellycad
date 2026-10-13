"""FreeCAD GUI study: source-derived skull placement and eye-facing holder candidate."""
from pathlib import Path
import json,math
import FreeCAD as App,FreeCADGui as Gui,Part,Mesh
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-placement'
settings=json.loads((Path(__file__).parent/'settings.json').read_text());sources={}
for name,file in [('print_in_place_review2','print-test/r03/print-in-place-review.FCStd'),('r11b_carrier','rear-arm-r11/r11b-carrier.FCStd'),('tapered_baseplate','baseplate-taper/tapered-baseplate.FCStd')]:
 sources[name]=App.getDocument(name) if name in App.listDocuments() else App.openDocument(str(ROOT/'generated/mouse-hats'/file))
p=json.loads((OUT/'placement.json').read_text());hp=json.loads((ROOT/'generated/mouse-hats/print-test/r01/holder-pose.json').read_text())
doc=App.newDocument('SkullPlacementStudy');doc.Label='Skull + R11B — provisional placement and eye aim'
def shape(name,s,color):
 o=doc.addObject('Part::Feature',name);o.Shape=s.copy();o.ViewObject.ShapeColor=color;return o
def mesh(name,file,color):
 o=doc.addObject('Mesh::Feature',name);o.Mesh=Mesh.Mesh(str(OUT/file));o.ViewObject.ShapeColor=color;return o
sk=mesh('SkullReference','placed-reference-0.stl',(.82,.79,.67));sk.Label='Original skull surface — intersections present'
if (OUT/'placed-skull-repaired.stl').is_file():
 repaired=mesh('RepairedSkull','placed-skull-repaired.stl',(.82,.79,.67));repaired.Label='Repaired skull — 0.04 mm voxel candidate';sk.Visibility=False
for i in [1,2]:mesh('Eye'+str(i),f'placed-reference-{i}.stl',(.3,.65,.9))
connector=mesh('EyeConnector','placed-reference-3.stl',(.5,.5,.5));connector.Visibility=False
source=sources['print_in_place_review2']
carrier=shape('R11BCarrier',sources['r11b_carrier'].RibbonClearanceCarrier.Shape,(.2,.7,.8))
shape('TaperedBaseplate',sources['tapered_baseplate'].TaperedBaseplate.Shape,(.85,.65,.2))
cap=shape('Cap',source.CapReference.Shape,(.65,.65,.68));cap.Visibility=False
original=shape('OriginalHolder',source.Holder.Shape,(.55,.4,.75));original.Visibility=False
clip=shape('OriginalClip',source.ClipReference.Shape,(.85,.65,.2));clip.Visibility=False
ball=App.Vector(*hp['ball_center_mm'])
# Marked flat plate center: proxy for the lens center until sensor dimensions are provided.
local=App.Vector(*settings['lens_plate_center_local_mm'])
lens=source.Holder.Placement.multVec(local)
centers=[App.Vector(*e['assembly_center_mm']) for e in p['eyes']]
eye=min(centers,key=lambda v:(v-lens).Length);idx=centers.index(eye)
# Surface target facing the lens, not a claimed anatomical pupil landmark.
em=doc.getObject('Eye'+str(idx+1)).Mesh
direction=lens-eye;direction.normalize()
pts=[pt.Vector for pt in em.Points]
target=max(pts,key=lambda v:(v-eye).dot(direction))
axis=source.Holder.Placement.Rotation.multVec(App.Vector(0,0,-1))
if axis.dot(target-lens)<0:axis=-axis
rotation=App.Rotation()
for _ in range(60):
 current=ball+rotation.multVec(lens-ball);normal=rotation.multVec(axis)
 desired=target-current;desired.normalize()
 delta=App.Rotation(normal,desired);rotation=delta.multiply(rotation)
 if normal.getAngle(desired)<1e-10:break
transform=App.Placement(ball-rotation.multVec(ball),rotation)
aimed=source.Holder.Shape.copy();aimed.Placement=transform.multiply(aimed.Placement)
holder=shape('AimedHolderCandidate',aimed,(.62,.45,.8))
installed=source.ClipReference.Shape.copy();installed.Placement=transform.multiply(installed.Placement)
shape('AimedClipCandidate',installed,(.85,.65,.2))
newlens=transform.multVec(lens);newaxis=rotation.multVec(axis)
line=shape('OpticalAxisProxy',Part.makeLine(newlens,target),(1.,.15,.1));line.ViewObject.LineWidth=4;line.ViewObject.LineColor=(1.,.15,.1)
shape('LensCenterProxy',Part.makeSphere(.3,newlens),(1.,.2,.1))
shape('PupilAreaProxy',Part.makeSphere(.25,target),(1.,.7,.05))
normal=shape('MarkedPlateNormal',Part.makeLine(newlens,newlens+newaxis*5),(1.,.15,.1));normal.ViewObject.LineWidth=4;normal.ViewObject.LineColor=(1.,.15,.1)
overlap=aimed.common(carrier.Shape,.001)
if overlap.Volume>1e-6:shape('HolderCarrierInterference',overlap,(1.,.1,.1))
report=dict(units='mm and degrees',lens_local_proxy_mm=list(local),original_lens_assembly_mm=list(lens),aimed_lens_mm=list(newlens),target_mm=list(target),eye_center_mm=list(eye),target_note='Eye mesh support point toward original lens: provisional visible-surface target, NOT an identified pupil.',rotation_deg=rotation.Angle*180/math.pi,rotation_quaternion_xyzw=list(rotation.Q),holder_carrier_overlap_mm3=overlap.Volume,axis_target_error_deg=newaxis.getAngle(target-newlens)*180/math.pi,ball_center_mm=list(ball),scope='Pose study only; socket/arms unchanged; interference means socket reorientation/redesign required before adoption.')
(OUT/'aim-study.json').write_text(json.dumps(report,indent=2))
doc.recompute();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(OUT/'skull-placement-study.FCStd'))
print(json.dumps(report,indent=2))
