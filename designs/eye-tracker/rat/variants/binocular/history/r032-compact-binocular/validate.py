"""Validate saved binocular geometry, matched interfaces and anatomy crossings."""
from pathlib import Path
import json,sys,itertools,zipfile,hashlib
import numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/compact-binocular-r32';O=R/'generated/eye-tracker/rat/compact-binocular-r32';E=O/'validation-meshes';E.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
cfg=json.loads((S/'recipe.json').read_text());m=cfg['geometry_lineage_r30'];p=O/'ET-RAT-COMPACT-BINOCULAR-R32.FCStd';d=A.openDocument(str(p));old=A.openDocument(str(R/m['native_checkpoint']));T=np.array(cfg['mount_to_skull'])
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):
 s=s.copy();s.Placement=pose(t).multiply(s.Placement);return s
report={'passed':False,'units':'mm','physical_fit_verified':False,'print_release':False,'aim':{},'interfaces':{},'interferences':{},'anatomy_crossings':{},'mesh_checks':{},'arm_pairs':{}}
sh={'Carrier':world(d.FinishedCarrier),'Baseplate':world(d.Baseplate)};source={'Carrier':world(old.FinishedCarrier),'Baseplate':world(old.skull_mount_Baseplate)}
for side,rec in cfg['sides'].items():
 cam=d.getObject(side+'Camera');lens=cam.getGlobalPlacement().multVec(cam.OpticalAxis.Origin);axis=cam.getGlobalPlacement().Rotation.multVec(cam.OpticalAxis.Direction);eye=A.Vector(*next(e['center_mm'] for e in json.loads((S.parent/'registered-eyes-r14/placement.json').read_text())['eyes'] if e['side']==side));off=eye-lens
 report['aim'][side]={'eye_center_world_mm':list(eye),'target_world_mm':list(pose(T).multVec(A.Vector(*rec['eye_target_mount_mm']))),'miss_mm':off.cross(axis).Length,'forward_mm':off.dot(axis)}
 assert off.cross(axis).Length<.01 and off.dot(axis)>0,report['aim'][side]
 for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','ribbon']:
  s=Part.Shape();s.read(str(O/(side+'-'+n+'.brep')));sh[side+n]=moved(s,T);source[side+n]=world(old.getObject('RibbonCandidate' if n=='ribbon' else n))
 for n in ['eye_primary_Holder','eye_primary_Clip']:
  sh[side+n]=world(d.getObject(side+n));source[side+n]=world(old.getObject(n))
 socket=world(d.getObject(side+'RetainedSocket'));original=world(old.RetainedSocket);oldT=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['mount_to_skull']);delta=T@np.array(rec['head_delta'])@np.linalg.inv(oldT);expected=moved(original,delta)
 report['interfaces'][side+'socket_difference_mm3']=socket.cut(expected).Volume+expected.cut(socket).Volume
 assert report['interfaces'][side+'socket_difference_mm3']<1e-5
 for n in ['eye_primary_Holder','eye_primary_Clip']:
  expected=moved(world(old.getObject(n)),delta);actual=sh[side+n];v=actual.cut(expected).Volume+expected.cut(actual).Volume;assert v<1e-5;report['interfaces'][side+n+'_difference_mm3']=v
base=sh['Baseplate'];before=source['Baseplate'].copy();before.translate(A.Vector(0,0,-2));diff=base.cut(before).Volume+before.cut(base).Volume;assert diff<1e-6;report['interfaces']['baseplate_difference_mm3']=diff
for a,b in itertools.combinations(sh,2):
 v=sh[a].common(sh[b]).Volume
 if v<1e-5:continue
 same_side=any(a.startswith(s) and b.startswith(s) for s in cfg['sides']);prior=source[a].common(source[b]).Volume if same_side or {a,b}=={'Carrier','Baseplate'} else 0
 report['interferences'][a+'/'+b]={'overlap_mm3':v,'inherited_mm3':prior};assert v<=prior+1e-5,(a,b,v,prior)
print('SOLID_AND_INTERFACE_CHECKS_PASS',report['aim'],flush=True)
armnames=[s+n for s in cfg['sides'] for n in ['UpperSupport','LowerSupport']];central=world(d.CentralCarrier);sockets=[world(d.getObject(s+'RetainedSocket')) for s in cfg['sides']]
for a,b in itertools.combinations(armnames,2):
 aa=world(d.getObject(a));bb=world(d.getObject(b));v=aa.common(bb).Volume
 for cut in [central,*sockets]:aa=aa.cut(cut);bb=bb.cut(cut)
 gap=aa.distToShape(bb)[0];report['arm_pairs'][a+'/'+b]={'overlap_mm3':v,'free_gap_mm':gap};assert v<1e-6 and gap>.3
sk=d.RatDesignSkull.Mesh.copy();sk.Placement=d.RatDesignSkull.getGlobalPlacement()
for name,s in sh.items():
 assert s.isValid() and len(s.Solids)>0,name
 for linear,angular in [(.04,.15),(.02,.10),(.08,.2)]:
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=linear,AngularDeflection=angular,Relative=False);closed=mesh.isSolid();selfcross=mesh.hasSelfIntersections()
  if closed and not selfcross:break
 report['mesh_checks'][name]={'closed':closed,'self_intersections':selfcross,'linear_deflection_mm':linear,'angular_deflection_rad':angular};assert closed and not selfcross,(name,report['mesh_checks'][name])
 mesh.write(str(E/(name+'.stl')))
 if name=='Baseplate':continue
 n=mesh.CountFacets;mesh.addMesh(sk);cross=sum((pair[0]<n)!=(pair[1]<n) for pair in mesh.getSelfIntersections());report['anatomy_crossings'][name]=cross;print('skull',name,cross,flush=True);assert cross==0,(name,cross)
for name in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 assert old.getObject(name).Mesh.Topology==d.getObject(name).Mesh.Topology and old.getObject(name).getGlobalPlacement()==d.getObject(name).getGlobalPlacement()
report['anatomy_unchanged']=True;report['carrier_single_solid']=len(sh['Carrier'].Solids)==1;assert report['carrier_single_solid'];report['source_hash_unchanged']=hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256'];assert report['source_hash_unchanged']
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
report['passed']=True;(O/'validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(d.Name);A.closeDocument(old.Name);print('NATIVE_VALIDATION_PASS')



