"""Integrate adult reference envelopes into hash-pinned complete assemblies."""
from pathlib import Path
import json,hashlib,sys,math
import FreeCAD as A,Mesh,MeshPart,Part
ROOT=Path(__file__).resolve().parents[4]
recipe=Path(sys.argv[1]).resolve();cfg=json.loads(recipe.read_text());sp=cfg['species']
src=ROOT/cfg['source']['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg['source']['sha256']
sel=json.loads((recipe.parent.parent/'active-model.json').read_text());assert hashlib.sha256((ROOT/sel['native_checkpoint']).read_bytes()).hexdigest()==sel['native_sha256']
definition=json.loads((ROOT/cfg['anatomy_definition']).read_text());assets=ROOT/cfg['anatomy_definition'];assets=assets.parent
out=ROOT/'generated/eye-tracker'/sp/recipe.parent.name;out.mkdir(parents=True,exist_ok=True)
d=A.openDocument(str(src))
names=['Eye1','Eye2'] if sp=='mouse' else ['RightEye','LeftEye']
def signature(o):
 pose=list(o.getGlobalPlacement().toMatrix().A) if hasattr(o,'getGlobalPlacement') else None
 if hasattr(o,'Shape'):return [pose,hashlib.sha256(o.Shape.exportBrepToString().encode()).hexdigest()]
 if hasattr(o,'Mesh'):return [pose,o.Mesh.CountFacets,list(o.Mesh.BoundBox.__getstate__()) if False else str(o.Mesh.BoundBox)]
 return pose
exclude=lambda n:any(n.startswith(e) for e in names)
before={o.Name:signature(o) for o in d.Objects if not exclude(o.Name)}
report={'units':'mm','revision':cfg['revision'],'targeting':cfg['targeting_recipe'],'eyes':{}}
for name in names:
 frame=d.getObject(name+'OpticalFrame' if sp=='mouse' else name)
 pose=frame.getGlobalPlacement()
 if sp=='mouse':d.getObject(name).Label+=' — superseded source (hidden)'
 for region in ['sclera','cornea']:
  o=d.getObject(name+region.title())
  if o is None:o=d.addObject('Mesh::Feature',name+region.title());frame.addObject(o)
  o.Mesh=Mesh.Mesh(str(assets/f'{sp}-{region}.stl'));o.Placement=A.Placement()
  o.Label=f'{name} {region} — adult reference envelope'
 axis=d.getObject(name+'OpticalAxis');apex=definition['apex_z_mm'];back=definition['posterior_z_mm'];tip=apex+6
 axis.Shape=Part.makeCompound([Part.makeLine(A.Vector(0,0,back-3),A.Vector(0,0,tip)),Part.makeLine(A.Vector(0,0,tip),A.Vector(.35,0,tip-.8)),Part.makeLine(A.Vector(0,0,tip),A.Vector(-.35,0,tip-.8))])
 axis.CornealApex=A.Vector(0,0,apex);axis.PosteriorPole=A.Vector(0,0,back)
 if not hasattr(frame,'AnatomyRevision'):frame.addProperty('App::PropertyString','AnatomyRevision')
 frame.AnatomyRevision='adult-eyes-r01; representative adult, not sex-specific population median'
 if hasattr(frame,'FrameDefinition'):frame.FrameDefinition='Preserved r02 frame origin; +Z through corneal apex. Origin is prior-envelope centroid, not new volume centroid or measured rotation center.'
 whole=Mesh.Mesh(str(assets/f'{sp}-whole.stl'));whole.transform(pose.toMatrix());whole.write(str(out/f'{name}-world.stl'))
 report['eyes'][name]={'frame_origin_world_mm':list(pose.Base),'axis_world':list(pose.Rotation.multVec(A.Vector(0,0,1))),'apex_world_mm':list(pose.multVec(A.Vector(0,0,apex))),'frame_pose_preserved':True}
for name,sig in before.items():assert signature(d.getObject(name))==sig,name
report['non_eye_geometry_and_placements_unchanged']=True
camera_axis=d.DetailedOpticalAxis;axis_pose=camera_axis.getGlobalPlacement()
origin=axis_pose.multVec(camera_axis.Origin)
direction=axis_pose.Rotation.multVec(camera_axis.Direction);direction.normalize()
target_name='Eye1OpticalFrame' if sp=='mouse' else 'RightEye'
delta=d.getObject(target_name).getGlobalPlacement().Base-origin
forward=delta.dot(direction)
report['camera_aim_to_eye_frame']={'eye_frame':target_name,'forward_distance_mm':forward,
 'miss_distance_mm':(delta-direction*forward).Length,
 'note':'Retained source aim; mouse source target was an inherited surface proxy, not globe center.'}
hardware=Mesh.Mesh()
for name in ['PCB','camera_pcb','JST_4pin','M4_lens','IR_LED','IR_LED_001','RibbonCandidate','FinishedCarrier','eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','skull_mount_Baseplate']:
 o=d.getObject(name);s=o.Shape.copy();s.Placement=o.getGlobalPlacement()
 hardware.addMesh(MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False))
hardware.write(str(out/'hardware-world.stl'))
skull=d.getObject('Skull' if sp=='mouse' else 'StandardSkull')
m=Mesh.Mesh(skull.Mesh);parent=skull.getGlobalPlacement().multiply(skull.Placement.inverse());m.transform(parent.toMatrix());m.write(str(out/'skull-world.stl'))
# Mesh.Points already applies local Placement; only parent transform is required.
for name in names:
 eye=Mesh.Mesh(str(out/f'{name}-world.stl'));count=eye.CountFacets
 row={}
 for label,other in [('hardware',hardware),('skull',m)]:
  combined=Mesh.Mesh(eye);combined.addMesh(other)
  row[label+'_surface_crossings']=sum((a[0]<count)!=(a[1]<count) for a in combined.getSelfIntersections())
 report['eyes'][name].update(row)
 if sp=='rat':
  old=Mesh.Mesh(str(ROOT/'designs/eye-tracker/rat/references/eyes/r02/rat-eye-r02-whole.stl'))
  old.transform(d.getObject(name).getGlobalPlacement().toMatrix())
  old.write(str(out/f'{name}-previous-world.stl'))
  n=old.CountFacets;old.addMesh(m)
  row['previous_skull_surface_crossings']=sum((a[0]<n)!=(a[1]<n) for a in old.getSelfIntersections())
  report['eyes'][name].update(row)
 print(name,row,flush=True)
d.recompute();d.Label=cfg['revision']+' — adult reference eyes';d.saveAs(str(out/(cfg['revision']+'.FCStd')))
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('ADULT_ASSEMBLY_OK',cfg['revision'])
