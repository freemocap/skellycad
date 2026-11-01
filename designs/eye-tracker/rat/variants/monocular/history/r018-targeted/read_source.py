from pathlib import Path
import sys,json,hashlib
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/targeted-r18';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
m=json.loads((R/'designs/eye-tracker/mouse/compact-guard-r16/review.json').read_text());p=R/m['native_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(p));s=world(d.skull_mount_Baseplate);print('base faces',[(i+1,round(f.Area,2),list(f.CenterOfMass),str(type(f.Surface))) for i,f in enumerate(s.Faces)]);print('axis',d.DetailedOpticalAxis.PropertiesList);print('axispose',d.DetailedOpticalAxis.Placement);print('head',d.camera_pcb.getGlobalPlacement());s.exportBrep(str(S/'source-baseplate.brep'))
import numpy as np
r=json.loads((R/'designs/eye-tracker/rat/bregma-baseplate-r17/placement.json').read_text());n=np.array(r['plane_normal']);ap=np.array([n[2],0,-n[0]]);F=np.column_stack([ap,[0,1,0],n]);normal=np.array(list(s.Faces[4].normalAt(0,0)));x=np.array([1.,0,0]);C=np.column_stack([x,np.cross(normal,x),normal]);tip=np.array(list(max(s.Faces[4].Vertexes,key=lambda v:v.Point.x).Point));M=np.eye(4);M[:3,:3]=F@C.T;M[:3,3]=np.array(r['rostral_tip_design_mm'])-M[:3,:3]@tip
a=d.DetailedOpticalAxis;p=a.getGlobalPlacement();axis={'origin':list(p.multVec(a.Origin)),'direction':list(p.Rotation.multVec(a.Direction))}
(S/'baseline.json').write_text(json.dumps({'source':m,'mount_to_skull':M.tolist(),'axis':axis,'source_tip':tip.tolist()},indent=2));print('BASELINE',M,axis)
