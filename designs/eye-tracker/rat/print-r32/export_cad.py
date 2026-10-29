"""Export exact R32 matched rigid hardware and anatomy inputs for a trial print."""
from pathlib import Path
import json,hashlib,zipfile,sys
import numpy as np
import FreeCAD as A,Part,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-r32';O=R/'generated/eye-tracker/rat/print-r32';H=O/'hardware'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
m=json.loads((S.parent/'compact-binocular-r32/review.json').read_text());p=R/m['native_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(p));cfg=json.loads((S.parent/'compact-binocular-r32/recipe.json').read_text());report={'source':m,'units':'mm','geometry_changes':'None; rigid print placement only','physical_fit_verified':False,'unsliced':True,'parts':{}}
for n in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 o=d.getObject(n);mesh=o.Mesh.copy();mesh.transform(o.getGlobalPlacement().multiply(o.Placement.inverse()).toMatrix());mesh.write(str(O/(n+'.stl')))
base=world(d.Baseplate);MeshPart.meshFromShape(Shape=base,LinearDeflection=.02,AngularDeflection=.1,Relative=False).write(str(O/'baseplate-world.stl'))
T=A.Placement(A.Matrix(*sum(cfg['mount_to_skull'],[])));inv=T.inverse();orientation=A.Placement(A.Vector(),A.Rotation(A.Vector(0,1,0),-90))
def oriented(s):return s.transformed(orientation.multiply(inv).toMatrix())
carrier=oriented(world(d.FinishedCarrier));holders=[oriented(world(d.getObject(side+'eye_primary_Holder'))) for side in ['Right','Left']]
assert all(carrier.common(h).Volume<1e-6 for h in holders)
main=Part.makeCompound([carrier,*holders]);b=main.BoundBox;translation=A.Vector(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,-b.ZMin)
report['hardware_world_to_print_rotation']=list(orientation.multiply(inv).toMatrix().A);report['main_print_translation_mm']=list(translation);report['main_print_shells']=3
printdoc=A.newDocument('RAT_R32_hardware_print')
def export(name,shape,expected,common_shift=None):
 s=shape.copy();v=common_shift if common_shift is not None else A.Vector(-s.BoundBox.Center.x,-s.BoundBox.Center.y,-s.BoundBox.ZMin);s.translate(v)
 assert s.isValid() and len(s.Solids)==expected,name
 for linear,angular in [(.04,.15),(.02,.10),(.08,.2)]:
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=linear,AngularDeflection=angular,Relative=False)
  if mesh.isSolid() and not mesh.hasSelfIntersections():break
 assert mesh.isSolid() and not mesh.hasSelfIntersections(),name
 f=H/(name+'.stl');mesh.write(str(f));report['parts'][name]={'shells':expected,'volume_mm3':s.Volume,'bounds_mm':[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength],'closed':True,'self_intersections':False,'linear_deflection_mm':linear,'angular_deflection_rad':angular,'initial_cad_export_sha256':hashlib.sha256(f.read_bytes()).hexdigest()};return s
mainprint=export('RAT-R32-carrier-and-two-holders',main,3,translation)
export('RAT-R32-carrier',carrier,1)
for side,holder in zip(['right','left'],holders):export('RAT-R32-'+side+'-holder',holder,1)
clips=[]
for side in ['Right','Left']:
 head=A.Placement(A.Matrix(*sum(cfg['sides'][side]['head'],[])));clip=world(d.getObject(side+'eye_primary_Clip')).transformed(head.inverse().multiply(inv).toMatrix());clips.append(export('RAT-R32-'+side.lower()+'-clip',clip,1))
# Keep the two clips detached from the mechanism, arranged beside it on the bed.
clips[0].translate(A.Vector(mainprint.BoundBox.XMax+8-clips[0].BoundBox.XMin,0,0));clips[1].translate(A.Vector(mainprint.BoundBox.XMax+8-clips[1].BoundBox.XMin,clips[0].BoundBox.YLength+5,0))
allprint=Part.makeCompound([mainprint,*clips]);export('RAT-R32-all-hardware',allprint,5,A.Vector())
export('RAT-R32-baseplate-optional',base,1)
for name,s in [('CarrierAndTwoHolders',mainprint),('RightClip',clips[0]),('LeftClip',clips[1])]:o=printdoc.addObject('Part::Feature',name);o.Shape=s
printdoc.Label='RAT R32 - hardware trial-print layout';printdoc.recompute();p=O/'RAT-R32-hardware-print.FCStd';printdoc.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
(O/'hardware-validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(printdoc.Name);A.closeDocument(d.Name);print('R32_HARDWARE_EXPORTED',report['parts']['RAT-R32-all-hardware']['bounds_mm'])

