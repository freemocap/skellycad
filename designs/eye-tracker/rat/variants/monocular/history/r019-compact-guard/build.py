"""Tighten only the rear guard of the complete R18 assembly; units mm."""
from pathlib import Path
import sys, json, hashlib, math
import FreeCAD as A, Part, MeshPart
R=Path.cwd(); S=R/'designs/eye-tracker/rat/compact-guard-r19'; O=R/'generated/eye-tracker/rat/compact-guard-r19'; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
from replace_camera import world,assign
sys.path.insert(0,str(R/'designs/eye-tracker/shared/compact-guard-r02'))
from guard import unit,rectangle
m=json.loads((S.parent/'targeted-r18/review.json').read_text()); src=R/m['native_checkpoint']; assert hashlib.sha256(src.read_bytes()).hexdigest()==m['native_sha256']
sel=json.loads((S.parent/'active-model.json').read_text()); selected_actual=hashlib.sha256((R/sel['native_checkpoint']).read_bytes()).hexdigest()
# R01 is not an input to this adaptation; preserve and report its pre-existing mismatch.
d=A.openDocument(str(src))
p=json.loads((S.parent/'targeted-r18/arms.json').read_text())['RearRibbonGuard']; a=p['arm']
M=A.Placement(A.Matrix(*sum(json.loads((S.parent/'targeted-r18/solution.json').read_text())['mount_to_skull'],[])))
root=A.Vector(*a['root_mm']); t0=unit(a['root_tangent']); w0=unit(a['root_width_direction']); radial=unit(a['radial_direction']); n=unit(p['socket_axis'])
start=root+t0*p['embed_mm']; end=A.Vector(*p['socket_center_mm'])+n*p['attachment_height_mm']+radial*p['attachment_radius_mm']; stop=end+radial*p['socket_lead_mm']
# One polynomial span: no internal curve junction or tangent/curvature discontinuity.
poles=[start,start+t0*6,A.Vector(-9,2,17.5),A.Vector(-9,0,30),stop+radial*5,stop]
c=Part.BezierCurve(); c.setPoles(poles)
samples=[(c.value(i/48),c.tangent(i/48)[0]) for i in range(49)]
widths=[w0]
for (_,u),(_,v) in zip(samples,samples[1:]): widths.append(A.Rotation(u,v).multVec(widths[-1]))
target=unit(radial.cross(n))
if widths[-1].dot(target)<0:target=-target
t=samples[-1][1]; angle=math.degrees(math.atan2(t.dot(widths[-1].cross(target)),widths[-1].dot(target)))
wires=[]
for i,((pos,t),w) in enumerate(zip(samples,widths)):
 u=i/48; w=A.Rotation(t,angle*u*u*(3-2*u)).multVec(w)
 q=min(1,2*u);q=q*q*(3-2*q); b=a['root_width_mm']*(1-q)+2.6*q; h=a['root_thickness_mm']*(1-q)+1.8*q
 if u>.5:
  q=2*u-1;q=q*q*(3-2*q);b=2.6*(1-q)+3*q;h=1.8*(1-q)+2.2*q
 wires.append(rectangle(pos,t,w,b,h))
arm=Part.makeLoft(wires,True,False,False,5)
arm=arm.fuse(Part.makeLoft([rectangle(root,t0,w0,a['root_width_mm'],a['root_thickness_mm']),wires[0]],True,True))
arm=arm.fuse(Part.makeLoft([wires[-1],rectangle(end-radial*.8,-radial,target,3,2.2)],True,True)).removeSplitter()
assert arm.isValid() and len(arm.Solids)==1
arm=arm.transformed(M.toMatrix())
old=world(d.FinishedCarrier); before=world(d.RearRibbonGuard)
tray=world(d.RetainedPCBTray); socket=world(d.RetainedSocket); upper=world(d.UpperSupport)
carrier=tray.multiFuse([socket,upper,arm]).removeSplitter()
trim=Part.makeBox(3.70677424482636-3.2,3.7,5.8,A.Vector(3.2,11.4,-2.9)).transformed(M.toMatrix())
carrier=carrier.cut(trim).removeSplitter();carrier.limitTolerance(1e-6)
assert carrier.isValid() and len(carrier.Solids)==1
report={'selected_baseline_audit':{'recorded':sel['native_sha256'],'actual':selected_actual,'used_as_geometry_input':False},'source':m,'units':'mm','centerline':'single degree-5 Bezier','poles_mount_mm':[list(v) for v in poles], 'guard_valid':arm.isValid(),'carrier_solids':len(carrier.Solids),'seating':{'tray_overlap_mm3':arm.common(tray).Volume,'socket_overlap_mm3':arm.common(socket).Volume},'ribbon':{'overlap_mm3':arm.common(world(d.RibbonCandidate)).Volume,'gap_mm':arm.distToShape(world(d.RibbonCandidate))[0]},'carrier_collisions':{}}
for name in ['eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens','skull_mount_Baseplate']:
 sh=world(d.getObject(name)); prior=old.common(sh).Volume; now=carrier.common(sh).Volume
 report['carrier_collisions'][name]={'before_mm3':prior,'after_mm3':now}
 assert now<=prior+1e-5,(name,now,prior)
(O/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
assert report['ribbon']['overlap_mm3']<1e-6 and report['ribbon']['gap_mm']>=1.0
assert min(report['seating'].values())>.1
assign(d.RearRibbonGuard,arm);assign(d.FinishedCarrier,carrier)
mesh=MeshPart.meshFromShape(Shape=carrier,LinearDeflection=.03,AngularDeflection=.12,Relative=False)
report['carrier_mesh']={'closed':mesh.isSolid(),'self_intersections':mesh.hasSelfIntersections()}; assert mesh.isSolid() and not mesh.hasSelfIntersections()
mesh.write(str(O/'carrier.stl'))
report['fixed_interfaces']='All other geometry and placements inherited unchanged from R18'
(O/'validation.json').write_text(json.dumps(report,indent=2))
d.Label='Rat R19 - tighter smooth rear guard';d.recompute();d.saveAs(str(O/'ET-RAT-COMPACT-GUARD-R19.FCStd'))
print('R19 SAVED',flush=True)
