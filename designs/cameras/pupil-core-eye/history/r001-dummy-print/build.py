"""Build a four-material camera surrogate with captured TPU end tabs."""
from pathlib import Path
import sys,json,hashlib,itertools
import FreeCAD as A, Part, MeshPart
ROOT=Path(__file__).resolve().parents[6]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'generated/eye-tracker/shared/camera-dummy-r01';OUT.mkdir(parents=True,exist_ok=True)
P=json.loads((HERE/'parameters.json').read_text())
for p,h in P['sources'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
sys.path.insert(0,str(HERE.parent/'study-r01'))
import camera_study as base
scene={o['name']:o for o in json.loads((HERE.parent/'study-r02/calibrated-scene.json').read_text())['objects']}
V=A.Vector; bt=P['board_thickness'];rt=P['ribbon_thickness']
def board(name):
 o=scene[name];return Part.Face(base.boundary(o['vertices'],o['triangles'])).extrude(V(0,0,bt))
def box_bounds(b,z,height):return Part.makeBox(b.XLength,b.YLength,height,V(b.XMin,b.YMin,z))
main=board('PCB');head=board('camera-pcb')
ribbon=Part.makeBox(4,32.85,rt,V(-2,0,0))
# Dovetail plan tabs captured between PLA skins. No added length in the free span.
def tab(y,sign):
 pts=[(-1,0),(1,0),(1,0.8),(2,1.8),(2,2.8),(-2,2.8),(-2,1.8),(-1,.8)]
 wire=Part.makePolygon([V(x,y+sign*d,.2) for x,d in pts+[pts[0]]])
 return Part.Face(wire).extrude(V(0,0,.4))
anchors=[tab(0,-1),tab(32.85,1)]
for a in anchors:ribbon=ribbon.fuse(a)
main=main.cut(anchors[0]).removeSplitter();head=head.cut(anchors[1]).removeSplitter()
# Keep measured lens and LED XY extents; close inherited 0.0124 mm floating gaps.
lens_b=base.rigid_shape(scene['M4-lens'],(0,0,0)).BoundBox
lens=box_bounds(lens_b,bt,lens_b.ZMax)
# R03 connector exterior bounding box, with pins/cavities filled for a robust dummy.
sel=json.loads((HERE.parent/'study-r03/connector-selection.json').read_text());conn=Part.Shape();conn.read(str(HERE.parent/sel['asset']))
old=base.rigid_shape(scene['JST-4pin'],(0,0,0)).BoundBox;b=conn.BoundBox
conn.translate(V((old.XMin+old.XMax-b.XMin-b.XMax)/2,old.YMin-b.YMin,0));b=conn.BoundBox
connector=box_bounds(b,bt,b.ZMax)
leds=[box_bounds(base.rigid_shape(scene[n],(0,0,0)).BoundBox,bt,1) for n in ['IR-LED','IR-LED.001']]
parts={'Red_PLA_boards':Part.makeCompound([main,head]),'Black_PLA_lens':lens,'White_PLA_connector_LEDs':Part.makeCompound([connector]+leds),'Yellow_TPU_ribbon':ribbon.removeSplitter()}
colors=[(1,.12,.1),(.12,.12,.14),(.94,.94,.90),(1,.8,.02)]
# Shared print frame, all bed-contact surfaces at Z=0; preserve relative positions.
shift=V(0,31.283345794677736,0)
d=A.newDocument('CameraDummyR01');d.Label='CAMERA DUMMY R01 - PLA boards / TPU ribbon'
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
assert abs(ribbon.common(Part.makeBox(4,32.85,2,V(-2,0,0))).Volume-4*32.85*rt)<1e-7
for (name,sh),color in zip(parts.items(),colors):
 sh.translate(shift);o=d.addObject('PartDesign::Feature',name);o.Shape=sh
 o.addProperty('App::PropertyString','Material').Material='TPU' if 'TPU' in name else 'PLA'
 if A.GuiUp:o.ViewObject.ShapeColor=color
 mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
 assert mesh.isSolid();mesh.write(str(OUT/(name+'.stl')))
 report['parts'][name]={'solids':len(sh.Solids),'volume_mm3':sh.Volume,'mesh_closed':True,'triangles':mesh.CountFacets}
d.recompute();d.saveAs(str(OUT/'CAMERA-DUMMY-R01.FCStd'))
Part.makeCompound(list(parts.values())).exportStep(str(OUT/'CAMERA-DUMMY-R01.step'))
report['passed']=True
(OUT/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n')
if A.GuiUp:
 import FreeCADGui as G
 G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui()
 G.activeDocument().activeView().saveImage(str(OUT/'preview.png'),1600,1000,'White')
print('CAMERA_DUMMY_GEOMETRY_OK',flush=True)
