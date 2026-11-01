from pathlib import Path
import sys,json,hashlib,copy
import FreeCAD as A,Part,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/mouse/nasal-camera-r15';O=R/'generated/eye-tracker/mouse/nasal-camera-r15';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
from detailed_ribbon import ribbon_solid
sys.path.insert(0,str(R/'designs/eye-tracker/shared/compact-guard-r02'));from guard import build as lower
sys.path.insert(0,str(R/'designs/mouse-hats/b-flared-loop-r07'));from flared_arm import geometry,rectangle,unit
m=json.loads((S.parent/'landmark-eye-placement-r14/review.json').read_text());src=R/m['native_checkpoint'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['native_sha256'];sel=json.loads((S.parent/'active-model.json').read_text());assert hashlib.sha256((R/sel['native_checkpoint']).read_bytes()).hexdigest()==sel['native_sha256'];d=A.openDocument(str(src));sol=json.loads((S/'solution.json').read_text());D=A.Placement(A.Matrix(*sum(sol['delta'],[])))
old={n:world(d.getObject(n)) for n in ['FinishedCarrier','RetainedSocket','UpperSupport','RearRibbonGuard','RetainedPCBTray','camera_pcb','M4_lens','IR_LED','IR_LED_001','eye_primary_Holder','eye_primary_Clip','RibbonCandidate','PCB','JST_4pin','eye_primary_Cap','skull_mount_Baseplate']};sh={n:v.copy() for n,v in old.items()}
for n in ['RetainedSocket','camera_pcb','M4_lens','IR_LED','IR_LED_001','eye_primary_Holder','eye_primary_Clip']:
 sh[n].Placement=D.multiply(sh[n].Placement);assign(d.getObject(n),sh[n])
rib,mesh,metric=ribbon_solid(sol['parameters']);sh['RibbonCandidate']=rib;assign(d.RibbonCandidate,rib)
config=json.loads((S.parent/'inset-arm-r08/input-parameters.json').read_text())['arms']['UpperSupport'];config['attachment_height_mm']=4.2
low=json.loads((S.parent/'compact-guard-r13/recipe.json').read_text())['guard'];params={'UpperSupport':config,'RearRibbonGuard':low['parameters']}
for name,p in params.items():
 p['socket_center_mm']=list(D.multVec(A.Vector(*p['socket_center_mm'])));p['socket_axis']=list(D.Rotation.multVec(A.Vector(*p['socket_axis'])));p['arm']['radial_direction']=list(D.Rotation.multVec(A.Vector(*p['arm']['radial_direction'])))
 if name=='RearRibbonGuard':arm=lower(p,[-12.,0.,20.])
 else:
  arm=geometry(p,p['body_width_mm'],p['body_thickness_mm'])[0];n=unit(p['socket_axis']);v=unit(p['arm']['radial_direction']);end=A.Vector(*p['socket_center_mm'])+n*p['attachment_height_mm']+v*p['attachment_radius_mm'];w=unit(v.cross(n));arm=arm.fuse(Part.makeLoft([rectangle(end+v*.25,-v,w,3,2.2),rectangle(end-v*.8,-v,w,3,2.2)],True,True)).removeSplitter()
 sh[name]=arm;assign(d.getObject(name),arm);print(name,'tray',arm.common(sh['RetainedPCBTray']).Volume,'socket',arm.common(sh['RetainedSocket']).Volume,flush=True)
carrier=sh['RetainedPCBTray'].multiFuse([sh['RetainedSocket'],sh['UpperSupport'],sh['RearRibbonGuard']]).removeSplitter();carrier=carrier.cut(Part.makeBox(3.70677424482636-3.2,3.7,5.8,A.Vector(3.2,11.4,-2.9))).removeSplitter();carrier.limitTolerance(1e-6);assert carrier.isValid() and len(carrier.Solids)==1;sh['FinishedCarrier']=carrier;assign(d.FinishedCarrier,carrier)
a=d.DetailedOpticalAxis;a.Placement=D.multiply(a.Placement)
d.recompute();d.Label='ET-MOUSE-NASAL-R15';d.saveAs(str(O/'ET-MOUSE-NASAL-R15.FCStd'));(S/'arms.json').write_text(json.dumps(params,indent=2))
report={'source':m,'pose':sol,'ribbon_metric':metric,'carrier_valid':True,'carrier_solids':1,'ribbon':{},'carrier':{}}
for n in ['RetainedSocket','UpperSupport','RearRibbonGuard','FinishedCarrier','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','skull_mount_Baseplate']:
 v=rib.common(sh[n]).Volume;gap=rib.distToShape(sh[n])[0];report['ribbon'][n]={'overlap_mm3':v,'gap_mm':gap};print('ribbon',n,v,gap,flush=True);(O/'validation.json').write_text(json.dumps(report,indent=2))
for n in ['eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens']:
 v=carrier.common(sh[n]).Volume;prev=old['FinishedCarrier'].common(old[n]).Volume;report['carrier'][n]={'overlap_mm3':v,'previous_mm3':prev};print('carrier',n,v,prev,flush=True)
(O/'validation.json').write_text(json.dumps(report,indent=2));print('BUILT',flush=True)

assert all(v["overlap_mm3"] < 1e-6 for v in report["ribbon"].values()), "Ribbon collision"
assert all(v["overlap_mm3"] <= v["previous_mm3"]+1e-6 for v in report["carrier"].values()), "New carrier collision"
