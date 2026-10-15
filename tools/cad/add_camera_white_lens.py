"""Add a shallow white lens cap, keeping the black notched rim visible."""
from pathlib import Path
import json
import FreeCAD as A,Part,MeshPart
R=Path.cwd();O=R/'generated/eye-tracker/shared/camera-interlock-075-r06';O.mkdir(parents=True,exist_ok=True)
d=A.openDocument(str(R/'generated/eye-tracker/shared/camera-interlock-075-r05/CAMERA-INTERLOCK-075-R05.FCStd'))
black=d.Black_PLA_lens.Shape;white=d.White_PLA_connector_LEDs.Shape
lens=max(black.Solids,key=lambda s:s.CenterOfMass.y);b=lens.BoundBox;cx=(b.XMin+b.XMax)/2;cy=(b.YMin+b.YMax)/2
radius=1.55;height=.55;base=4.35;sr=(radius*radius+height*height)/(2*height)
dome=Part.makeSphere(sr,A.Vector(cx,cy,base+height-sr)).common(Part.makeBox(4,4,height,A.Vector(cx-2,cy-2,base))).removeSplitter()
assert dome.isValid() and len(dome.Solids)==1 and dome.common(black).Volume>0
black=black.cut(dome).removeSplitter();white=white.fuse(dome).removeSplitter()
assert black.isValid() and white.isValid() and black.common(white).Volume<1e-7
for name,sh in [('Black_PLA_lens',black),('White_PLA_connector_LEDs',white)]:
 d.getObject(name).Shape=sh
 mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.02,AngularDeflection=.1,Relative=False);assert mesh.isSolid();mesh.write(str(O/(name+'.stl')))
d.Label='Camera dummy - white domed lens';d.recompute();d.saveAs(str(O/'CAMERA-INTERLOCK-075-R06.FCStd'))
(O/'validation.json').write_text(json.dumps({'units':'mm','dome_diameter':3.1,'dome_height':height,'dome_top_z':base+height,'black_rim_top_z':b.ZMax,'material_overlap_mm3':black.common(white).Volume,'valid_solids':True,'closed_meshes':True,'physical_print_verified':False},indent=2))
