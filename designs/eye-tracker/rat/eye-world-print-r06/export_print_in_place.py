from pathlib import Path
import json,hashlib,zipfile,math,numpy as np
import FreeCAD as A,Part,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-print-r06';O=R/'generated/eye-tracker/rat/eye-world-print-r06';O=O/'print-in-place-v2';O.mkdir(exist_ok=True);P=O/'print-pack';P.mkdir(exist_ok=True)
m=json.loads((S/'review.json').read_text());source=R/m['native_checkpoint'];assert hashlib.sha256(source.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(source));cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull']);H=np.array(json.loads((S/'selected-pose.json').read_text())['head_world']);right=T@np.array(cfg['sides']['Right']['head'])
def world(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
# Minimize the length-weighted out-of-bed component of all four arm tangents.
old=json.loads((R/'generated/eye-tracker/rat/lowered-cameras-r43/04-arms.json').read_text());curves=[np.array(old[n]['poles_mm'])@T[:3,:3].T+T[:3,3] for n in ['RightUpperSupport','RightLowerSupport']]
curves += [np.array(json.loads((O.parent/n).read_text())['poles_world_mm']) for n in ['support-validation.json','second-support-validation.json']]
segments=[]
for poles in curves:
 n=len(poles)-1;points=np.array([sum(math.comb(n,i)*(1-u)**(n-i)*u**i*poles[i] for i in range(n+1)) for u in np.linspace(0,1,101)]);segments.extend(np.diff(points,axis=0))
v=np.array(segments);length=np.linalg.norm(v,axis=1);unit=v/length[:,None];val,vec=np.linalg.eigh((unit*length[:,None]).T@unit);normal=vec[:,0];normal*=np.sign(normal[2]);carrierRot=A.Rotation(A.Vector(*normal),A.Vector(0,0,1));rms=float(np.sqrt(np.average(np.degrees(np.arcsin(np.clip(abs(unit@normal),0,1)))**2,weights=length)))
report={'revision':'RAT W06','units':'mm','source':m,'unsliced':True,'physical_fit_verified':False,'carrier_bed_normal_world':normal.tolist(),'carrier_length_weighted_rms_arm_angle_degrees':rms,'carrier_requires_supports':True,'files':{},'parts':{}}
objects={'carrier':'EyeWorldCarrier','eye-holder':'Righteye_primary_Holder','world-holder':'WorldCameraTopStemTray','eye-clip':'Righteye_primary_Clip','world-clip':'WorldCameraMatchingClip','baseplate':'Baseplate'}
original={k:world(d.getObject(n)) for k,n in objects.items()}
rotations={'carrier':carrierRot,'eye-holder':A.Rotation(A.Vector(*right[:3,0]),A.Vector(0,0,-1)),'world-holder':A.Rotation(A.Vector(*H[:3,2]),A.Vector(0,0,1))}
for name in ['eye-clip','world-clip','baseplate']:
 candidates=[];shape=original[name]
 for face in shape.Faces:
  if not isinstance(face.Surface,Part.Plane):continue
  if 'clip' in name and len(face.Edges)<10:continue
  rot=A.Rotation(face.normalAt(0,0),A.Vector(0,0,-1));mat=A.Placement(A.Vector(),rot).toMatrix();msh=MeshPart.meshFromShape(Shape=shape.transformed(mat),LinearDeflection=.04,AngularDeflection=.15,Relative=False);ff=face.transformed(mat)
  if ff.BoundBox.ZLength<1e-5 and abs(ff.BoundBox.ZMin-msh.BoundBox.ZMin)<1e-4:candidates.append((face.Area,rot))
 assert candidates,name;rotations[name]=max(candidates,key=lambda x:x[0])[1]

report['print_revision']='W06 print-in-place v2';report['joints']={}
for name in ['eye-holder','world-holder']:
 overlap=original['carrier'].common(original[name]).Volume;gap=original['carrier'].distToShape(original[name])[0]
 assert overlap<1e-6 and gap>0,(name,overlap,gap)
 report['joints'][name]={'overlap_mm3':overlap,'minimum_clearance_mm':gap,'relative_pose_preserved':True}
 print('JOINT',name,overlap,gap,flush=True)
plate=A.newDocument('RatW06PrintInPlace');meshes={};placed={}
# The carrier and both captured balls receive ONE rigid transformation.
combined=Part.makeCompound([original[n] for n in ['carrier','eye-holder','world-holder']]);rotmat=A.Placement(A.Vector(),carrierRot).toMatrix();bb=MeshPart.meshFromShape(Shape=combined.transformed(rotmat),LinearDeflection=.04,AngularDeflection=.15,Relative=False).BoundBox
shift=A.Vector(5-bb.XMin,5-bb.YMin,-bb.ZMin);groupmat=A.Placement(shift,carrierRot).toMatrix();x=5.;y=bb.YLength+15
for name,shape in original.items():
 if name in ['carrier','eye-holder','world-holder']:mat=groupmat
 else:
  rot=rotations[name];s=shape.transformed(A.Placement(A.Vector(),rot).toMatrix());bb2=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False).BoundBox;mat=A.Placement(A.Vector(x-bb2.XMin,y-bb2.YMin,-bb2.ZMin),rot).toMatrix();x+=bb2.XLength+10
 s=shape.transformed(mat);assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-shape.Volume)<1e-5
 accepted=None
 for lin,ang in [(.04,.15),(.02,.1),(.08,.2),(.03,.12),(.05,.15),(.01,.08),(.06,.18),(.1,.25),(.025,.13),(.035,.16),(.045,.17),(.015,.09)]:
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
  if mesh.isSolid() and not mesh.hasSelfIntersections():accepted=mesh;break
 assert accepted is not None,('Mesh defect',name)
 meshes[name]=accepted;placed[name]=s;obj=plate.addObject('Part::Feature',name.replace('-','_'));obj.Shape=s
 report['parts'][name]={'world_to_print_matrix':list(mat.A),'linear_deflection_mm':lin,'angular_deflection_rad':ang,'volume_mm3':shape.Volume}
 print('MESH',name,len(mesh.Topology[1]),flush=True)
for name in ['eye-holder','world-holder']:
 gap=placed['carrier'].distToShape(placed[name])[0];assert abs(gap-report['joints'][name]['minimum_clearance_mm'])<1e-6
 report['joints'][name]['print_clearance_mm']=gap
names=list(meshes)
groups={'carrier-with-captive-holders':names[:3],'all-hardware':names,'hardware-without-baseplate':names[:-1],'eye-clip':['eye-clip'],'world-clip':['world-clip'],'baseplate':['baseplate']}
for label,parts in groups.items():
 mesh=Mesh.Mesh()
 for n in parts:mesh.addMesh(meshes[n])
 assert mesh.isSolid() and not mesh.hasSelfIntersections(),label
 p=P/('RAT-W06-PIP-'+label+'.stl');mesh.write(str(p));test=Mesh.Mesh(str(p));assert test.isSolid() and not test.hasSelfIntersections(),label
 report['files'][p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'shell_count':len(parts)}
layout=Mesh.Mesh()
for mesh in meshes.values():layout.addMesh(mesh)
report['layout_bounds_mm']=[layout.BoundBox.XLength,layout.BoundBox.YLength,layout.BoundBox.ZLength];report['clips_flat']=True;report['assembled_print_group_shell_count']=3
plate.Label='RAT W06 - print in place';plate.recompute();p=O/'RAT-W06-print-in-place.FCStd';plate.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
(O/'print-validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(plate.Name);A.closeDocument(d.Name);print('PASS',flush=True)
