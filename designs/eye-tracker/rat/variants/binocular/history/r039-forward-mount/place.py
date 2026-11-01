from pathlib import Path
import sys,json,zipfile,hashlib,numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/forward-mount-r39';O=R/'generated/eye-tracker/rat/forward-mount-r39';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import assign
cfg=json.loads((S/'recipe.json').read_text());sel=json.loads((O/'selected-pose.json').read_text());T=np.array(cfg['mount_to_skull']);d=A.openDocument(str(O/'01-forward-mount.FCStd'));ll=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset'])
def read(n):s=Part.Shape();s.read(str(O/(n+'.brep')));return s
def move(s,t):return s.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
assign(d.CentralCarrier,move(read('central'),T))
for side in ['Right','Left']:
 H=np.array(sel['heads_mount'][side]);cam=d.getObject(side+'Camera');cam.Placement=A.Placement(A.Matrix(*T.ravel().tolist()))
 cam.PhysicalParts[0].Shape=Part.makeCompound([read(side+n) for n in ['PCB','camera_pcb']]);cam.PhysicalParts[1].Shape=read(side+'M4_lens');cam.PhysicalParts[2].Shape=Part.makeCompound([read(side+n) for n in ['JST_4pin','IR_LED','IR_LED_001']]);cam.PhysicalParts[3].Shape=read(side+'-ribbon')
 oldH=np.array(cfg['sides'][side].get('previous_head',cfg['sides'][side]['head']));D=H@np.linalg.inv(oldH);axis=cam.OpticalAxis;origin=H[:3,3]+H[:3,:3]@ll;direction=H[:3,2];sensor=D[:3,:3]@np.array(list(axis.SensorCenter))+D[:3,3];axis.Origin=A.Vector(*origin);axis.Direction=A.Vector(*direction);axis.SensorCenter=A.Vector(*sensor);axis.Shape=Part.makeLine(A.Vector(*origin),A.Vector(*(origin+direction*23)));cam.SensorFrame.Placement=A.Placement(A.Vector(*sensor),A.Placement(A.Matrix(*H.ravel().tolist())).Rotation)
 for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:assign(d.getObject(side+tail),move(read(side+tail),T))
 cfg['sides'][side]['previous_head']=oldH.tolist();cfg['sides'][side]['head']=H.tolist();cfg['sides'][side]['head_delta_r38']=D.tolist()
 r=cfg['sides'][side];target=(np.linalg.inv(T)@np.array([8.263833250818816,(-1 if side=='Right' else 1)*8.284849782773964,-6.338181566207952,1]))[:3];delta=target-origin;r.update(eye_target_mount_mm=target.tolist(),lens_mount_mm=origin.tolist(),aim_miss_mm=float(np.linalg.norm(np.cross(delta,direction))),forward_mm=float(delta@direction),head_delta=(H@np.linalg.inv(np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['head']))).tolist(),aim={'axis_miss_mm':float(np.linalg.norm(np.cross(delta,direction))),'forward_distance_mm':float(delta@direction)})
for o in d.Objects:
 if hasattr(o,'Visibility'):o.Visibility=o.TypeId=='App::Part'
for n in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea','CentralCarrier','Baseplate']+[s+t for s in ['Right','Left'] for t in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']]:d.getObject(n).Visibility=True
for side in ['Right','Left']:
 cam=d.getObject(side+'Camera')
 for o in cam.PhysicalParts:o.Visibility=True
 cam.OpticalAxis.Visibility=True
cfg['pose_search']={'candidate_count':len(json.loads((O/'pose-candidates.json').read_text())),'board_reversal':'Not selected: current board poses admit a collision-free developable-sheet route; avoid changing PCB interfaces unnecessarily','selected':sel};(S/'recipe.json').write_text(json.dumps(cfg,indent=2));d.recompute();p=O/'02-camera-and-ribbon-study.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);print('SAVED',sel['axis_miss_mm'],sel['symmetry_error_mm'],sel['ribbon_metric'])
