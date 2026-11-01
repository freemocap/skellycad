"""Create a bilateral complete assembly using proper camera rotation and mirrored printed fixtures."""
from pathlib import Path
import json,hashlib,sys,zipfile
import numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/symmetric-binocular-r37';O=R/'generated/eye-tracker/rat/symmetric-binocular-r37';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):return s.transformed(pose(t).toMatrix())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((S.parent/'compact-binocular-r32/review.json').read_text());assert sha(R/m['native_checkpoint'])==m['native_sha256'];d=A.openDocument(str(R/m['native_checkpoint']))
cfg=json.loads((S.parent/'compact-binocular-r32/recipe.json').read_text());T=np.array(cfg['mount_to_skull']);inv=np.linalg.inv(T)
F=np.diag([1.,-1.,1.,1.]);Fm=inv@F@T
def mirror(s):return s.mirror(A.Vector(*inv[:3,3]),A.Vector(*(inv[:3,:3]@np.array([0.,1.,0.]))))
def local(o):return moved(world(o),inv)
originalH=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['head']);lenslocal=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset'])
oldH=np.array(cfg['sides']['Left']['head']);H=oldH.copy();lens=H[:3,3]+H[:3,:3]@lenslocal;delta=np.eye(4)
assert np.linalg.det(H[:3,:3])>.999999
cfg['sides']['Left'].update(head=H.tolist(),head_delta=(H@np.linalg.inv(originalH)).tolist())
# Keep real camera solids rigid. Only printed holders, clips, sockets and supports are reflected.
for side in ['Right','Left']:
 components={}
 for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
  s=Part.Shape();s.read(str(R/'generated/eye-tracker/rat/compact-binocular-r32'/(side+'-'+n+'.brep')))
  if side=='Left' and n not in ['PCB','JST_4pin']:s=moved(s,delta)
  s.exportBrep(str(O/(side+'-'+n+'.brep')));components[n]=s
 cam=d.getObject(side+'Camera');cam.PhysicalParts[0].Shape=Part.makeCompound([components['PCB'],components['camera_pcb']]);cam.PhysicalParts[1].Shape=components['M4_lens'];cam.PhysicalParts[2].Shape=Part.makeCompound([components[n] for n in ['JST_4pin','IR_LED','IR_LED_001']])
 if side=='Left':cam.SensorFrame.Placement=A.Placement(cam.OpticalAxis.SensorCenter,pose(H).Rotation)
for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket','UpperSupport','LowerSupport']:
 s=mirror(local(d.getObject('Right'+tail)));assign(d.getObject('Left'+tail),moved(s,T))
# A physical camera cannot be reflected. Give both mirrored printed holders the
# same bilateral board clearance; preserve all material outside these pockets.
leftboard=Part.Shape();leftboard.read(str(O/'Left-camera_pcb.brep'));b=moved(leftboard,np.linalg.inv(H)).BoundBox
relief=mirror(moved(Part.makeBox(b.XLength+.3,b.YLength+.3,b.ZLength+.3,A.Vector(b.XMin-.15,b.YMin-.15,b.ZMin-.15)),H))
holder=local(d.Righteye_primary_Holder).cut(relief).removeSplitter()
assert holder.isValid() and len(holder.Solids)==1
assign(d.Righteye_primary_Holder,moved(holder,T));assign(d.Lefteye_primary_Holder,moved(mirror(holder),T))
# Clear the real opposing PCB envelopes at the support roots, symmetrically.
boardcuts=[]
for side in ['Right','Left']:
 s=Part.Shape();s.read(str(O/(side+'-PCB.brep')));boardcuts.extend([s,mirror(s)])
for tail in ['UpperSupport','LowerSupport']:
 arm=local(d.getObject('Right'+tail)).cut(Part.makeCompound(boardcuts)).removeSplitter()
 assert arm.isValid() and len(arm.Solids)==1
 assign(d.getObject('Right'+tail),moved(arm,T));assign(d.getObject('Left'+tail),moved(mirror(arm),T))
# Apply R36's window and label edits to the original central part, preserving those accepted changes.
pm=json.loads((S.parent/'labeled-spine-r36/review.json').read_text());assert sha(R/pm['native_checkpoint'])==pm['native_sha256'];pd=A.openDocument(str(R/pm['native_checkpoint']))
pr=json.loads((R/'generated/eye-tracker/rat/print-r32/hardware-validation.json').read_text());rot=pose(np.array(pr['hardware_world_to_print_rotation']).reshape(4,4));shift=A.Placement(A.Vector(*pr['main_print_translation_mm']),A.Rotation());P=shift.multiply(rot);p_to_m=pose(inv).multiply(P.inverse())
latest=pd.Carrier.Shape.transformed(p_to_m.toMatrix());oldcarrier=local(d.FinishedCarrier);central=local(d.CentralCarrier);central=central.cut(oldcarrier.cut(latest)).fuse(latest.cut(oldcarrier)).removeSplitter();assert central.isValid()
parts=[local(d.getObject(side+tail)) for side in ['Right','Left'] for tail in ['RetainedSocket','UpperSupport','LowerSupport']]
carrier=central.multiFuse(parts).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
assign(d.CentralCarrier,moved(central,T));assign(d.FinishedCarrier,moved(carrier,T));central.exportBrep(str(O/'central.brep'));carrier.exportBrep(str(O/'carrier.brep'))
for side in ['Right','Left']:
 for tail in ['UpperSupport','LowerSupport']:local(d.getObject(side+tail)).exportBrep(str(O/(side+'-'+tail+'.brep')))
cfg.update(revision='ET-RAT-SYMMETRIC-BINOCULAR-R37',source_complete_assembly=m,print_detail_source=pm,symmetry_plane='skull world Y=0',symmetry_policy='Existing symmetric optical poses preserved. Printed head fixtures and support pair reflected exactly from Right, with identical bilateral PCB clearance pockets. No camera geometry reflected.',holder_clearance_mm=.15)
(S/'recipe.json').write_text(json.dumps(cfg,indent=2));d.Label='Rat R37 - symmetric binocular complete assembly';d.recompute();p=O/'aimed.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(pd.Name);A.closeDocument(d.Name);print('PREPARED_SYMMETRIC_HEADS')
