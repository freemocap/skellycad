from pathlib import Path
import json,hashlib,zipfile,math,numpy as np
import FreeCAD as A,Part,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-print-r06';O=R/'generated/eye-tracker/rat/eye-world-print-r06';P=O/'print-pack';P.mkdir(exist_ok=True)
m=json.loads((S/'review.json').read_text());source=R/m['native_checkpoint'];assert hashlib.sha256(source.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(source));cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull']);H=np.array(json.loads((S/'selected-pose.json').read_text())['head_world']);right=T@np.array(cfg['sides']['Right']['head'])
def world(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
# Minimize the length-weighted out-of-bed component of all four arm tangents.
old=json.loads((R/'generated/eye-tracker/rat/lowered-cameras-r43/04-arms.json').read_text());curves=[np.array(old[n]['poles_mm'])@T[:3,:3].T+T[:3,3] for n in ['RightUpperSupport','RightLowerSupport']]
curves += [np.array(json.loads((O/n).read_text())['poles_world_mm']) for n in ['support-validation.json','second-support-validation.json']]
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
plate=A.newDocument('RatW06PrintPlate');placed=[];meshes=[];x=5.;y=30.;rowheight=0.
for name,shape in original.items():
 if name=='world-holder':
  s=Part.Shape();s.read(str(O/'stable-world-holder-print.brep'));stable=json.loads((O/'stable-holder-print.json').read_text());shift=A.Vector(*stable['translation']);rotations[name]=A.Rotation(A.Matrix(*np.linalg.inv(H).ravel().tolist()))
 else:
  s=shape.transformed(A.Placement(A.Vector(),rotations[name]).toMatrix());m0=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False);bb=m0.BoundBox
  if x+bb.XLength>180:x=5.;y+=rowheight+8;rowheight=0
  shift=A.Vector(x-bb.XMin,y-bb.YMin,-bb.ZMin);s.translate(shift);x+=bb.XLength+8;rowheight=max(rowheight,bb.YLength)
 assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-shape.Volume)<1e-5
 accepted=None
 for lin,ang in [(.04,.15),(.02,.1),(.08,.2),(.03,.12),(.05,.15),(.01,.08),(.06,.18),(.1,.25)]:
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
  if mesh.isSolid() and not mesh.hasSelfIntersections():accepted=mesh;break
 assert accepted is not None,('Export mesh defect',name)
 # Individual files retain their plate positions so they import as matched parts.
 path=P/('RAT-W06-'+name+'.stl');accepted.write(str(path));reload=Mesh.Mesh(str(path));assert reload.isSolid() and not reload.hasSelfIntersections(),name
 report['parts'][name]={'rotation_xyzw':list(rotations[name].Q),'translation_mm':list(shift),'closed':True,'self_intersections':False,'volume_mm3':shape.Volume,'bounds_mm':[accepted.BoundBox.XLength,accepted.BoundBox.YLength,accepted.BoundBox.ZLength],'z_min_mm':accepted.BoundBox.ZMin,'linear_deflection_mm':lin,'angular_deflection_rad':ang}
 transform=np.eye(4);mat=A.Placement(shift,rotations[name]).toMatrix();transform=np.array(mat.A).reshape(4,4)
 if name=='world-holder':transform=np.linalg.inv(H);transform[:3,3]+=np.array(list(shift));report['parts'][name]['translation_mm']=transform[:3,3].tolist()
 report['parts'][name]['world_to_print_matrix']=transform.tolist()
 obj=plate.addObject('Part::Feature',name.replace('-','_'));obj.Shape=s;placed.append(s);meshes.append(accepted);print('STL',name,len(accepted.Topology[1]),flush=True)
allmesh=Mesh.Mesh()
for mesh in meshes:allmesh.addMesh(mesh)
assert allmesh.isSolid() and not allmesh.hasSelfIntersections();allmesh.write(str(P/'RAT-W06-all-hardware.stl'))
nomount=Mesh.Mesh()
for mesh in meshes[:-1]:nomount.addMesh(mesh)
nomount.write(str(P/'RAT-W06-hardware-without-baseplate.stl'))
for filename in ['RAT-W06-all-hardware.stl','RAT-W06-hardware-without-baseplate.stl']:
 mesh=Mesh.Mesh(str(P/filename));assert mesh.isSolid() and not mesh.hasSelfIntersections()
report['all_hardware_shells']=6;report['layout_bounds_mm']=[allmesh.BoundBox.XLength,allmesh.BoundBox.YLength,allmesh.BoundBox.ZLength];report['clips_flat']=True
plate.Label='RAT W06 - hardware print layout';plate.recompute();p=O/'RAT-W06-print-layout.FCStd';plate.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
for p in P.glob('*.stl'):report['files'][p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
(O/'print-validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(plate.Name);A.closeDocument(d.Name);print('PRINT_EXPORT_PASS',report['layout_bounds_mm'],rms,flush=True)
