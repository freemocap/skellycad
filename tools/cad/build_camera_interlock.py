"""0.75 mm camera with captive TPU anchors at both PCB boundaries; mm."""
from pathlib import Path
import json,hashlib,itertools
import FreeCAD as A,Part,MeshPart
R=Path.cwd();O=R/'generated/eye-tracker/shared/camera-interlock-075-r01';O.mkdir(parents=True,exist_ok=True)
S=R/'designs/eye-tracker/shared/cameras/pupil-core-eye';m=json.loads((S/'active-model.json').read_text())
parts={}
for name,rec in m['parts'].items():
 p=R/rec['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'];sh=Part.Shape();sh.read(str(p))
 if name in ['Red_PLA_boards','Yellow_TPU_ribbon']:
  faces=[f for f in sh.Faces if abs(f.BoundBox.ZMin)<1e-6 and abs(f.BoundBox.ZMax)<1e-6]
  sh=sh.multiFuse([f.extrude(A.Vector(0,0,-.5)) for f in faces]).removeSplitter()
 sh.translate(A.Vector(0,0,.5));parts[name]=sh
red=parts['Red_PLA_boards'];yellow=parts['Yellow_TPU_ribbon'];before=red.fuse(yellow)
b=yellow.BoundBox;anchors=[]
for edge,direction in [(b.YMin,-1),(b.YMax,1)]:
 # Full-height narrow neck, enlarged central head trapped by PLA skins.
 ys=sorted([edge-direction*.2,edge+direction*2.1])
 neck=Part.makeBox(1.6,ys[1]-ys[0],.75,A.Vector(-.8,ys[0],0))
 head=Part.makeCylinder(1.5,.25,A.Vector(0,edge+direction*2.1,.25))
 anchor=neck.fuse(head).common(red).removeSplitter()
 assert anchor.Volume>2 and len(anchor.Solids)==1
 anchors.append(anchor)
keys=anchors[0].fuse(anchors[1]);red=red.cut(keys).removeSplitter();yellow=yellow.fuse(keys).removeSplitter()
assert red.isValid() and len(red.Solids)==2
assert yellow.isValid() and len(yellow.Solids)==1
assert red.common(yellow).Volume<1e-7
after=red.fuse(yellow);difference=before.cut(after).Volume+after.cut(before).Volume;assert difference<1e-7
parts['Red_PLA_boards']=red;parts['Yellow_TPU_ribbon']=yellow
report={'units':'mm','substrate_thickness':.75,'neck_width':1.6,'head_diameter':3.,'embed_depth':3.6,'head_z':[.25,.5],'PLA_skin_thickness':.25,'anchor_volumes_mm3':[s.Volume for s in anchors],'exterior_difference_mm3':difference,'material_overlaps':{},'physical_fit_verified':False,'bond_strength_verified':False,'parts':{}}
d=A.newDocument('CameraInterlock075R01')
for (an,a),(bn,bb) in itertools.combinations(parts.items(),2):
 v=a.common(bb).Volume;report['material_overlaps'][an+'/'+bn]=v;assert v<1e-7
for name,sh in parts.items():
 obj=d.addObject('Part::Feature',name);obj.Shape=sh
 mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
 print(name,mesh.isSolid(),mesh.hasSelfIntersections(),flush=True);assert mesh.isSolid() and (name not in ['Red_PLA_boards','Yellow_TPU_ribbon'] or not mesh.hasSelfIntersections());mesh.write(str(O/(name+'.stl')))
 report['parts'][name]={'solids':len(sh.Solids),'mesh_closed':True,'self_intersections':mesh.hasSelfIntersections()}
d.recompute();d.saveAs(str(O/'CAMERA-INTERLOCK-075-R01.FCStd'))
(O/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

