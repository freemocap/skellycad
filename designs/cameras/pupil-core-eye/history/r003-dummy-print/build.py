"""Preserve source camera dimensions with exclusive printable material regions."""
from pathlib import Path
import sys,json,hashlib,itertools
import FreeCAD as A, Part, MeshPart
ROOT=Path(__file__).resolve().parents[6]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'generated/eye-tracker/shared/camera-dummy-r03';OUT.mkdir(parents=True,exist_ok=True)
P=json.loads((HERE/'parameters.json').read_text())
for p,h in P['sources'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
sys.path.insert(0,str(HERE.parent/'study-r01'))
import camera_study as base
scene={o['name']:o for o in json.loads((HERE.parent/'study-r02/calibrated-scene.json').read_text())['objects']}
V=A.Vector; bt=P['board_thickness'];rt=P['ribbon_thickness']
def board(name):
 o=scene[name];return Part.Face(base.boundary(o['vertices'],o['triangles'])).extrude(V(0,0,bt))
def box_bounds(b,z,height):return Part.makeBox(b.XLength,b.YLength,height,V(b.XMin,b.YMin,z))
main=base.rigid_shape(scene['PCB'],(0,0,0));head=base.rigid_shape(scene['camera-pcb'],(0,0,0))
ribbon=base.ribbon_shape(32.85,4,.15,0)[0]
reference=base.rigid_shape(scene['M4-lens'],(0,0,0)).BoundBox
cx=(reference.XMin+reference.XMax)/2;cy=(reference.YMin+reference.YMax)/2
# User-measured external envelope; collar, bore and locating pegs are approximations.
# Morphology follows the user-selected CCOM photograph [@ccomMiniatureLensHolders].
lens=Part.makeBox(6.3,6.3,2.7,V(cx-3.15,cy-3.15,0))
collar=Part.makeCylinder(2.7,.2,V(cx,cy,2.7))
lens=lens.fuse(collar)
# Blind nominal 4 mm bore leaves a printable floor over the sensor.
lens=lens.cut(Part.makeCylinder(2,3,V(cx,cy,.35)))
for px,py in [(-2.6,-2.6),(2.6,2.6)]:
 lens=lens.fuse(Part.makeCylinder(.25,.2,V(cx+px,cy+py,-.2)))
lens=lens.removeSplitter()
assert abs(lens.BoundBox.XLength-6.3)<1e-8
assert abs(lens.BoundBox.ZMax-2.9)<1e-8
sel=json.loads((HERE.parent/'study-r03/connector-selection.json').read_text());connector=Part.Shape();connector.read(str(HERE.parent/sel['asset']))
old=base.rigid_shape(scene['JST-4pin'],(0,0,0)).BoundBox;b=connector.BoundBox
connector.translate(V((old.XMin+old.XMax-b.XMin-b.XMax)/2,old.YMin-b.YMin,0))
leds=[base.rigid_shape(scene[n],(0,0,0)) for n in ['IR-LED','IR-LED.001']]
# Preserve all exterior bounds; fill only the inherited 0.012396 mm gap beneath lens/LEDs.
for i,s in enumerate(leds):
 b=s.BoundBox;leds[i]=s.fuse(box_bounds(b,0,b.ZMin)).removeSplitter()
# Source rigid components and ribbon overlap at their material interfaces.
# Assign any shared volume to white, then black, then yellow for exclusive regions.
white=Part.makeCompound([connector]+leds)
lens=lens.cut(white).removeSplitter()
main=main.cut(white).cut(ribbon).removeSplitter();head=head.cut(white).cut(lens).cut(ribbon).removeSplitter()
parts={'Red_PLA_boards':Part.makeCompound([main,head]),'Black_PLA_lens':lens,'White_PLA_connector_LEDs':Part.makeCompound([connector]+leds),'Yellow_TPU_ribbon':ribbon.removeSplitter()}
colors=[(1,.12,.1),(.12,.12,.14),(.94,.94,.90),(1,.8,.02)]
# Shared print frame, all bed-contact surfaces at Z=0; preserve relative positions.
shift=V(0,31.283345794677736,.25)
d=A.newDocument('CameraDummyR03');d.Label='CAMERA DUMMY R03 - PLA boards / TPU ribbon'
report={'revision':P['revision'],'units':'mm','sources':P['sources'],'parameters':P,'parts':{},'overlaps_mm3':{},'physical_fit_verified':False,'stiffness_verified':False}
for name,sh in parts.items():
 assert sh.isValid() and all(s.Volume>0 for s in sh.Solids),name
for (an,a),(bn,b) in itertools.combinations(parts.items(),2):
 vol=a.common(b).Volume;assert vol<1e-7,(an,bn,vol);report['overlaps_mm3'][an+'/'+bn]=vol
whole=main.fuse(head).fuse(lens).fuse(connector)
for s in leds+[ribbon]:whole=whole.fuse(s)
assert len(whole.Solids)==1 and whole.isValid(),'Unconnected material regions'
assert abs(main.BoundBox.XLength-9)<1e-8 and abs(main.BoundBox.YLength-30.85)<1e-8
assert abs(head.BoundBox.XLength-6)<1e-8 and abs(head.BoundBox.YLength-15)<1e-8
assert abs(ribbon.common(Part.makeBox(4,32.85,2,V(-2,0,-1))).Volume-4*32.85*rt)<1e-7
for (name,sh),color in zip(parts.items(),colors):
 sh.translate(shift);o=d.addObject('PartDesign::Feature',name);o.Shape=sh
 o.addProperty('App::PropertyString','Material').Material='TPU' if 'TPU' in name else 'PLA'
 if A.GuiUp:o.ViewObject.ShapeColor=color
 mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
 assert mesh.isSolid();mesh.write(str(OUT/(name+'.stl')))
 report['parts'][name]={'solids':len(sh.Solids),'volume_mm3':sh.Volume,'mesh_closed':True,'triangles':mesh.CountFacets}
holder=d.getObject('Black_PLA_lens')
for key,value in [('SquareWidth',6.3),('CornerHeight',2.7),('RimHeight',2.9),('BoreDiameter',4.0),('CollarDiameter',5.4)]:
 holder.addProperty('App::PropertyLength',key,'Lens dimensions');setattr(holder,key,value)
holder.addProperty('App::PropertyString','GeometryNote').GeometryNote='Measured square and heights; approximate smooth bore, collar and diagonal locating pins; dummy only.'
# Standalone holder export in assembly coordinates.
holder.Shape.exportStep(str(OUT/'LENS-HOLDER-R01.step'))
d.recompute();d.saveAs(str(OUT/'CAMERA-DUMMY-R03.FCStd'))
Part.makeCompound(list(parts.values())).exportStep(str(OUT/'CAMERA-DUMMY-R03.step'))
report['passed']=True
(OUT/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
if A.GuiUp:
 import FreeCADGui as G
 G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui()
 G.activeDocument().activeView().saveImage(str(OUT/'preview.png'),1600,1000,'White')
print('CAMERA_DUMMY_GEOMETRY_OK',flush=True)
