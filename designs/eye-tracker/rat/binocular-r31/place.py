"""Create the binocular R31 placement candidate from verified R30 inputs."""
from pathlib import Path
import json,sys,hashlib,zipfile
import numpy as np
import FreeCAD as A,Part,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/binocular-r31';O=R/'generated/eye-tracker/rat/binocular-r31';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
from replace_camera import world
sys.path.insert(0,str(R/'designs/eye-tracker'))
from shared.camera import add_camera
baseline=json.loads((S/'baseline.json').read_text());m=baseline['source'];assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
sol=json.loads((S.parent/'oval-camera-r21/solution.json').read_text());T=np.array(sol['mount_to_skull']);H=np.array(sol['head']);F=np.diag([1.,1.,-1.,1.]);F[2,3]=2*T[1,3];localflip=np.diag([-1,1,1,1]);HL=F@H@localflip
# Reflect the optical location, preserving real camera handedness via a proper rotation.
lenslocal=np.array(sol['lens_local_offset']);targetlens=(F@np.r_[sol['lens'],1])[:3];HL[:3,3]=targetlens-HL[:3,:3]@lenslocal
B=np.eye(4);B[1,3]=4.;BL=np.diag([-1.,1.,-1.,1.]);BL[:3,3]=[2*5.28706399647303-4,4,2*T[1,3]]
recipe={'revision':'ET-RAT-BINOCULAR-R31','units':'mm','source':m,'selected_species_manifest':'designs/eye-tracker/rat/active-model.json','selected_hash_mismatch':baseline['selected'],'mount_to_skull':T.tolist(),'board_back_gap_mm':4.,'board_raise_mount_y_mm':4.,'cap':'omitted','physical_fit_verified':False,'print_release':False,'sides':{}}
src=A.openDocument(str(R/m['native_checkpoint']));d=A.newDocument('RatBinocularR31');d.Label='Rat R31 - uncapped binocular candidate'
def placement(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(sh,t):
 s=sh.copy();s.Placement=placement(t).multiply(s.Placement);return s
sh={n:world(src.getObject(n)).transformed(placement(T).inverse().toMatrix()) for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','eye_primary_Holder','eye_primary_Clip','RetainedSocket','RetainedPCBTray','UpperSupport','RearRibbonGuard','RibbonCandidate','skull_mount_Baseplate']}
def put(n,s):
 o=d.addObject('Part::Feature',n);o.Shape=moved(s,T);return o
for n in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 ob=src.getObject(n);o=d.addObject('Mesh::Feature',n);o.Mesh=ob.Mesh.copy();o.Placement=ob.getGlobalPlacement()
put('Baseplate',sh['skull_mount_Baseplate'])
for side,board,head in [('Right',B,H),('Left',BL,HL)]:
 delta=head@np.linalg.inv(H);eye=np.array(sol['eye_mount_frame']) if side=='Right' else (F@np.r_[sol['eye_mount_frame'],1])[:3];lens=head[:3,3]+head[:3,:3]@lenslocal;axis=head[:3,2]
 # Load the selected complete module through the shared entry point, then articulate its verified parts.
 cam=add_camera(d,side+'Camera');cam.Placement=placement(T)
 components={n:moved(sh[n],board if n in ['PCB','JST_4pin'] else delta) for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']}
 for ob,shape in zip(cam.PhysicalParts,[Part.makeCompound([components['PCB'],components['camera_pcb']]),components['M4_lens'],Part.makeCompound([components[n] for n in ['JST_4pin','IR_LED','IR_LED_001']]),Part.Shape()]):ob.Shape=shape
 cam.OpticalAxis.Shape=Part.makeLine(A.Vector(*lens),A.Vector(*eye));cam.OpticalAxis.Origin=A.Vector(*lens);cam.OpticalAxis.Direction=A.Vector(*axis);cam.OpticalAxis.SensorCenter=A.Vector(*(lens-axis*1.6076923076925));cam.SensorFrame.Placement=A.Placement(cam.OpticalAxis.SensorCenter,placement(head).Rotation)
 for n in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:put(side+n,moved(sh[n],delta))
 # Save separate physical solids for exhaustive collision validation.
 for n,s in components.items():s.exportBrep(str(O/(side+'-'+n+'.brep')))
 recipe['sides'][side]={'board_transform':board.tolist(),'head':head.tolist(),'head_delta':delta.tolist(),'eye_target_mount_mm':eye.tolist(),'lens_mount_mm':lens.tolist(),'aim_miss_mm':float(np.linalg.norm(np.cross(eye-lens,axis))),'forward_mm':float((eye-lens)@axis),'rotation_determinant':float(np.linalg.det(head[:3,:3])),'connector_access':'Outward from each PCB face; uncapped, no outer closure'}
 assert recipe['sides'][side]['aim_miss_mm']<.01 and recipe['sides'][side]['forward_mm']>0 and np.linalg.det(head[:3,:3])>.99999
(S/'recipe.json').write_text(json.dumps(recipe,indent=2));d.recompute();p=O/'placement.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);A.closeDocument(src.Name);print('PLACEMENT_SAVED',json.dumps(recipe['sides']))

