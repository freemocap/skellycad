"""Cosmetic main-board components for the 0.75 mm three-tooth print model."""
from pathlib import Path
import json,hashlib
import FreeCAD as A,Part,MeshPart
R=Path.cwd();src=R/'generated/eye-tracker/shared/camera-interlock-075-r02/CAMERA-INTERLOCK-075-R02.FCStd'
O=R/'generated/eye-tracker/shared/camera-interlock-075-r04';O.mkdir(parents=True,exist_ok=True)
d=A.openDocument(str(src));red=d.Red_PLA_boards.Shape;white=d.White_PLA_connector_LEDs.Shape
connector=min(white.Solids,key=lambda s:s.CenterOfMass.y);height=connector.BoundBox.ZLength
# x,y,width,length,height: approximate populated-board appearance, not real circuitry.
layout=[(-2.25,22.0,4.5,6.0,1.375),(-3.2,12.8,3.2,4.3,1.125),(.8,14.5,2.6,1.2,1.0),(.1,7.7,3.6,2.3,1.25),(-3.2,7.5,1.8,1.1,1.0),(1.2,11.2,1.5,1.2,1.0)]
chips=[]
for x,y,w,l,h in layout:
 assert height/3<=h<=height/2
 sh=Part.makeBox(w,l,h,A.Vector(x,y,.75));assert sh.isValid()
 assert sh.common(red).Volume<1e-7 and sh.distToShape(red)[0]<1e-7
 for other in [white,d.Black_PLA_lens.Shape,d.Yellow_TPU_ribbon.Shape,*chips]:assert sh.common(other).Volume<1e-7
 chips.append(sh)
group=Part.makeCompound(chips);mesh=MeshPart.meshFromShape(Shape=group,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/'Black_PLA_chips.stl'))
d.Black_PLA_lens.Shape=Part.makeCompound([d.Black_PLA_lens.Shape,*chips]);d.Black_PLA_lens.Label='Black PLA - lens assembly and cosmetic PCB chips'
d.Label='Camera 0.75 mm - three-tooth joints and populated PCB';d.recompute();d.saveAs(str(O/'CAMERA-INTERLOCK-075-R04.FCStd'))
report={'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'JST_height_above_board_mm':height,'chip_layout_xywhh_mm':layout,'reference_photo':'codex-clipboard-926b0153-6802-4198-949a-ce155ceaf8a5.png','layout_basis':'Approximate visual proportions; not calibrated component measurements','chip_count':len(chips),'chip_mesh_closed':True,'self_intersections':False,'material_overlaps_mm3':0,'board_contact_verified':True,'unchanged':['boards','ribbon','three-tooth joints','JST','LEDs','lens'],'physical_fit_verified':False}
(O/'validation.json').write_text(json.dumps(report,indent=2));print(report)
