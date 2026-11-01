from pathlib import Path
import sys,json,hashlib,numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-top-joint-r04';O=R/'generated/eye-tracker/rat/eye-world-top-joint-r04';P=R/'generated/eye-tracker/rat/eye-world-tray-r03'
c=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(c['mount_to_skull']);H=np.array(json.loads((S/'selected-pose.json').read_text())['head_world']);old=T@np.array(c['sides']['Left']['head']);m=json.loads((S.parent/'lowered-cameras-r43/review.json').read_text());assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(R/m['native_checkpoint']))
def move(sh,t):return sh.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
def world(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s

def read(n):
 s=Part.Shape();s.read(str(P/(n+'.brep')));return s
parts=[move(world(d.getObject(n)),np.linalg.inv(T)) for n in ['CentralCarrier','RightUpperSupport','RightLowerSupport','RightRetainedSocket']];carrier=parts[0].multiFuse(parts[1:]).removeSplitter();print('CLEAN',carrier.Volume,carrier.isValid(),len(carrier.Solids),flush=True);assert carrier.isValid() and len(carrier.Solids)==1;move(carrier,T).exportBrep(str(O/'clean-carrier.brep'))
orig=read('source-holder-head');tray=read('stemless-tray-head');stem=orig.common(Part.makeBox(100,100,30,A.Vector(-50,-50,-31.2501))).removeSplitter();print('stem',stem.Volume,len(stem.Solids),flush=True)
# Rotate the existing back-facing stem upward about its attachment region.
J=np.eye(4);J[:3,:3]=np.array([[0,0,-1],[0,1,0],[1,0,0]]);anchor=np.array([3.09436,6.76724,-1.24998]);landing=np.array([4.35,6.76724,-.65]);J[:3,3]=landing-J[:3,:3]@anchor
up=move(stem,J);holder=tray.fuse(up).removeSplitter();print('HOLDER',holder.Volume,holder.isValid(),len(holder.Solids),flush=True);assert holder.isValid() and len(holder.Solids)==1
socket=move(world(d.LeftRetainedSocket),np.linalg.inv(old));socket=move(socket,J)
for name,sh in [('top-stem-holder',holder),('top-socket',socket)]:
 sh=move(sh,H);print(name,sh.BoundBox,flush=True);sh.exportBrep(str(O/(name+'.brep')))
(O/'joint-transform.json').write_text(json.dumps({'head_stem_transform':J.tolist(),'stem_anchor_original_mm':anchor.tolist(),'stem_landing_head_mm':landing.tolist()},indent=2))
A.closeDocument(d.Name)

