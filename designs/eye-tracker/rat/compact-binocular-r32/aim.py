"""Retarget the lowered sensors while preserving complete matched head interfaces."""
from pathlib import Path
import sys,json,zipfile
import numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/compact-binocular-r32';O=R/'generated/eye-tracker/rat/compact-binocular-r32'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
from poses import aim_sensor,axis_error
cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);local=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset']);d=A.openDocument(str(O/'compact-central.FCStd'))
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):
 s=s.copy();s.Placement=pose(t).multiply(s.Placement);return s
for side,rec in cfg['sides'].items():
 old=np.array(rec['head']);e=next(e for e in json.loads((S.parent/'registered-eyes-r14/placement.json').read_text())['eyes'] if e['side']==side);eye=(np.linalg.inv(T)@np.r_[e['center_mm'],1])[:3];lens=old[:3,3]+old[:3,:3]@local;head=aim_sensor(eye,lens,local,old[:3,:3]);delta=head@np.linalg.inv(old);components={}
 for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
  s=Part.Shape();s.read(str(O/(side+'-'+n+'.brep')))
  if n not in ['PCB','JST_4pin']:s=moved(s,delta)
  s.exportBrep(str(O/(side+'-'+n+'.brep')));components[n]=s
 cam=d.getObject(side+'Camera');cam.PhysicalParts[0].Shape=Part.makeCompound([components['PCB'],components['camera_pcb']]);cam.PhysicalParts[1].Shape=components['M4_lens'];cam.PhysicalParts[2].Shape=Part.makeCompound([components[n] for n in ['JST_4pin','IR_LED','IR_LED_001']]);cam.PhysicalParts[3].Shape=Part.Shape()
 cam.OpticalAxis.Shape=Part.makeLine(A.Vector(*lens),A.Vector(*eye));cam.OpticalAxis.Origin=A.Vector(*lens);cam.OpticalAxis.Direction=A.Vector(*head[:3,2]);cam.OpticalAxis.SensorCenter=A.Vector(*(lens-head[:3,2]*1.6076923076925));cam.SensorFrame.Placement=A.Placement(cam.OpticalAxis.SensorCenter,pose(head).Rotation)
 for n in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:
  o=d.getObject(side+n);assign(o,moved(world(o),T@delta@np.linalg.inv(T)))
 rec.update(head=head.tolist(),head_delta=(head@np.linalg.inv(np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['head']))).tolist(),eye_target_mount_mm=eye.tolist(),lens_mount_mm=lens.tolist(),aim=axis_error(head,local,eye))
 rec['aim_miss_mm']=rec['aim']['axis_miss_mm'];rec['forward_mm']=rec['aim']['forward_distance_mm']
 assert rec['aim']['axis_miss_mm']<1e-6
(S/'recipe.json').write_text(json.dumps(cfg,indent=2));d.recompute();p=O/'aimed.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);print('AIMED_AND_SAVED')
