"""Isolated rigid PCB catch mockups. No production geometry is replaced."""
from pathlib import Path
import json,hashlib
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/pcb-retention-study';OUT.mkdir(exist_ok=True)
manifest=json.loads((HERE/'reference-manifest.json').read_text())
source=ROOT/manifest['snapshot'];assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['sha256']
ref=App.openDocument(str(source))
p=json.loads((HERE/'mockup-settings.json').read_text())
seat=p['seat_x_mm'];edge=p['board_edge_y_trial_mm'];end=p['board_end_z_trial_mm']
gap=p['roof_gap_mm'];roof=p['roof_thickness_mm'];overlap=p['overlap_mm'];sidegap=p['edge_side_gap_mm'];wall=p['root_width_mm']
# This is only the local corner of a board, not a full fitted PCB or component map.
board=Part.makeBox(p['pcb_thickness_mm'],3.5,6,App.Vector(seat,edge,end))
def prism(points,vector):
 return Part.Face(Part.makePolygon([App.Vector(*v) for v in points+[points[0]]])).extrude(App.Vector(*vector))
def catch(kind):
 # Chamfer the last 0.15 mm of the underside as a lead-in; roof depth remains 0.6 mm.
 a=seat-.15;b=seat+gap;c=b+roof
 if kind=='R1':
  out=edge-sidegap-wall;post=edge-sidegap;tip=edge+overlap;z=-13.0
  pts=[(a,out,z),(c,out,z),(c,tip,z),(b+.15,tip,z),(b,tip-.15,z),(b,post,z),(a,post,z)]
  return prism(pts,(0,0,2))
 out=end-sidegap-wall;post=end-sidegap;tip=end+overlap;y=edge+.55
 pts=[(a,y,out),(c,y,out),(c,y,tip),(b+.15,y,tip),(b,y,tip-.15),(b,y,post),(a,y,post)]
 return prism(pts,(0,2,0))
def iso(s):
 t=Part.Shape();t.importBrepFromString(s.exportBrepToString());return t
reports={}
for key in ['R1','R2']:
 add=catch(key); final=ref.Carrier.Shape.fuse(add).removeSplitter();final.check(True)
 assert final.isValid() and len(final.Solids)==1
 capover=iso(add).common(iso(ref.CapReference.Shape)).Volume
 boardover=add.common(board).Volume
 assert capover<1e-8 and boardover<1e-8
 # Simple local sliding demonstration only: opposite-side stops/ribbon not modeled.
 delta=App.Vector(0,.8,0) if key=='R1' else App.Vector(0,0,.8)
 travel=[]
 for i in range(21):
  s=board.copy();s.translate(delta*(i/20));travel.append(add.common(s).Volume)
 assert max(travel)<1e-8
 doc=App.newDocument('PCB'+key);doc.Label='PCB-'+key+' - RIGID CATCH CONCEPT (not print-ready)'
 def obj(name,label,shape):
  o=doc.addObject('Part::Feature',name);o.Label=label;o.Shape=shape;return o
 obj('CarrierReference','Frozen R06A carrier - reference',ref.Carrier.Shape)
 obj('CandidateCarrier','Full carrier with integral catch - concept',final)
 obj('Catch','Gold - added integral geometry',add)
 # Crop for inspection only. Never export this cropped view for printing.
 crop=Part.makeBox(9,13,13,App.Vector(2,6,-19))
 obj('TrayDetail','Blue - cropped tray reference, NOT a print part',ref.Carrier.Shape.common(crop))
 obj('BoardEdge','Green - illustrative PCB corner, placement unverified',board)
 ghost=board.copy();ghost.translate(delta)
 obj('InsertionStart','Optional ghost - local slide start only',ghost)
 obj('CapReference','Optional cap - seated position',ref.CapReference.Shape)
 doc.recompute();doc.saveAs(str(OUT/(key.lower()+'-concept.FCStd')))
 reports[key]={'valid_carrier':True,'carrier_solids':1,'added_volume_mm3':final.Volume-ref.Carrier.Shape.Volume,'catch_cap_overlap_mm3':capover,'catch_board_sample_overlap_mm3':boardover,'sampled_local_slide_max_overlap_mm3':max(travel),'slide_samples':21,'full_board_insertion_verified':False,'components_verified':False,'roof_gap_mm':gap,'nominal_edge_overlap_mm':overlap,'board_lift_clearance_mm':gap-p['pcb_thickness_mm']}
 App.closeDocument(doc.Name)
(OUT/'mockup-validation.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
