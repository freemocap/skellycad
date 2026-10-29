"""Check bilateral head geometry, all physical collisions and anatomical crossings."""
from pathlib import Path
import json,sys,hashlib,zipfile,itertools
import numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/symmetric-binocular-r37';O=R/'generated/eye-tracker/rat/symmetric-binocular-r37';E=O/'validation-meshes';E.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);d=A.openDocument(str(O/'ribbons.FCStd'));src=A.openDocument(str(R/cfg['source_complete_assembly']['native_checkpoint']))
def moved(s,t):return s.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
F=np.diag([1.,-1.,1.,1.]);sh={'Carrier':world(d.FinishedCarrier),'Baseplate':world(d.Baseplate)};prior={'Carrier':world(src.FinishedCarrier),'Baseplate':world(src.Baseplate)}
report={'units':'mm','passed':False,'symmetry':{},'aim':{},'interferences':{},'mesh_checks':{},'anatomy_crossings':{},'seating':{},'physical_fit_verified':False,'print_release':False}
for side,rec in cfg['sides'].items():
 cam=d.getObject(side+'Camera');lens=cam.getGlobalPlacement().multVec(cam.OpticalAxis.Origin);axis=cam.getGlobalPlacement().Rotation.multVec(cam.OpticalAxis.Direction)
 eye=A.Vector(*next(e['center_mm'] for e in json.loads((S.parent/'registered-eyes-r14/placement.json').read_text())['eyes'] if e['side']==side));off=eye-lens
 report['aim'][side]={'lens_world_mm':list(lens),'axis_world':list(axis),'miss_mm':off.cross(axis).Length,'stand_off_mm':off.Length,'forward_mm':off.dot(axis)};assert off.cross(axis).Length<1e-6 and off.dot(axis)>0
 for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','ribbon']:
  s=Part.Shape();s.read(str(O/(side+'-'+n+'.brep')));sh[side+n]=moved(s,T)
  s=Part.Shape();s.read(str(R/'generated/eye-tracker/rat/compact-binocular-r32'/(side+'-'+n+'.brep')));prior[side+n]=moved(s,T)
 for n in ['eye_primary_Holder','eye_primary_Clip']:
  sh[side+n]=world(d.getObject(side+n));prior[side+n]=world(src.getObject(side+n))
 for n in ['UpperSupport','LowerSupport']:
  arm=world(d.getObject(side+n));seat={'central_mm3':arm.common(world(d.CentralCarrier)).Volume,'socket_mm3':arm.common(world(d.getObject(side+'RetainedSocket'))).Volume};assert min(seat.values())>.1;report['seating'][side+n]=seat
for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket','UpperSupport','LowerSupport']:
 print('CHECK_SYMMETRY',tail,flush=True)
 a=world(d.getObject('Right'+tail)).mirror(A.Vector(),A.Vector(0,1,0));b=world(d.getObject('Left'+tail));v=a.cut(b).Volume+b.cut(a).Volume;assert v<1e-5,(tail,v);report['symmetry'][tail+'_difference_mm3']=v
for key in ['lens_world_mm','axis_world']:
 a=np.array(report['aim']['Right'][key])*[1,-1,1];b=np.array(report['aim']['Left'][key]);err=float(np.linalg.norm(a-b));assert err<1e-6;report['symmetry'][key+'_reflection_error']=err
RH=(T@np.array(cfg['sides']['Right']['head']))[:3,:3];LH=(T@np.array(cfg['sides']['Left']['head']))[:3,:3]
assert np.max(np.abs(LH-F[:3,:3]@RH@np.diag([-1.,1.,1.])))<1e-6
report['symmetry']['proper_camera_rotation_determinants']=[float(np.linalg.det(RH)),float(np.linalg.det(LH))]
for a,b in itertools.combinations(sh,2):
 v=sh[a].common(sh[b]).Volume
 if v<1e-5:continue
 prev=prior[a].common(prior[b]).Volume;report['interferences'][a+'/'+b]={'mm3':v,'inherited_mm3':prev};assert v<=prev+2e-5,(a,b,v,prev)
print('SYMMETRY_AND_SOLID_CLEARANCES_PASS',flush=True)
sk=d.RatDesignSkull.Mesh.copy();sk.Placement=d.RatDesignSkull.getGlobalPlacement()
for name,s in sh.items():
 assert s.isValid() and len(s.Solids)>0
 for lin,ang in [(.04,.15),(.02,.10),(.08,.2)]:
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
  if mesh.isSolid() and not mesh.hasSelfIntersections():break
 assert mesh.isSolid() and not mesh.hasSelfIntersections(),name
 report['mesh_checks'][name]={'closed':True,'self_intersections':False};mesh.write(str(E/(name+'.stl')))
 if name=='Baseplate':continue
 n=mesh.CountFacets;mesh.addMesh(sk);cross=sum((p[0]<n)!=(p[1]<n) for p in mesh.getSelfIntersections());assert cross==0,(name,cross);report['anatomy_crossings'][name]=cross;print('SKULL_CLEAR',name,flush=True)
for name in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 assert d.getObject(name).Mesh.Topology==src.getObject(name).Mesh.Topology and d.getObject(name).getGlobalPlacement()==src.getObject(name).getGlobalPlacement()
assert sh['Baseplate'].cut(prior['Baseplate']).Volume+prior['Baseplate'].cut(sh['Baseplate']).Volume<1e-7
d.recompute();p=O/'ET-RAT-SYMMETRIC-BINOCULAR-R37.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
report.update(passed=True,anatomy_and_baseplate_unchanged=True,carrier_single_solid=len(sh['Carrier'].Solids)==1)
(O/'validation.json').write_text(json.dumps(report,indent=2));(S/'validation.json').write_text(json.dumps(report,indent=2))
(S/'review.json').write_text(json.dumps({'revision':'ET-RAT-SYMMETRIC-BINOCULAR-R37','units':'mm','native_checkpoint':str(p.relative_to(R)),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_complete_assembly':cfg['source_complete_assembly'],'print_details_from':cfg['print_detail_source'],'validation':'validation.json','status':'Symmetric binocular complete assembly; static validation passed; physical fit pending'},indent=2))
A.closeDocument(d.Name);A.closeDocument(src.Name);print('R37_VALIDATED_AND_SAVED')
