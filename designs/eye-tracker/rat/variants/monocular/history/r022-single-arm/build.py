from pathlib import Path
import sys,json,hashlib,math
import FreeCAD as A,Part,MeshPart,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/single-arm-r22';O=R/'generated/eye-tracker/rat/single-arm-r22';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
from arm_geometry import geometry,unit
m=json.loads((S.parent/'oval-camera-r21/review.json').read_text());assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
sel=json.loads((S.parent/'active-model.json').read_text());audit={'recorded':sel['native_sha256'],'actual':hashlib.sha256((R/sel['native_checkpoint']).read_bytes()).hexdigest(),'used':False}
d=A.openDocument(str(R/m['native_checkpoint']))
sol=json.loads((S.parent/'oval-camera-r21/solution.json').read_text());M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])))
names=['RetainedPCBTray','RetainedSocket','RibbonCandidate','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens','FinishedCarrier','skull_mount_Baseplate']
sh={name:world(d.getObject(name)).transformed(M.inverse().toMatrix()) for name in names}
p=json.loads((S.parent/'oval-camera-r21/arms.json').read_text())['RearRibbonGuard']
c=A.Vector(*p['socket_center_mm']);n=unit(p['socket_axis']);root=A.Vector(3.2,12.78,17.0)
radial=unit(root-c-n*(root-c).dot(n))
p.update(width_mm=3.2,thickness_mm=2.0,root_lead_mm=.7,embed_mm=.4,socket_width_mm=2.6,socket_thickness_mm=2.0,socket_lead_mm=.4,sections=49,attachment_height_mm=3.9,attachment_radius_mm=2.2)
p['arm'].update(root_mm=list(root),root_tangent=[0,0,1],root_width_direction=[0,1,0],root_width_mm=4.,root_thickness_mm=2.,radial_direction=list(radial))
arm=None; trials=[]
for rh,eh,bow in [(10,6,-6)]:
 p['bow_mm']=bow
 p['arm']['root_handle_mm']=rh;p['arm']['socket_handle_mm']=eh
 try:
  candidate=geometry(p,3.2,1.8)[0];gap=candidate.distToShape(sh['RibbonCandidate'])[0];vol=candidate.common(sh['RibbonCandidate']).Volume
  other=max(candidate.common(sh[k]).Volume for k in ['eye_primary_Holder','eye_primary_Clip','camera_pcb','M4_lens','PCB'])
  seat=[candidate.common(sh[k]).Volume for k in ['RetainedPCBTray','RetainedSocket']]
  row=dict(handles=[rh,eh],bow=bow,gap=gap,ribbon_overlap=vol,other_overlap=other,seating=seat);trials.append(row);print(row,flush=True)
  if vol<1e-6 and other<1e-6 and min(seat)>.1 and gap>.25:arm=candidate;break
 except Exception as e:print('retry',rh,eh,str(e)[:120],flush=True)
(O/'trials.json').write_text(json.dumps(trials,indent=2));assert arm is not None,'No clear seated single-arm candidate'
carrier=sh['RetainedPCBTray'].fuse(sh['RetainedSocket']).fuse(arm).removeSplitter()
carrier=carrier.cut(Part.makeBox(3.70677424482636-3.2,3.7,5.8,A.Vector(3.2,11.4,-2.9))).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
report={'source':m,'selected_baseline_audit':audit,'units':'mm','single_arm':trials[-1],'carrier_valid':True,'carrier_solids':1,'overlaps':{}}
for k in ['eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens','skull_mount_Baseplate','RibbonCandidate']:
 v=carrier.common(sh[k]).Volume;old=sh['FinishedCarrier'].common(sh[k]).Volume;report['overlaps'][k]={'before_mm3':old,'after_mm3':v};assert v<=old+1e-5,(k,v,old)
obj=d.addObject('Part::Feature','SingleTaperedArm');obj.Label='Single tapered support behind ribbon exit';assign(obj,arm.transformed(M.toMatrix()));assign(d.FinishedCarrier,carrier.transformed(M.toMatrix()));d.FinishedCarrier.Label='Single-arm carrier - tray, tapered support and socket'
# Historical construction remains hidden; only one support is included in carrier.
mesh=MeshPart.meshFromShape(Shape=world(d.FinishedCarrier),LinearDeflection=.03,AngularDeflection=.12,Relative=False);report['mesh']={'closed':mesh.isSolid(),'self_intersections':mesh.hasSelfIntersections()};assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/'carrier.stl'))
am=MeshPart.meshFromShape(Shape=world(obj),LinearDeflection=.04,AngularDeflection=.15,Relative=False);am.write(str(O/'arm.stl'));report['anatomy']={}
for k in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 mesh=d.getObject(k).Mesh.copy();count=mesh.CountFacets;mesh.addMesh(am);cross=sum((ids[0]<count)!=(ids[1]<count) for ids in mesh.getSelfIntersections());report['anatomy'][k]=cross;assert cross==0
(S/'parameters.json').write_text(json.dumps(p,indent=2));(O/'validation.json').write_text(json.dumps(report,indent=2));d.Label='Rat R22 - single tapered arm';d.recompute();d.saveAs(str(O/'ET-RAT-SINGLE-ARM-R22.FCStd'));print('R22 SAVED',flush=True)
