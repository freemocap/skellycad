from pathlib import Path
import sys,json,hashlib,zipfile
import numpy as np
import FreeCAD as A
R=Path.cwd();S=R/'designs/eye-tracker/rat/forward-mount-r39';O=R/'generated/eye-tracker/rat/forward-mount-r39';P=S.parent/'refined-supports-r38';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
m=json.loads((P/'review.json').read_text());p=R/m['native_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(p));cfg=json.loads((P/'recipe.json').read_text())
o=d.RatDesignSkull;mesh=o.Mesh.copy();mesh.transform(o.getGlobalPlacement().multiply(o.Placement.inverse()).toMatrix());mesh.write(str(O/'skull.stl'));pts,faces=mesh.Topology;tri=np.array([list(v) for v in pts])[np.array(faces)]
def roof(x,y):
 a=tri[:,0,:2];e=tri[:,1,:2]-a;f=tri[:,2,:2]-a;b=np.array([x,y])-a;det=e[:,0]*f[:,1]-e[:,1]*f[:,0];good=abs(det)>1e-10;u=np.divide(b[:,0]*f[:,1]-b[:,1]*f[:,0],det,out=np.zeros(len(det)),where=good);v=np.divide(e[:,0]*b[:,1]-e[:,1]*b[:,0],det,out=np.zeros(len(det)),where=good);good&=(u>=0)&(v>=0)&(u+v<=1);z=tri[:,0,2]+u*(tri[:,1,2]-tri[:,0,2])+v*(tri[:,2,2]-tri[:,0,2]);return float(max(z[good]))
base=world(d.Baseplate);x=base.BoundBox.Center.x;dz=roof(x+9,0)-roof(x,0);delta=A.Vector(9,0,dz)
# Move the mount assembly rigidly as the provisional forward-seat study; cameras will be solved next.
for o in d.Objects:
 if o.TypeId=='App::Part' and o.Name in ['RightCamera','LeftCamera']:o.Placement.Base+=delta
for n in ['Baseplate','CentralCarrier','FinishedCarrier']+[side+tail for side in ['Right','Left'] for tail in ['RetainedSocket','UpperSupport','LowerSupport','eye_primary_Holder','eye_primary_Clip']]:
 o=d.getObject(n);s=world(o);s.translate(delta);assign(o,s)
T=np.array(cfg['mount_to_skull']);T[:3,3]+=list(delta);cfg['mount_to_skull']=T.tolist();cfg['revision']='ET-RAT-FORWARD-MOUNT-R39';cfg['source_complete_assembly']=m;cfg['forward_mount']={'translation_world_mm':list(delta),'roof_height_before_mm':roof(x,0),'roof_height_after_mm':roof(x+9,0),'baseplate_geometry_unchanged':True,'seating':'Provisional roof-height matched placement; preserve intentional Boolean-cut stock; physical seating unverified'}
d.recompute();p=O/'01-forward-mount.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
(S/'recipe.json').write_text(json.dumps(cfg,indent=2));(O/'01-forward-mount.json').write_text(json.dumps(cfg['forward_mount'],indent=2));A.closeDocument(d.Name);print(cfg['forward_mount'])
