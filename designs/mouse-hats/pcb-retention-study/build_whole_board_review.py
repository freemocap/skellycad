"""Whole-board orientation review, replacing rejected cropped-corner proposals.
No new catch is built until the upper-edge contact and insertion path are verified.
"""
from pathlib import Path
import hashlib,json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/pcb-retention-study'
m=json.loads((HERE/'reference-manifest.json').read_text());src=ROOT/m['snapshot']
assert hashlib.sha256(src.read_bytes()).hexdigest()==m['sha256']
ref=App.openDocument(str(src))
p=json.loads((HERE/'whole-board-settings.json').read_text())
x,y,z=p['board_underside_origin_mm'];L=p['board_length_mm'];W=p['board_width_mm'];t=p['board_thickness_mm']
board=Part.makeBox(t,W,L,App.Vector(x,y,z))
doc=App.newDocument('PCBWholeBoardReview');doc.Label='PCB retention - WHOLE BOARD and upward escape - placement study'
def obj(name,label,shape):
 o=doc.addObject('Part::Feature',name);o.Label=label;o.Shape=shape;return o
for name in ['Carrier','Holder','ClipReference','CapReference','BaseplateReference']:
 obj(name,('REFERENCE - ' if name=='CapReference' else '')+name,ref.getObject(name).Shape.copy())
obj('WholePCB','Whole PCB - approximate 30 x 10 x 0.25 mm, pose provisional',board)
# Height envelope illustrations, not an electronics reconstruction.
component=Part.makeBox(1.0-t,7.0,22,App.Vector(x+t,y+1.5,z+4))
connector=Part.makeBox(1.7-t,4.2,2.4,App.Vector(x+t,y+2.9,z))
obj('ComponentEnvelope','Optional component height envelope - position illustrative',component)
obj('ConnectorEnvelope','White connector envelope - 1.7 mm total height, footprint illustrative',connector)
# Orange line marks the desired TOP edge. It is an annotation, not added plastic.
edge=Part.makeCylinder(.13,9,App.Vector(x+t+.12,y+W,z+.8),App.Vector(0,0,1))
obj('UpperEdgeTarget','ORANGE - top edge to capture; annotation only',edge)
for i,az in enumerate([z+2.5,z+10]):
 start=App.Vector(x+2,y+W+.5,az);d=App.Vector(0,1,0)
 arrow=Part.makeCylinder(.16,3.4,start,d).fuse(Part.makeCone(.55,0,1,start+d*3.4,d))
 obj('EscapeArrow'+str(i),'RED - upward escape along tray (+Y), not a physical part',arrow)
# Full carrier reference is retained unchanged. A motion review is not a new print revision.
doc.recompute();doc.saveAs(str(OUT/'whole-board-review.FCStd'))
report={'reference_sha256':m['sha256'],'carrier_unchanged':doc.Carrier.Shape.exportBrepToString()==ref.Carrier.Shape.exportBrepToString(),'nominal_pcb_mm':[L,W,t],'board_pose_verified':False,'new_retainer_geometry_created':False,'board_carrier_overlap_at_provisional_pose_mm3':board.common(ref.Carrier.Shape).Volume,'board_cap_overlap_at_provisional_pose_mm3':board.common(ref.CapReference.Shape).Volume}
(OUT/'whole-board-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
