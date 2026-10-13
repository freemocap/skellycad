"""Local nose correction and non-adopted upper-lip clearance study."""
from pathlib import Path
import json,hashlib
import FreeCAD as A, Part
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file());OUT=ROOT/'generated/mouse-hats/pcb-retention-study'
m=json.loads((HERE/'reference-manifest.json').read_text());src=ROOT/m['snapshot'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['sha256']
r=A.openDocument(str(src));b=A.openDocument(str(OUT/'whole-board-review.FCStd'))
settings=json.loads((HERE/'top-lip-options.json').read_text())
x=settings['board_backing_x_mm']
# Limit cut to the tiny forward tip ABOVE the mounting lip; retain all Y<6 geometry.
tool=Part.makeBox(5,5,settings['nose_cut_z_span_mm'],A.Vector(x,settings['nose_cut_min_y_mm'],settings['nose_cut_z_min_mm']))
removed=r.Carrier.Shape.common(tool);fixed=r.Carrier.Shape.cut(tool).removeSplitter();fixed.check(True)
assert fixed.isValid() and len(fixed.Solids)==1
assert removed.BoundBox.YMin>=6-1e-6
assert fixed.common(tool).Volume<1e-8
# Hypothetical top capture; this diagnostic deliberately retains any cap collision.
edge=settings['board_upper_edge_y_assumed_mm'];z=settings['lip_start_z_mm'];gap=settings['roof_gap_mm']
backer=Part.makeBox(x-3.70677424482636,.8,2,A.Vector(3.70677424482636,17.2,z))
# Continuous L section: rear support spans to y18; roof reaches down to y17.
pts=[(x-.05,18,z),(x+1.2,18,z),(x+1.2,17,z),(x+.75,17,z),(x+.6,17.15,z),(x+.6,17.5,z),(x-.05,17.5,z)]
lip=Part.Face(Part.makePolygon([A.Vector(*v) for v in pts+[pts[0]]])).extrude(A.Vector(0,0,2)).fuse(backer).removeSplitter()
candidate=fixed.fuse(lip).removeSplitter();candidate.check(True);assert candidate.isValid() and len(candidate.Solids)==1
clash=lip.common(r.CapReference.Shape)
doc=A.newDocument('PCBTopLipOptions');doc.Label='PCB upper lip - flush nose / clearance options (STUDY)'
def add(name,label,shape):
 o=doc.addObject('Part::Feature',name);o.Label=label;o.Shape=shape;return o
add('FixedCarrier','Carrier - circled nose flush with board backing',fixed)
add('RemovedNose','Hidden red - removed nose only',removed)
add('CandidateWithLip','Hidden fused carrier - lip CONCEPT, cap conflict unresolved',candidate)
add('TopLip','Gold - TOP lip concept; current cap conflicts',lip)
add('CapConflict','Red - lip overlap with current cap',clash)
for name in ['WholePCB','ConnectorEnvelope','Holder','ClipReference','CapReference']:
 add(name,b.getObject(name).Label,b.getObject(name).Shape)
# A dimensional target only. Not a stretched carrier or a translated cap.
for name,y in [('CurrentUpperEdge',17.5923586623637),('PlusOneTarget',18.5923586623637)]:
 add(name,('Current upper edge datum' if name=='CurrentUpperEdge' else '+1 mm HEIGHT TARGET - not solid geometry'),Part.makeLine(A.Vector(x+1.3,y,-17.59),A.Vector(x+1.3,y,17.766)))
doc.recompute();doc.saveAs(str(OUT/'top-lip-clearance-study.FCStd'))
report={'nose_removed_mm3':removed.Volume,'nose_protrusion_mm':removed.BoundBox.XMax-x,'nose_flush_plane_x_mm':x,'nose_cut_min_y_mm':6,'valid_fixed_carrier':True,'lower_mount_geometry_preserved_below_y_mm':6,'lip_cap_overlap_mm3':clash.Volume,'lip_board_overlap_mm3':lip.common(b.WholePCB.Shape).Volume,'current_side_room_mm':17.5923586623637-edge,'plus_one_side_room_mm':18.5923586623637-edge,'lip_post_width_mm':.5,'pcb_to_post_gap_mm':.1,'fixed_carrier_board_overlap_mm3':fixed.common(b.WholePCB.Shape).Volume,'whole_pcb_pose_verified':False,'height_change_adopted':False,'upper_lip_adopted':False}
(OUT/'top-lip-clearance-study.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
