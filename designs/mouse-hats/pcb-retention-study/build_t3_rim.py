"""T3: raise tray-side cap engagement rail to catch the T2 upper hook."""
from pathlib import Path
import json
import FreeCAD as A,Part,MeshPart
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry';OUT=P/'t3-rim';OUT.mkdir(exist_ok=True)
s=A.openDocument(str(P/'t2-grip/R11B-T2-grip.FCStd'))
x0=4.28706399647303;x1=5.28706399647303;y0=17.5918887142941
# Added ridge lies ahead of hook with 0.15 mm lateral clearance. Its chamfer
# provides a lead-in; it retains a vertical shoulder below the chamfer.
pts=[(x0,y0-.2),(x1,y0-.2),(x1,y0+.7),(x0+.45,y0+.7),(x0+.3,y0+.55),(x0+.3,y0),(x0,y0)]
vs=[A.Vector(x,y,-8.03370315014152) for x,y in pts]
rail=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,17.365))
carrier=s.Carrier.Shape.fuse(rail).removeSplitter();carrier.check(True)
assert carrier.isValid() and len(carrier.Solids)==1
cap=s.Cap.Shape
roi=Part.makeBox(5,4,13,A.Vector(2,16,-7))
old_overlap=s.Carrier.Shape.common(cap).Volume
assert abs(carrier.common(cap).Volume-old_overlap)<1e-7
assert carrier.common(s.ApproxPCB.Shape).Volume<1e-7
assert abs(carrier.distToShape(s.Holder.Shape)[0]-.33172186266949)<1e-6
pull=cap.copy();pull.translate(A.Vector(.3,0,0))
old_block=s.Carrier.Shape.common(pull).common(roi).Volume
new_block=carrier.common(pull).common(roi).Volume
assert new_block>0 and old_block<1e-7,(old_block,new_block)
report={'rail_raise_mm':.7,'rail_length_mm':17.365,'entry_chamfer_mm':.15,'rail_top_y_mm':y0+.7,'cap_roof_y_mm':18.5923586623637,'roof_clearance_mm':18.5923586623637-(y0+.7),'hook_tip_y_mm':17.7423586623637,'vertical_capture_mm':y0+.7-17.7423586623637,'lateral_hook_clearance_mm':.15,'carrier_added_mm3':carrier.Volume-s.Carrier.Shape.Volume,'seated_cap_contact_mm3':carrier.common(cap).Volume,'board_overlap_mm3':0,'pull_test_mm':.3,'previous_upper_hook_blocking_mm3':old_block,'new_upper_hook_blocking_mm3':new_block}
print(json.dumps(report,indent=2),flush=True)
d=A.newDocument('T3Rim');d.Label='T3 +1 mm tray - raised cap engagement rail'
for name,sh in [('Carrier',carrier),('Cap',cap),('UpperRail',rail),('UpperCatch',s.UpperCatch.Shape),('Holder',s.Holder.Shape),('ApproxPCB',s.ApproxPCB.Shape)]:
 o=d.addObject('Part::Feature',name);o.Shape=sh
for name,sh in [('carrier-and-holder',Part.makeCompound([carrier,s.Holder.Shape])),('cap',cap)]:
 m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.03,AngularDeflection=.15,Relative=False);m.write(str(OUT/('R11B-T3-plus-1p0mm-'+name+'.stl')))
d.recompute();d.saveAs(str(OUT/'R11B-T3-rim.FCStd'))
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
(ROOT/'designs/mouse-hats/pcb-retention-study/t3-rim-settings.json').write_text(json.dumps(report,indent=2))
