from pathlib import Path
import sys,json,hashlib,copy
import FreeCAD as A,Part,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/neutral-camera-r20';O=R/'generated/eye-tracker/rat/neutral-camera-r20';O.mkdir(parents=True,exist_ok=True)
review=json.loads((S.parent/'compact-guard-r19/review.json').read_text());assert hashlib.sha256((R/review['native_checkpoint']).read_bytes()).hexdigest()==review['native_sha256']
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
from detailed_ribbon import ribbon_solid
sys.path.insert(0,str(R/'designs/eye-tracker/shared/compact-guard-r02'));from smooth_guard import build as lower
sys.path.insert(0,str(R/'designs/eye-tracker/rat/targeted-r18'));from arm_geometry import geometry,rectangle,unit
m=json.loads((R/'designs/eye-tracker/mouse/compact-guard-r16/review.json').read_text());src=R/m['native_checkpoint'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['native_sha256'];sel=json.loads((S.parent/'active-model.json').read_text());print('Historical selected R01 hash match:',hashlib.sha256((R/sel['native_checkpoint']).read_bytes()).hexdigest()==sel['native_sha256'],flush=True);d=A.openDocument(str(src));sol=json.loads((S/'solution.json').read_text());D=A.Placement(A.Matrix(*sum(sol['delta_relative_R16'],[])))
old={n:world(d.getObject(n)) for n in ['FinishedCarrier','RetainedSocket','UpperSupport','RearRibbonGuard','RetainedPCBTray','camera_pcb','M4_lens','IR_LED','IR_LED_001','eye_primary_Holder','eye_primary_Clip','RibbonCandidate','PCB','JST_4pin','eye_primary_Cap','skull_mount_Baseplate']};sh={n:v.copy() for n,v in old.items()}
for n in ['RetainedSocket','camera_pcb','M4_lens','IR_LED','IR_LED_001','eye_primary_Holder','eye_primary_Clip']:
 sh[n].Placement=D.multiply(sh[n].Placement);assign(d.getObject(n),sh[n])
rib,mesh,metric=ribbon_solid(sol['parameters']);sh['RibbonCandidate']=rib;assign(d.RibbonCandidate,rib)
config=json.loads((R/'designs/eye-tracker/mouse/inset-arm-r08/input-parameters.json').read_text())['arms']['UpperSupport'];config['attachment_height_mm']=4.2
low=json.loads((R/'designs/eye-tracker/mouse/compact-guard-r13/recipe.json').read_text())['guard'];params={'UpperSupport':config,'RearRibbonGuard':low['parameters']}
absolute=A.Placement(A.Matrix(*sum(sol['delta'],[])))
for name,p in params.items():
 p['socket_center_mm']=list(absolute.multVec(A.Vector(*p['socket_center_mm'])));p['socket_axis']=list(absolute.Rotation.multVec(A.Vector(*p['socket_axis'])));p['arm']['radial_direction']=list(absolute.Rotation.multVec(A.Vector(*p['arm']['radial_direction'])))
 if name=='RearRibbonGuard':arm=lower(p,[-8.,0.,20.])
 else:
  arm=None
  for rh,shandle in [(8,8),(12,8),(8,12),(12,12),(4,2),(15,15)]:
   p['arm']['root_handle_mm']=rh;p['arm']['socket_handle_mm']=shandle
   try:
    candidate=geometry(p,p['body_width_mm'],p['body_thickness_mm'])[0]
    if candidate.isValid():arm=candidate;break
   except Exception as exc:print('upper retry',rh,shandle,str(exc)[:50],flush=True)
  assert arm is not None,'No valid upper arm'
  n=unit(p['socket_axis']);v=unit(p['arm']['radial_direction']);end=A.Vector(*p['socket_center_mm'])+n*p['attachment_height_mm']+v*p['attachment_radius_mm'];w=unit(v.cross(n));arm=arm.fuse(Part.makeLoft([rectangle(end+v*.25,-v,w,3,2.2),rectangle(end-v*.8,-v,w,3,2.2)],True,True)).removeSplitter()
 sh[name]=arm;assign(d.getObject(name),arm);print(name,'tray',arm.common(sh['RetainedPCBTray']).Volume,'socket',arm.common(sh['RetainedSocket']).Volume,flush=True)
carrier=sh['RetainedPCBTray'].multiFuse([sh['RetainedSocket'],sh['UpperSupport'],sh['RearRibbonGuard']]).removeSplitter();carrier=carrier.cut(Part.makeBox(3.70677424482636-3.2,3.7,5.8,A.Vector(3.2,11.4,-2.9))).removeSplitter();carrier.limitTolerance(1e-6);assert carrier.isValid() and len(carrier.Solids)==1;sh['FinishedCarrier']=carrier;assign(d.FinishedCarrier,carrier)
a=d.DetailedOpticalAxis;a.Placement=D.multiply(a.Placement)
d.recompute();d.Label='ET-RAT-NEUTRAL-R20';d.saveAs(str(O/'ET-RAT-NEUTRAL-R20.FCStd'));(S/'arms.json').write_text(json.dumps(params,indent=2))
report={'source':m,'pose':sol,'ribbon_metric':metric,'carrier_valid':True,'carrier_solids':1,'ribbon':{},'carrier':{}}
for n in ['RetainedSocket','UpperSupport','RearRibbonGuard','FinishedCarrier','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','skull_mount_Baseplate']:
 v=rib.common(sh[n]).Volume;gap=rib.distToShape(sh[n])[0];report['ribbon'][n]={'overlap_mm3':v,'gap_mm':gap};print('ribbon',n,v,gap,flush=True);(O/'validation.json').write_text(json.dumps(report,indent=2))
for n in ['eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens']:
 v=carrier.common(sh[n]).Volume;prev=old['FinishedCarrier'].common(old[n]).Volume;report['carrier'][n]={'overlap_mm3':v,'previous_mm3':prev};print('carrier',n,v,prev,flush=True)
(O/'validation.json').write_text(json.dumps(report,indent=2));print('BUILT',flush=True)

assert all(v["overlap_mm3"] < 1e-6 for v in report["ribbon"].values()), "Ribbon collision"
assert all(v["overlap_mm3"] <= v["previous_mm3"]+1e-6 for v in report["carrier"].values()), "New carrier collision"

# Apply the accepted mount frame once to hardware after local fit checks.
M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])))
for name in sh:
 assign(d.getObject(name),sh[name].transformed(M.toMatrix()))
d.DetailedOpticalAxis.Placement=M.multiply(d.DetailedOpticalAxis.Placement)
d.recompute();d.saveAs(str(O/'ET-RAT-NEUTRAL-R20.FCStd'))
print('WORLD_ASSEMBLY_READY',flush=True)
