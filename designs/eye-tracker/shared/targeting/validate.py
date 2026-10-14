"""Validate and export the complete target-driven hardware assembly."""
from pathlib import Path
import json,hashlib
import FreeCAD as A,Part,MeshPart,Mesh
from prepare import checkpoint,placement
from poses import axis_error
import numpy as np

def validate(recipe_path,out):
 cfg=json.loads(Path(recipe_path).read_text());out=Path(out);d=A.openDocument(str(out/(cfg.get('document_name','monocular-rat-targeted-r02')+'.FCStd')));carrier=d.FinishedCarrier.Shape;carrier.check(True);assert carrier.isValid() and len(carrier.Solids)==1;rib=d.RibbonCandidate.Shape;rows={}
 names=['FinishedCarrier','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','skull_mount_Baseplate']
 for parent in ['MeasuredMainPCB','MeasuredSensorHead']:names.extend(o.Name for o in d.getObject(parent).Group)
 for name in names:
  sh=d.getObject(name).Shape;overlap=rib.common(sh).Volume;rows[name]={'ribbon_overlap_mm3':overlap};print(name,'ribbon overlap',overlap,flush=True);assert overlap<1e-6
 source,_=checkpoint(cfg['hardware_manifest']);baseline=A.openDocument(str(source));rigid_clearance={}
 for name in names:
  if name in ['FinishedCarrier','eye_primary_Cap','skull_mount_Baseplate']:continue
  sh=d.getObject(name).Shape;v=carrier.common(sh).Volume;b=baseline.getObject(name);bs=b.Shape.copy();bs.Placement=b.getGlobalPlacement();inherited=baseline.FinishedCarrier.Shape.common(bs).Volume;rigid_clearance[name]={'overlap_mm3':v,'inherited_overlap_mm3':inherited,'gap_mm':carrier.distToShape(sh)[0]};print(name,'carrier overlap',v,'inherited',inherited,flush=True);assert v<=inherited+1e-6
 local_carrier=Part.Shape();local_carrier.read(str(out/'finished.brep'));local_holder=Part.Shape();local_holder.read(str(out/'eye_primary_Holder.brep'))
 parts={'carrier-and-holder':Part.makeCompound([local_carrier,local_holder]),'matching-cap':baseline.eye_primary_Cap.Shape,'camera-clip':baseline.eye_primary_Clip.Shape,'baseplate':baseline.skull_mount_Baseplate.Shape};pr=out/'print';pr.mkdir(exist_ok=True);exports={}
 for name,shape in parts.items():
  m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.12,Relative=False);assert m.isSolid() and not m.hasSelfIntersections(),name;p=pr/(name+'.stl');m.write(str(p));exports[name]={'closed':True,'self_intersections':False,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'facets':m.CountFacets}
 # Pairwise surface intersections with the preserved dense skull, reported separately.
 skull=d.StandardSkull.Mesh;count=skull.CountFacets;anatomy={}
 for name in ['FinishedCarrier','eye_primary_Holder','skull_mount_Baseplate','RibbonCandidate','camera_pcb','M4_lens']:
  sh=d.getObject(name).Shape;mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.06,AngularDeflection=.15,Relative=False);combined=Mesh.Mesh(skull);combined.addMesh(mesh);cross=[x for x in combined.getSelfIntersections() if (x[0]<count)!=(x[1]<count)];anatomy[name]={'skull_surface_crossings':len(cross)};mesh.write(str(out/(name+'-world.stl')));print('skull',name,len(cross),flush=True)
 skull.write(str(out/'skull-world.stl'))
 policy=cfg.get('skull_contact_policy',{})
 assert not (set(policy)-{'skull_mount_Baseplate'}),'Only the tapered baseplate may be Boolean-cut stock'
 for name,row in anatomy.items():
  row['contact_policy']=policy.get(name,'clearance')
  assert row['contact_policy'] in ['clearance','boolean_cut_stock']
  if row['contact_policy']=='clearance':assert row['skull_surface_crossings']==0,name+' crosses skull'
  else:assert row['skull_surface_crossings']>0,'Expected baseplate/skull stock overlap is absent'
 eye_checks={}
 for side in ['Right','Left']:
  eye=Mesh.Mesh()
  for region in ['Sclera','Cornea']:
   obj=d.getObject(side+'Eye'+region);m=Mesh.Mesh(obj.Mesh);m.transform(obj.getGlobalPlacement().toMatrix());eye.addMesh(m)
  count=eye.CountFacets;eye.write(str(out/(side+'Eye-world.stl')))
  for name in ['FinishedCarrier','eye_primary_Holder','RibbonCandidate','camera_pcb','M4_lens']:
   m=MeshPart.meshFromShape(Shape=d.getObject(name).Shape,LinearDeflection=.06,AngularDeflection=.15,Relative=False);combined=Mesh.Mesh(eye);combined.addMesh(m);cross=sum((x[0]<count)!=(x[1]<count) for x in combined.getSelfIntersections());eye_checks[side+'/'+name]=cross
 assert not any(eye_checks.values()),'Hardware crosses eye model'
 arm_checks={}
 for name in ['UpperSupport','RearRibbonGuard']:
  arm=d.getObject(name).Shape;arm_checks[name]={'tray_engagement_mm3':arm.common(d.RetainedPCBTray.Shape).Volume,'socket_engagement_mm3':arm.common(d.RetainedSocket.Shape).Volume};assert min(arm_checks[name].values())>1e-6
 socket_gap=d.RetainedSocket.Shape.distToShape(d.eye_primary_Holder.Shape)[0];baseline_gap=baseline.RetainedSocket.Shape.distToShape(baseline.eye_primary_Holder.Shape)[0];assert abs(socket_gap-baseline_gap)<1e-6
 target=json.loads((out/'target.json').read_text());report={'units':'mm','aim':target['aim'],'carrier_valid':True,'carrier_solids':1,'bop_check':True,'ribbon_checks':rows,'carrier_checks':rigid_clearance,'print_exports':exports,'anatomy_surface_checks':anatomy,'eye_surface_checks':eye_checks,'arm_checks':arm_checks,'socket_holder_gap_mm':socket_gap,'status':'Geometric review candidate; anatomy and physical mounting fit remain provisional'};(out/'validation.json').write_text(json.dumps(report,indent=2));return report

