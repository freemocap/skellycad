"""Complete H/T height trials with rigid upper PCB catches. All lengths mm."""
from pathlib import Path
import json
import FreeCAD as A
import Part,MeshPart
from pcb_reference import board_shape,PARAMETERS as PCB
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry/labeled'
OUT=SRC.parent/'with-catch';OUT.mkdir(exist_ok=True)
x=5.28706399647303
settings={'units':'mm','pcb_seating_x':x,'pcb_top_y':PCB['board_upper_y_mm'],'pcb_thickness':.25,'lip_z_start':-10.7,'lip_length':2.0,'lip_lower_y':17.0,'roof_clearance_from_seat':.6,'roof_thickness':.6,'post_thickness':.4,'cap_wall_clearance':.15}
report={}
for letter,h in [('H',.5),('T',1.)]:
 d=A.openDocument(str(SRC/('R11B-'+letter+'-height-test.FCStd')))
 old=d.Carrier.Shape;cap=d.Cap.Shape;holder=d.Holder.Shape
 # Fixed landing plane; remove only the previously approved tiny stem nose.
 nose=Part.makeBox(5,5,2,A.Vector(x,6,-1))
 fixed=old.cut(nose).removeSplitter()
 top=17.5923586623637+h-.15
 postbottom=top-.4
 # One L profile: upper edge stop plus short retaining roof over bare PCB edge.
 pts=[(x-.08,top),(x+1.2,top),(x+1.2,17.0),(x+.75,17.0),(x+.6,17.15),(x+.6,postbottom),(x-.08,postbottom)]
 vs=[A.Vector(px,py,-10.7) for px,py in pts]
 lip=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,2))
 # Anchor into the backing continuously; no free-standing extra part.
 support=Part.makeBox(x-3.70677424482636,.7,2,A.Vector(3.70677424482636,top-.7,-10.7))
 lip=lip.fuse(support).removeSplitter()
 new=fixed.fuse(lip).removeSplitter();new.check(True)
 board=board_shape()
 row={'height_mm':h,'valid':new.isValid(),'solids':len(new.Solids),'lip_cap_overlap_mm3':lip.common(cap).Volume,'lip_board_overlap_mm3':lip.common(board).Volume,'carrier_board_overlap_mm3':new.common(board).Volume,'nose_removed_mm3':old.common(nose).Volume,'added_catch_mm3':new.Volume-fixed.Volume,'cap_contact_mm3':new.common(cap).Volume,'holder_gap_mm':new.distToShape(holder)[0],'top_edge_room_mm':postbottom-PCB['board_upper_y_mm'],'roof_clearance_above_bare_pcb_mm':.35}
 print(letter,row,flush=True)
 assert new.isValid() and len(new.Solids)==1
 assert row['lip_cap_overlap_mm3']<1e-7 and row['lip_board_overlap_mm3']<1e-7
 # Verify this is an actual upper/lift stop, not just decorative backing.
 upward=board.copy();upward.translate(A.Vector(0,row['top_edge_room_mm']+.1,0))
 lifted=board.copy();lifted.translate(A.Vector(.45,0,0))
 row['upper_escape_blocked_mm3']=lip.common(upward).Volume
 row['outward_escape_blocked_mm3']=lip.common(lifted).Volume
 assert row['upper_escape_blocked_mm3']>0 and row['outward_escape_blocked_mm3']>0
 row['inherited_board_envelope_overlap_mm3']=fixed.common(board).Volume
 assert new.common(board).Volume<1e-7
 assert cap.common(board).Volume<1e-7
 assert abs(new.common(board).Volume-fixed.common(board).Volume)<1e-7
 d.Carrier.Shape=new
 o=d.addObject('Part::Feature','UpperCatch');o.Shape=lip;o.Label='Upper PCB capture - integral, helper hidden'
 o=d.addObject('Part::Feature','ApproxPCB');o.Shape=board;o.Label='PCB envelope - slot-derived 30 x 9.2 x 0.25 mm'
 d.recompute();d.saveAs(str(OUT/('R11B-'+letter+'-with-catch.FCStd')))
 for name,shape in [('carrier-and-holder',Part.makeCompound([new,holder])),('cap',cap)]:
  mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
  mesh.write(str(OUT/('R11B-'+letter+'-plus-'+str(h).replace('.','p')+'mm-with-catch-'+name+'.stl')))
 report[letter]=row;A.closeDocument(d.Name)
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
(Path(__file__).parent/'catch-print-settings.json').write_text(json.dumps(settings,indent=2))
