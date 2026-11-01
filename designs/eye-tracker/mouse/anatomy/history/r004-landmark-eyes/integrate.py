from pathlib import Path
import json,hashlib
import FreeCAD as A,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/mouse/landmark-eye-placement-r14';cfg=json.loads((S/'recipe.json').read_text());src=R/cfg['source']['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg['source']['sha256'];selected=json.loads((S.parent/'active-model.json').read_text());assert hashlib.sha256((R/selected['native_checkpoint']).read_bytes()).hexdigest()==selected['native_sha256']
O=R/'generated/eye-tracker/mouse/landmark-eye-placement-r14';O.mkdir(parents=True,exist_ok=True);poses=json.loads((R/cfg['placement']).read_text());d=A.openDocument(str(src))
def signature(o):
 pose=list(o.getGlobalPlacement().toMatrix().A) if hasattr(o,'getGlobalPlacement') else None
 if hasattr(o,'Shape'):return [pose,hashlib.sha256(o.Shape.exportBrepToString().encode()).hexdigest()]
 if hasattr(o,'Mesh'):return [pose,o.Mesh.CountFacets,str(o.Mesh.BoundBox)]
 return pose
eye_members=set()
stack=[d.Eye1OpticalFrame,d.Eye2OpticalFrame]
while stack:
 o=stack.pop()
 if o.Name in eye_members:continue
 eye_members.add(o.Name);stack.extend(o.OutList)
before={o.Name:signature(o) for o in d.Objects if o.Name not in eye_members};report={'revision':cfg['revision'],'units':'mm','source':cfg['source'],'targeting_recipe':cfg['targeting_recipe'],'eyes':{}}
for row in poses['eyes']:
 name=row['eye'];frame=d.getObject(name+'OpticalFrame');parent=frame.getGlobalPlacement().multiply(frame.Placement.inverse());world=A.Placement(A.Vector(*row['center_world_mm']),A.Rotation(A.Vector(0,0,1),A.Vector(*row['axis_world'])));frame.Placement=parent.inverse().multiply(world)
 frame.AnatomyRevision='landmark-eyes-r04: user-accepted frame; sparse tissue-center fit; nominal ambulatory gaze'
 if hasattr(frame,'FrameDefinition'):frame.FrameDefinition='Origin: tissue-estimated globe center; +Z through corneal apex. See landmark-eyes-r04/placement.json.'
 eye=Mesh.Mesh(str(R/'generated/eye-tracker/mouse/landmark-eyes-r04'/(name+'-whole.stl')));eye.write(str(O/(name+'-world.stl')));report['eyes'][name]={'center_world_mm':row['center_world_mm'],'axis_world':row['axis_world']}
for name,sig in before.items():assert signature(d.getObject(name))==sig,name
report['all_non_eye_shapes_and_poses_unchanged']=True
hardware=Mesh.Mesh()
for name in ['PCB','camera_pcb','JST_4pin','M4_lens','IR_LED','IR_LED_001','RibbonCandidate','FinishedCarrier','eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','skull_mount_Baseplate']:
 o=d.getObject(name);sh=o.Shape.copy();sh.Placement=o.getGlobalPlacement();hardware.addMesh(MeshPart.meshFromShape(Shape=sh,LinearDeflection=.04,AngularDeflection=.15,Relative=False))
skull=Mesh.Mesh(d.Skull.Mesh);skull.transform(d.Skull.getGlobalPlacement().multiply(d.Skull.Placement.inverse()).toMatrix())
atlas=Mesh.Mesh(str(R/'generated/eye-tracker/mouse/landmark-review-r02/detailed-reference.stl'))
for name in ['Eye1','Eye2']:
 eye=Mesh.Mesh(str(O/(name+'-world.stl')))
 for label,m in [('existing_skull',skull),('reference_atlas',atlas),('hardware',hardware)]:
  joined=Mesh.Mesh(eye);n=joined.CountFacets;joined.addMesh(m);cross=sum((v[0]<n)!=(v[1]<n) for v in joined.getSelfIntersections());report['eyes'][name][label+'_surface_crossings']=cross
camera=d.DetailedOpticalAxis;pose=camera.getGlobalPlacement();origin=pose.multVec(camera.Origin);direction=pose.Rotation.multVec(camera.Direction);direction.normalize();target=d.Eye1OpticalFrame.getGlobalPlacement().Base;delta=target-origin;fwd=delta.dot(direction);report['camera_aim']={'forward_mm':fwd,'eye_center_miss_mm':(delta-direction*fwd).Length,'camera_pose_changed':False}
d.recompute();d.Label=cfg['revision']+' - landmark-based eye placement';d.saveAs(str(O/(cfg['revision']+'.FCStd')));(O/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
