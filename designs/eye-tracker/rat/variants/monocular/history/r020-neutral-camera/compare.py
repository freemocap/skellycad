from pathlib import Path
import sys,json,hashlib
import FreeCAD as A
import numpy as np
R=Path.cwd();S=R/'designs/eye-tracker/rat/neutral-camera-r20';O=R/'generated/eye-tracker/rat/neutral-camera-r20'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
from replace_camera import world
m=json.loads((S.parent/'compact-guard-r19/review.json').read_text());assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
old=A.openDocument(str(R/m['native_checkpoint']));new=A.openDocument(str(O/'ET-RAT-NEUTRAL-R20.FCStd'))
sol=json.loads((S/'solution.json').read_text());prior=json.loads((S.parent/'targeted-r18/solution.json').read_text());M=np.array(sol['mount_to_skull']);D=M@np.array(sol['head'])@np.linalg.inv(prior['head'])@np.linalg.inv(M);matrix=A.Matrix(*D.ravel().tolist())
report={'fixed':{},'moved_as_rigid_group':{}}
for group,names in [('fixed',['PCB','JST_4pin','eye_primary_Cap','skull_mount_Baseplate','RetainedPCBTray']),('moved_as_rigid_group',['camera_pcb','M4_lens','IR_LED','IR_LED_001','eye_primary_Holder','eye_primary_Clip','RetainedSocket'])]:
 for name in names:
  a=world(old.getObject(name));b=world(new.getObject(name))
  if group=='moved_as_rigid_group':a=a.transformed(matrix)
  error=a.cut(b).Volume+b.cut(a).Volume
  report[group][name]={'difference_mm3':error};assert error<1e-5,(name,error)
for name in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 a=old.getObject(name);b=new.getObject(name);assert a.Mesh.Topology==b.Mesh.Topology
report['anatomy_unchanged']=True
(O/'r19-comparison.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
