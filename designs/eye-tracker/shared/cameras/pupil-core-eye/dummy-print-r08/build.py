"""Preserve source camera dimensions with exclusive printable material regions."""
from pathlib import Path
import sys,json,hashlib,itertools
import FreeCAD as A, Part, MeshPart
ROOT=Path(__file__).resolve().parents[6]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'generated/eye-tracker/shared/camera-dummy-r08';OUT.mkdir(parents=True,exist_ok=True)
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
assert abs(rt-bt)<1e-9, 'Flush material boundaries require matching thicknesses'
ribbon=Part.makeBox(4,32.85,rt,V(-2,0,-bt))
for sh in [main,head,ribbon]:
 assert abs(sh.BoundBox.ZMin+bt)<1e-9 and abs(sh.BoundBox.ZMax)<1e-9
reference=base.rigid_shape(scene['M4-lens'],(0,0,0)).BoundBox
cx=(reference.XMin+reference.XMax)/2;cy=(reference.YMin+reference.YMax)/2
# Accepted protruding mock lens, retained unchanged above the mounting plane.
lens=Part.Shape();lens.read(str(ROOT/'designs/eye-tracker/shared/cameras/pupil-core-eye/checkpoints/CAMERA-DUMMY-R08/lens-source.step'))
local_center=V(0,0,(lens.BoundBox.ZMin+lens.BoundBox.ZMax)/2)
# Embedded locating pins stop at the PCB underside in the printable assembly.
lens=lens.common(Part.makeBox(20,20,20,V(-10,-10,-bt)))
lens.translate(V(cx,cy,0))
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
d=A.newDocument('CameraDummyR08');d.Label='CAMERA DUMMY R08 - PLA boards / TPU ribbon'
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
 sh.translate(shift);o=d.addObject('Part::Feature',name);o.Shape=sh
 o.addProperty('App::PropertyString','Material').Material='TPU' if 'TPU' in name else 'PLA'
 if A.GuiUp:o.ViewObject.ShapeColor=color
 mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
 assert mesh.isSolid();mesh.write(str(OUT/(name+'.stl')))
 report['parts'][name]={'solids':len(sh.Solids),'volume_mm3':sh.Volume,'mesh_closed':True,'triangles':mesh.CountFacets}
holder=d.getObject('Black_PLA_lens')
holder.addProperty('App::PropertyString','GeometryNote').GeometryNote='Accepted protruding M5-style dummy; embedded pins clipped at PCB underside.'
module=d.addObject('App::Part','CameraModule');module.Label='Complete camera module with optical datum'
for name in parts:module.addObject(d.getObject(name))
sensor=V(cx,cy,0)+shift
origin=V(cx,cy,local_center.z)+shift
axis=d.addObject('Part::Feature','OpticalAxis');module.addObject(axis)
axis.Label='Optical axis / sensor normal (+Z) - reference only'
axis.Shape=Part.makeCompound([Part.makeLine(origin,origin+V(0,0,14)),Part.makeLine(origin+V(0,0,14),origin+V(.55,0,12.8)),Part.makeLine(origin+V(0,0,14),origin+V(-.55,0,12.8))])
axis.addProperty('App::PropertyVector','Origin','Optical datum').Origin=origin
axis.addProperty('App::PropertyVector','Direction','Optical datum').Direction=V(0,0,1)
axis.addProperty('App::PropertyVector','SensorCenter','Optical datum').SensorCenter=sensor
axis.addProperty('App::PropertyLink','LensComponent','Optical datum').LensComponent=holder
axis.addProperty('App::PropertyBool','ExportForPrinting').ExportForPrinting=False
frame=d.addObject('App::FeaturePython','SensorFrame');module.addObject(frame)
frame.addProperty('App::PropertyPlacement','Placement').Placement=A.Placement(sensor,A.Rotation())
frame.addProperty('App::PropertyString','Definition').Definition='Hypothetical sensor center on PCB top; local +Z outward through lens, +X/+Y parallel to PCB. Not calibrated optical center.'
plane=d.addObject('Part::Feature','SensorPlane');module.addObject(plane)
plane.Shape=Part.Face(Part.makePolygon([sensor+V(-1.8,-1.8,0),sensor+V(1.8,-1.8,0),sensor+V(1.8,1.8,0),sensor+V(-1.8,1.8,0),sensor+V(-1.8,-1.8,0)]))
plane.addProperty('App::PropertyBool','ExportForPrinting').ExportForPrinting=False
assert (origin-sensor).cross(V(0,0,1)).Length<1e-9
assert plane.Shape.Faces[0].normalAt(0,0).dot(V(0,0,1))>.999999
report['optical_datum']={'origin_mm':list(origin),'sensor_center_mm':list(sensor),'direction':[0,0,1],'reference_only':True,'origin_definition':'Accepted lens bounding-box center on its symmetry axis','sensor_plane_definition':'PCB top at lens center; hypothetical sensor'}
(OUT/'optical-datum.json').write_text(json.dumps(report['optical_datum'],indent=2))
if A.GuiUp:
 axis.ViewObject.LineColor=(0,0.8,1);axis.ViewObject.LineWidth=3;plane.ViewObject.Visibility=False
d.recompute();d.saveAs(str(OUT/'CAMERA-DUMMY-R08.FCStd'))
Part.makeCompound(list(parts.values())).exportStep(str(OUT/'CAMERA-DUMMY-R08.step'))
report['flat_substrate']={'bottom_z_mm':0.0,'top_z_mm':bt,'ribbon_thickness_mm':rt,'coplanar_top_and_bottom':True}
report['passed']=True
(OUT/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
if A.GuiUp:
 import FreeCADGui as G
 G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui()
 G.activeDocument().activeView().saveImage(str(OUT/'preview.png'),1600,1000,'White')
print('CAMERA_DUMMY_GEOMETRY_OK',flush=True)