from pathlib import Path
import json
import FreeCAD as A,Part
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry/with-catch/numeric-labels'
x=5.28706399647303
report={}
for letter,h in [('H',.5),('T',1.)]:
 d=A.openDocument(str(p/('R11B-'+letter+'-numeric-catch.FCStd')))
 top=17.5923586623637+h-.15;post=top-.4
 rows=[]
 for thick in [.8,1.0,1.2]:
  # Add outward from PCB, keep underside and edge clearance fixed.
  pts=[(x-.08,top),(x+.6+thick,top),(x+.6+thick,17.0),(x+.75,17.0),(x+.6,17.15),(x+.6,post),(x-.08,post)]
  vs=[A.Vector(a,b,-10.7) for a,b in pts]
  lip=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,2))
  support=Part.makeBox(x-3.70677424482636,.7,2,A.Vector(3.70677424482636,top-.7,-10.7))
  lip=lip.fuse(support).removeSplitter()
  s=d.Carrier.Shape.fuse(lip).removeSplitter();s.check(True)
  rows.append({'roof_mm':thick,'length_mm':2,'cap_overlap_mm3':lip.common(d.Cap.Shape).Volume,'pcb_overlap_mm3':lip.common(d.ApproxPCB.Shape).Volume,'cap_distance_mm':lip.distToShape(d.Cap.Shape)[0],'added_mm3':s.Volume-d.Carrier.Shape.Volume,'valid':s.isValid(),'solids':len(s.Solids)})
 report[letter]=rows
 A.closeDocument(d.Name)
print(json.dumps(report,indent=2))
(ROOT/'generated/mouse-hats/pcb-retention-study/catch-strength-thickness-probe.json').write_text(json.dumps(report,indent=2))
