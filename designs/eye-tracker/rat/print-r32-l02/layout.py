"""Lay the R32 clips on their broad U-profile face without changing geometry."""
from pathlib import Path
import json,hashlib,shutil,zipfile,sys
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-r32-l02';O=R/'generated/eye-tracker/rat/print-r32-l02';OLD=R/'generated/eye-tracker/rat/print-r32';manifest=json.loads((OLD/'manifest.json').read_text())
for name,h in manifest['files'].items():
 p=OLD/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name
 if name.startswith('source/'):continue
 dest=O/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
src=A.openDocument(str(OLD/'RAT-R32-hardware-print.FCStd'));d=A.newDocument('RatR32Layout02');main=src.CarrierAndTwoHolders.Shape.copy();o=d.addObject('Part::Feature','CarrierAndTwoHolders');o.Shape=main;clips=[];report={'layout_revision':'R32 L02','units':'mm','geometry_changes':'Rigid clip rotation and plate placement only','main_mechanism_unchanged':True,'clips':{},'source_manifest_sha256':hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest()}
for side in ['Right','Left']:
 s=src.getObject(side+'Clip').Shape.copy();original=s.copy();faces=[f for f in s.Faces if isinstance(f.Surface,Part.Plane) and len(f.Edges)>=10];assert len(faces)==2
 face=max(faces,key=lambda f:abs(f.normalAt(0,0).y));rotation=A.Rotation(face.normalAt(0,0),A.Vector(0,0,-1));P=A.Placement(A.Vector(),rotation);s.Placement=P.multiply(s.Placement);flat=face.copy();flat.Placement=P.multiply(flat.Placement)
 assert flat.BoundBox.ZLength<1e-6 and abs(flat.BoundBox.ZMin-s.BoundBox.ZMin)<1e-6
 before=s.Volume;s.translate(A.Vector(-s.BoundBox.Center.x,-s.BoundBox.Center.y,-s.BoundBox.ZMin));assert abs(s.Volume-original.Volume)<1e-6 and abs(s.BoundBox.ZLength-3.5)<1e-5
 report['clips'][side]={'rotation_quaternion':list(rotation.Q),'full_U_face_on_bed':True,'contact_face_area_mm2':face.Area,'height_mm':s.BoundBox.ZLength,'footprint_mm':[s.BoundBox.XLength,s.BoundBox.YLength],'volume_mm3':s.Volume,'geometry_volume_delta_mm3':s.Volume-original.Volume}
 for linear,angular in [(.04,.15),(.02,.1)]:
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=linear,AngularDeflection=angular,Relative=False)
  if mesh.isSolid() and not mesh.hasSelfIntersections():break
 assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/'hardware'/('RAT-R32-'+side.lower()+'-clip.stl')));clips.append(s)
# Keep an 8 mm footprint gap from the mechanism and 5 mm between clips.
for i,s in enumerate(clips):
 s.translate(A.Vector(main.BoundBox.XMax+8-s.BoundBox.XMin,(-1 if i==0 else 1)*(s.BoundBox.YLength+5)/2,0));o=d.addObject('Part::Feature',('Right' if i==0 else 'Left')+'Clip');o.Shape=s
 assert abs(s.BoundBox.ZMin)<1e-6 and main.common(s).Volume<1e-7
assert clips[0].distToShape(clips[1])[0]>=5-1e-6
allprint=Part.makeCompound([main,*clips]);mesh=MeshPart.meshFromShape(Shape=allprint,LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/'hardware/RAT-R32-all-hardware.stl'))
report['all_hardware_shells']=len(allprint.Solids);assert report['all_hardware_shells']==5;report['layout_bounds_mm']=[allprint.BoundBox.XLength,allprint.BoundBox.YLength,allprint.BoundBox.ZLength]
d.Label='RAT R32 L02 - clips flat in XY';d.recompute();p=O/'RAT-R32-hardware-print.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
(O/'layout-validation.json').write_text(json.dumps(report,indent=2));(S/'layout-validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(d.Name);A.closeDocument(src.Name);print('FLAT_CLIP_LAYOUT_SAVED',report['clips'])
