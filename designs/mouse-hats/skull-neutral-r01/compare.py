"""Side-by-side saved snapshots of tilted R11B and translated neutral candidate."""
from pathlib import Path
import json
import FreeCAD as App,FreeCADGui as Gui,Part
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-neutral-r01'
source=next(d for d in App.listDocuments().values() if Path(d.FileName).name=='neutral-joint-study.FCStd')
oldref=App.getDocument('print_in_place_review2')
aim=json.loads((ROOT/'designs/mouse-hats/skull-placement/aim-study.json').read_text())
ball=App.Vector(*aim['ball_center_mm']);rotation=App.Rotation(*aim['rotation_quaternion_xyzw'])
oldpose=App.Placement(ball-rotation.multVec(ball),rotation)
view=Gui.activeDocument().activeView().getCameraOrientation();right=view.multVec(App.Vector(1,0,0));up=view.multVec(App.Vector(0,1,0))
doc=App.newDocument('NeutralJointComparison');doc.Label='Before / after — tilted holder vs posterior neutral joint'
for prefix,offset in [('Before',right*-28),('After',right*28)]:
 def addshape(name,s,color):
  o=doc.addObject('Part::Feature',prefix+name);o.Shape=s.copy();o.Placement.Base+=offset;o.ViewObject.ShapeColor=color;return o
 for name in ['Skull','Eye1','Eye2']:
  src=source.getObject(name);o=doc.addObject('Mesh::Feature',prefix+name);o.Mesh=src.Mesh.copy();o.Placement.Base+=offset;o.ViewObject.ShapeColor=src.ViewObject.ShapeColor
 addshape('Baseplate',source.TaperedBaseplate.Shape,(.85,.65,.2))
 if prefix=='Before':
  addshape('Carrier',source.OriginalR11BCarrier.Shape,(.5,.57,.6))
  for name in ['Holder','ClipReference']:
   s=oldref.getObject(name).Shape.copy();s.Placement=oldpose.multiply(s.Placement)
   addshape(name,s,(.6,.45,.75) if name=='Holder' else (.85,.65,.2))
  line=Part.makeLine(App.Vector(*aim['aimed_lens_mm']),App.Vector(*aim['target_mm']))
 else:
  for name in ['NeutralCarrier','CenteredHolder','CenteredClip']:
   src=source.getObject(name);addshape(name,src.Shape,src.ViewObject.ShapeColor)
  line=source.OpticalAxis.Shape
 o=addshape('Aim',line,(1.,.15,.1));o.ViewObject.LineColor=(1.,.15,.1);o.ViewObject.LineWidth=3
 label=doc.addObject('App::Annotation',prefix+'Label')
 label.LabelText=['BEFORE: holder tilted 20 deg' if prefix=='Before' else 'AFTER: joint rearward, holder centered']
 label.Position=App.Vector(4,3,7)+offset+up*34-right*19
 label.ViewObject.TextColor=(.95,.95,.95);label.ViewObject.FontSize=14
doc.recompute();Gui.activeDocument().activeView().setCameraOrientation(view.Q);Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(OUT/'before-after.FCStd'))
Gui.activeDocument().activeView().saveImage(str(OUT/'before-after.png'),1500,1000,'Current')
