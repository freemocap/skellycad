from support import *
import itertools,hashlib
def center(s):return sum((q.CenterOfMass*q.Volume for q in s.Solids),A.Vector())/s.Volume
assert json.loads((O/'label-audit.json').read_text())['passed']
E=O/'validation-meshes';E.mkdir(exist_ok=True);d=load('05-labeled');src=A.openDocument(str(R/cfg['source_complete_assembly']['native_checkpoint']));oldT=np.array(json.loads((S.parent/'forward-mount-r39/recipe.json').read_text())['mount_to_skull']);sh={'Carrier':world(d.FinishedCarrier),'Baseplate':world(d.Baseplate)};prior={'Carrier':world(src.FinishedCarrier),'Baseplate':world(src.Baseplate)};report={'passed':False,'units':'mm','physical_fit_verified':False,'print_release':False,'aim':{},'mesh_checks':{},'interferences':{},'seating':{},'anatomy_crossings':{}}
for side in ['Right','Left']:
 cam=d.getObject(side+'Camera');lens=cam.getGlobalPlacement().multVec(cam.OpticalAxis.Origin);axis=cam.getGlobalPlacement().Rotation.multVec(cam.OpticalAxis.Direction);eye=A.Vector(8.263833250818816,(-1 if side=='Right' else 1)*8.284849782773964,-6.338181566207952);delta=eye-lens;assert delta.cross(axis).Length<1e-5 and delta.dot(axis)>0;report['aim'][side]={'lens_world_mm':list(lens),'axis_world':list(axis),'miss_mm':delta.cross(axis).Length,'stand_off_mm':delta.Length}
 for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','ribbon']:
  s=Part.Shape();s.read(str(O/(side+('-' if n=='ribbon' else '')+n+'.brep')));sh[side+n]=moved(s,T)
  s=Part.Shape();s.read(str(R/'generated/eye-tracker/rat/forward-mount-r39'/(side+('-' if n=='ribbon' else '')+n+'.brep')));prior[side+n]=moved(s,oldT)
 for n in ['eye_primary_Holder','eye_primary_Clip']:sh[side+n]=world(d.getObject(side+n));prior[side+n]=world(src.getObject(side+n))
 for n in ['UpperSupport','LowerSupport']:
  s=world(d.getObject(side+n));seat=[s.common(world(d.CentralCarrier)).Volume,s.common(world(d.getObject(side+'RetainedSocket'))).Volume];assert min(seat)>.3;report['seating'][side+n]=seat
for k in ['lens_world_mm','axis_world']:assert np.linalg.norm(np.array(report['aim']['Right'][k])*[1,-1,1]-report['aim']['Left'][k])<1e-5
RH=(T@np.array(cfg['sides']['Right']['head']))[:3,:3];LH=(T@np.array(cfg['sides']['Left']['head']))[:3,:3];frame_error=float(np.max(np.abs(LH-np.diag([1.,-1.,1.])@RH@np.diag([1.,-1.,1.]))));assert frame_error<1e-6;report['mirrored_camera_frame_error']=frame_error
report['camera_access']={}
for side in ['Right','Left']:
 keep=Part.Shape();keep.read(str(O/(side+'-camera-access-keepout.brep')));keep=moved(keep,T);arm=Part.makeCompound([world(d.getObject(side+t)) for t in ['UpperSupport','LowerSupport']]);v=arm.common(keep).Volume;assert v<1e-6
 # The socket is retained; the new supporting beam must leave the access box empty.
 new_material=sh['Carrier'].cut(world(d.CentralCarrier)).cut(world(d.RightRetainedSocket)).cut(world(d.LeftRetainedSocket));assert new_material.common(keep).Volume<1e-5
 report['camera_access'][side]={'arm_overlap_mm3':v,'new_carrier_material_overlap_mm3':new_material.common(keep).Volume,'head_frame_keepout_mm':{'x':[-7.5,7.5],'y':[-1.5,17.5],'z':[-6.8,8]},'support_count':2}
 for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:
  a=world(d.getObject(side+tail));b=world(src.getObject(side+tail));D=T@np.array(cfg['sides'][side]['head'])@np.linalg.inv(np.array(cfg['sides'][side]['previous_head']))@inv;expected=moved(b,D)
  if side=='Left':
   H=T@np.array(cfg['sides'][side]['head']);expected=expected.mirror(A.Vector(*(H[:3,3]+H[:3,0]*cfg['left_fixture_reflection']['plane_x_mm'])),A.Vector(*H[:3,0]))
  assert abs(a.Volume-b.Volume)<1e-6 and (center(a)-center(expected)).Length<1e-5
report['view_clearance']={}
for side in ['Right','Left']:
 cone=Part.Shape();cone.read(str(O/(side+'-view-keepout.brep')));cone=moved(cone,T);checks={}
 for name,shape in sh.items():
  if not cone.BoundBox.intersect(shape.BoundBox):continue
  v=cone.common(shape).Volume;assert v<1e-5,(side,'view obstruction',name,v);checks[name]=v
 report['view_clearance'][side]={'overlaps_mm3':checks,'policy':cfg['view_policy']}
 v=d.addObject('PartDesign::Feature',side+'EyeViewClearance');v.Shape=cone;v.Label=side+' eye viewing clearance (hidden)';v.Visibility=False
assert len(json.loads((O/'04-arms.json').read_text()))==4
for a,b in itertools.combinations(sh,2):
 if not sh[a].BoundBox.intersect(sh[b].BoundBox):continue
 v=sh[a].common(sh[b]).Volume
 if v<1e-5:continue
 old=prior[a].common(prior[b]).Volume;report['interferences'][a+'/'+b]={'mm3':v,'baseline_mm3':old};assert v<=old+2e-5,(a,b,v,old)
 print('INHERITED',a,b,v,flush=True)
print('SOLID_CLEARANCE_PASS',flush=True)
sk=d.RatDesignSkull.Mesh.copy();sk.Placement=d.RatDesignSkull.getGlobalPlacement()
for name,s in sh.items():
 assert s.isValid() and len(s.Solids)>0
 for lin,ang in [(.04,.15),(.02,.10),(.08,.2)]:
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
  if mesh.isSolid() and not mesh.hasSelfIntersections():break
 assert mesh.isSolid() and not mesh.hasSelfIntersections(),name;mesh.write(str(E/(name+'.stl')));report['mesh_checks'][name]={'closed':True,'self_intersections':False}
 if name=='Baseplate':continue
 n=mesh.CountFacets;mesh.addMesh(sk);cross=sum((p[0]<n)!=(p[1]<n) for p in mesh.getSelfIntersections());assert cross==0,(name,cross);report['anatomy_crossings'][name]=cross;print('SKULL_CLEAR',name,flush=True)
for name in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:assert d.getObject(name).Mesh.Topology==src.getObject(name).Mesh.Topology
assert len(sh['Carrier'].Solids)==1
a=world(d.Baseplate);b=world(src.Baseplate);assert abs(a.Volume-b.Volume)<1e-8 and (center(a)-center(b)).Length<1e-8
assert np.allclose(sorted(tuple(v.Point) for v in a.Vertexes),sorted(tuple(v.Point) for v in b.Vertexes),atol=1e-8)
report.update(passed=True,ribbon_validation=json.loads((O/'02-camera-and-ribbon-study.json').read_text()),camera_roll_policy='Lens positions and axes mirrored; camera frames mirrored with a half-turn orientation difference',pcb_support_thickness_mm=1.8,baseplate_geometry_preserved=True,forward_mount=cfg['forward_mount'],junctions=json.loads((O/'04-finished.json').read_text()))
for o in d.Objects:o.Visibility=o.TypeId=='App::Part'
for n in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea','FinishedCarrier','Baseplate']+[s+t for s in ['Right','Left'] for t in ['eye_primary_Holder','eye_primary_Clip']]:d.getObject(n).Visibility=True
for side in ['Right','Left']:
 for o in d.getObject(side+'Camera').PhysicalParts:o.Visibility=True
 d.getObject(side+'Camera').OpticalAxis.Visibility=True
d.Label='RAT R41 - clear eye views and paired rear supports';d.recompute();p=O/'ET-RAT-CLEAR-VIEW-R41.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
(O/'validation.json').write_text(json.dumps(report,indent=2));(S/'review.json').write_text(json.dumps({'revision':'ET-RAT-CLEAR-VIEW-R41','units':'mm','native_checkpoint':str(p.relative_to(R)),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_complete_assembly':cfg['source_complete_assembly'],'physical_fit_verified':False,'status':'Two rear supports per camera; lens-to-eye viewing volumes and camera access checked; symmetric aim; physical fit pending'},indent=2));A.closeDocument(src.Name);A.closeDocument(d.Name);print('SAVED_R41')
