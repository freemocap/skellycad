"""T2 +1 mm tray: relocated stronger PCB lip and deeper upper cap hook."""
from pathlib import Path
import json
import FreeCAD as A,Part,MeshPart
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry'
OUT=P/'t2-grip';OUT.mkdir(exist_ok=True)
s=A.openDocument(str(P/'with-catch/numeric-labels/R11B-T-numeric-catch.FCStd'))
b=A.openDocument(str(P/'labeled/R11B-T-height-test.FCStd'))
x=5.28706399647303;top=18.4423586623637
# Use height carrier without previous catch, retaining embossed numeric label.
base=b.Carrier.Shape.cut(b.CarrierEmboss.Shape.common(Part.makeBox(100,200,200,A.Vector(3.70677424482636-100,-100,-100)))).removeSplitter()
base=base.cut(Part.makeBox(5,5,2,A.Vector(x,6,-1))).removeSplitter()
base=base.fuse(s.CarrierEmboss.Shape).removeSplitter()
z=-12.7;length=3.;tip=17.2
pts=[(x-.08,top),(x+1.6,top),(x+1.6,tip),(x+.75,tip),(x+.6,tip+.15),(x+.6,top-.4),(x-.08,top-.4)]
vs=[A.Vector(a,b,z) for a,b in pts]
lip=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,length))
lip=lip.fuse(Part.makeBox(x-3.70677424482636,.7,length,A.Vector(3.70677424482636,top-.7,z))).removeSplitter()
carrier=base.fuse(lip).removeSplitter()
params=json.loads((ROOT/'designs/mouse-hats/reconstruction/pcb_cap/parameters.json').read_text())
f=next(f for f in params['features'] if f['name']=='LongRetainingLip')
pts=[]
for xx,yy,zz in f['profile_mm']:
 if yy<=17.592359: yy-=.35
 if abs(xx-4.28706399647313)<1e-6:xx+=.15
 pts.append(A.Vector(xx,yy+1,zz))
hook=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(*f['extrusion_mm']))
cap=s.Cap.Shape.fuse(hook).removeSplitter()
# Local clearance around the relocated PCB catch, limited to the upper cap locating tab.
relief=Part.makeBox(2.0,1.65,3.4,A.Vector(x-.05,17.0,z-.2))
removed=cap.common(relief)
cap=cap.cut(relief).removeSplitter()
# The recess severs a tiny distal corner of the old locating tab; discard that
# detached offcut instead of exporting a loose fragment into the assembly.
ordered=sorted(cap.Solids,key=lambda v:v.Volume,reverse=True)
offcut_volume=sum(v.Volume for v in ordered[1:])
assert offcut_volume<.1
cap=ordered[0].removeSplitter()
for sh in [carrier,cap]:
 print("CHECK",sh.isValid(),len(sh.Solids),[v.Volume for v in sh.Solids],flush=True)
 sh.check(True);assert sh.isValid() and len(sh.Solids)==1
report={'catch_center_shift_toward_JST_mm':1.5,'catch_along_edge_length_mm':3.,'catch_roof_mm':1.,'catch_tip_overlap_mm':17.38-tip,'cap_hook_deeper_mm':.35,'cap_hook_return_extra_mm':.15,'local_cap_tab_relief_removed_mm3':removed.Volume,'detached_tab_corner_removed_mm3':offcut_volume,'carrier_cap_overlap_mm3':carrier.common(cap).Volume,'catch_cap_overlap_mm3':lip.common(cap).Volume,'catch_cap_min_gap_mm':lip.distToShape(cap)[0],'board_carrier_overlap_mm3':carrier.common(s.ApproxPCB.Shape).Volume,'board_cap_overlap_mm3':cap.common(s.ApproxPCB.Shape).Volume,'holder_gap_mm':carrier.distToShape(s.Holder.Shape)[0],'carrier_delta_mm3':carrier.Volume-s.Carrier.Shape.Volume,'cap_delta_mm3':cap.Volume-s.Cap.Shape.Volume}
print(json.dumps(report,indent=2),flush=True)
assert report['catch_cap_overlap_mm3']<1e-7
assert report['board_carrier_overlap_mm3']<1e-7 and report['board_cap_overlap_mm3']<1e-7
assert report['carrier_cap_overlap_mm3']<=.002219
assert abs(report['holder_gap_mm']-.33172186266949)<1e-6
u=s.ApproxPCB.Shape.copy();u.translate(A.Vector(0,.77,0));assert lip.common(u).Volume>0
v=s.ApproxPCB.Shape.copy();v.translate(A.Vector(.5,0,0));assert lip.common(v).Volume>0
d=A.newDocument('T2Grip');d.Label='T2 +1 mm - stronger relocated catch / deeper cap hook'
for name,sh in [('Carrier',carrier),('Cap',cap),('UpperCatch',lip),('UpperCapHook',hook),('CapReliefRemoved',removed),('Holder',s.Holder.Shape),('ApproxPCB',s.ApproxPCB.Shape)]:
 o=d.addObject('Part::Feature',name);o.Shape=sh
for name,sh in [('carrier-and-holder',Part.makeCompound([carrier,s.Holder.Shape])),('cap',cap)]:
 m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
 m.write(str(OUT/('R11B-T2-plus-1p0mm-'+name+'.stl')))
d.recompute();d.saveAs(str(OUT/'R11B-T2-grip.FCStd'))
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
(ROOT/'designs/mouse-hats/pcb-retention-study/t2-grip-settings.json').write_text(json.dumps(report,indent=2))

