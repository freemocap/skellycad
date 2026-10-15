"""Cosmetic solder leads and raised board traces; no functional circuitry."""
from pathlib import Path
import json,hashlib
import FreeCAD as A,Part,MeshPart
R=Path.cwd();base=R/'generated/eye-tracker/shared/camera-interlock-075-r04';O=R/'generated/eye-tracker/shared/camera-interlock-075-r05';O.mkdir(parents=True,exist_ok=True)
src=base/'CAMERA-INTERLOCK-075-R04.FCStd';d=A.openDocument(str(src))
layout=json.loads((base/'validation.json').read_text())['chip_layout_xywhh_mm']
bits=[];width=.45;z=.75;height=.25
for x,y,w,l,h in layout:
 count=max(1,int((l-.4)/.85))
 for i in range(count):
  yy=y+(i+.5)*l/count-width/2
  for xx in [x-.7,x+w]:bits.append(Part.makeBox(.7,width,height,A.Vector(xx,yy,z)))
 # Four-sided lead package for the large chip near the ribbon.
 if w>4:
  for i in range(5):
   xx=x+(i+.5)*w/5-width/2
   for yy in [y-.7,y+l]:bits.append(Part.makeBox(width,.7,height,A.Vector(xx,yy,z)))
pin_count=len(bits)
paths=[[(2.8,4.95),(2.8,6.2),(-.6,6.2),(-.6,7.7)],
       [(-2.6,8.6),(-2.6,10.4),(-1.6,10.4),(-1.6,12.8)],
       [(2.8,10),(2.8,13.4),(3.2,13.4),(3.2,19.8),(1.5,19.8),(1.5,22)],
       [(-1.6,17.1),(-1.6,18.5),(-3.2,18.5),(-3.2,23)],
       [(1.5,15.7),(1.5,17.8),(.2,17.8),(.2,22)]]
for path in paths:
 for (x1,y1),(x2,y2) in zip(path,path[1:]):
  bits.append(Part.makeBox(abs(x2-x1)+width,abs(y2-y1)+width,.125,A.Vector(min(x1,x2)-width/2,min(y1,y2)-width/2,z)))
detail=bits[0].multiFuse(bits[1:]).removeSplitter()
black=d.Black_PLA_lens.Shape;white=d.White_PLA_connector_LEDs.Shape;red=d.Red_PLA_boards.Shape
detail=detail.cut(black).cut(white).removeSplitter()
assert detail.isValid()
for s in detail.Solids:
 assert s.distToShape(red)[0]<1e-7
 assert s.common(red).Volume<1e-7
new=white.fuse(detail).removeSplitter()
assert new.isValid() and new.common(black).Volume<1e-7 and new.common(d.Yellow_TPU_ribbon.Shape).Volume<1e-7
mesh=MeshPart.meshFromShape(Shape=new,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/'White_PLA_connections.stl'))
d.White_PLA_connector_LEDs.Shape=new;d.White_PLA_connector_LEDs.Label='White PLA - connector, LEDs and cosmetic solder connections'
d.Label='Camera dummy - chips, solder pins and traces';d.recompute();d.saveAs(str(O/'CAMERA-INTERLOCK-075-R05.FCStd'))
report={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'units':'mm','pin_count_before_trimming':pin_count,'lead_width':width,'lead_height':height,'trace_height':.125,'trace_routes':paths,'white_mesh_closed':True,'white_self_intersections':False,'board_contact_verified':True,'material_overlaps_mm3':0,'cosmetic_only':True,'sliced':False,'physical_fit_verified':False}
(O/'validation.json').write_text(json.dumps(report,indent=2));print(report)
