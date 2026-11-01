from support import *
from detailed_ribbon import ribbon_solid
import hashlib
m=cfg['source_complete_assembly'];assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
baseline_cfg=json.loads((S.parent/'orthogonal-arms-r42/recipe.json').read_text());d=load('source');old=R/'generated/eye-tracker/rat/orthogonal-arms-r42';rec=json.loads((O/'pose-candidates.json').read_text())[0];ll=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset']);obs={'central':local(d.CentralCarrier)};metrics={};heads={};cones={};ribs={}
for i,side in enumerate(['Right','Left']):
 H=inv@np.array(rec['heads_world'][i]);D=H@np.linalg.inv(np.array(baseline_cfg['sides'][side]['head']));heads[side]=H.tolist()
 for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
  s=Part.Shape();s.read(str(old/(side+n+'.brep')));obs[side+n]=s if n in ['PCB','JST_4pin'] else moved(s,D)
 for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:
  obs[side+tail]=moved(local(d.getObject(side+tail)),D)
 rib,mesh,metric=ribbon_solid(rec['parameters'][i*12:(i+1)*12],nx=6,ny=132);ribs[side]=moved(rib,np.array(cfg['sides'][side]['board_transform']));metrics[side]=metric
 cam=d.getObject(side+'Camera');cam.Placement=pose(T)
 cam.PhysicalParts[0].Shape=Part.makeCompound([obs[side+n] for n in ['PCB','camera_pcb']]);cam.PhysicalParts[1].Shape=obs[side+'M4_lens'];cam.PhysicalParts[2].Shape=Part.makeCompound([obs[side+n] for n in ['JST_4pin','IR_LED','IR_LED_001']]);cam.PhysicalParts[3].Shape=ribs[side]
 lens=H[:3,3]+H[:3,:3]@ll;axis=H[:3,2];sensor=D[:3,:3]@np.array(list(cam.OpticalAxis.SensorCenter))+D[:3,3];cam.OpticalAxis.Origin=A.Vector(*lens);cam.OpticalAxis.Direction=A.Vector(*axis);cam.OpticalAxis.SensorCenter=A.Vector(*sensor);cam.OpticalAxis.Shape=Part.makeLine(A.Vector(*lens),A.Vector(*(lens+axis*28)));cam.SensorFrame.Placement=A.Placement(A.Vector(*sensor),pose(H).Rotation)
 for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:assign(d.getObject(side+tail),moved(obs[side+tail],T))
 target=(inv@np.array([8.263833250818816,(-1 if side=='Right' else 1)*8.284849782773964,-6.338181566207952,1]))[:3];dist=np.linalg.norm(target-lens)
 front=moved(obs[side+'M4_lens'],np.linalg.inv(H)).BoundBox.ZMax-ll[2]+.05
 cones[side]=Part.makeCone(2.25,5.75,float(dist-front),A.Vector(*(lens+axis*front)),A.Vector(*axis))
 cfg['view_policy']['front_offset_from_optical_datum_mm']=float(front)
 cfg['sides'][side].update(previous_head=baseline_cfg['sides'][side]['head'],head=H.tolist(),lens_mount_mm=lens.tolist(),eye_target_mount_mm=target.tolist())
report={'ribbon_collisions':{},'view_obstructions':{},'metrics':metrics,'passed':False}
for side,rib in ribs.items():
 for n,s in obs.items():
  if not rib.BoundBox.intersect(s.BoundBox):continue
  v=rib.common(s).Volume
  if v>1e-5:report['ribbon_collisions'][side+'/'+n]=v
for side,cone in cones.items():
 for n,s in dict(obs,**{k+'-ribbon':v for k,v in ribs.items()}).items():
  if not cone.BoundBox.intersect(s.BoundBox):continue
  v=cone.common(s).Volume
  if v>1e-5:report['view_obstructions'][side+'/'+n]=v
report['passed']=not report['ribbon_collisions'] and not report['view_obstructions'];print('CHECKS',report,flush=True);(O/'02-checks.json').write_text(json.dumps(report,indent=2))
assert not report['ribbon_collisions'] and not report['view_obstructions']
for n,s in obs.items():s.exportBrep(str(O/(n+'.brep')))
for side,s in ribs.items():s.exportBrep(str(O/(side+'-ribbon.brep')))
for side,s in cones.items():
 s.exportBrep(str(O/(side+'-view-keepout.brep')))
 moved(Part.makeBox(15,19,14.8,A.Vector(-7.5,-1.5,-6.8)),np.array(heads[side])).exportBrep(str(O/(side+'-camera-access-keepout.brep')))
for o in d.Objects:o.Visibility=o.TypeId=='App::Part'
for n in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea','CentralCarrier','Baseplate']+[s+t for s in ['Right','Left'] for t in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']]:d.getObject(n).Visibility=True
for side in ['Right','Left']:
 for o in d.getObject(side+'Camera').PhysicalParts:o.Visibility=True
 d.getObject(side+'Camera').OpticalAxis.Visibility=True
 for tail in ['UpperSupport','LowerSupport']:
  if d.getObject(side+tail):d.removeObject(side+tail)
  o=d.addObject('PartDesign::Feature',side+tail);o.Visibility=False
report['passed']=True;cfg['left_fixture_reflection']={'head_frame_normal':[1,0,0],'plane_x_mm':float(ll[0]),'parts':['eye_primary_Holder','eye_primary_Clip','RetainedSocket'],'camera_electronics_reflected':False};cfg['pose_search']=rec;cfg['ribbon_metric']=metrics;(S/'recipe.json').write_text(json.dumps(cfg,indent=2));(S/'selected-pose.json').write_text(json.dumps(rec,indent=2));d.recompute();d.saveAs(str(O/'04-arms-working.FCStd'));save(d,'02-camera-and-ribbon-study',report)
