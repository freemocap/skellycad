"""Camera-fixed, length-constrained smooth ribbon; arm offset behind its face."""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np
from scipy.optimize import minimize
import FreeCAD as A,Part,MeshPart,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/ribbon-led-r23';O=R/'generated/eye-tracker/rat/ribbon-led-r23';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
sys.path.insert(0,str(R/'designs/eye-tracker/shared/compact-guard-r02'));from guard import unit,rectangle
m=json.loads((S.parent/'oval-camera-r21/review.json').read_text());assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(R/m['native_checkpoint']))
sol=json.loads((S.parent/'oval-camera-r21/solution.json').read_text());M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])));H=np.array(sol['head']);start=np.array([5.53706399647303,12.78,16.5]);end=H[:3,3];t0=np.array([0.,0,1]);t1=H[:3,1]
u=np.linspace(0,1,201)
def samples(h):
 cubic=np.array([start,start+t0*h[0],end-t1*h[1],end])
 p=cubic
 for degree in [3,4]:
  p=np.array([p[0]]+[p[i-1]*(i/(degree+1))+p[i]*(1-i/(degree+1)) for i in range(1,degree+1)]+[p[-1]])
 p[2]+=h[2:5];p[3]+=h[5:8]
 def bez(p):
  degree=len(p)-1
  return sum(math.comb(degree,i)*(1-u[:,None])**(degree-i)*u[:,None]**i*x for i,x in enumerate(p))
 q=bez(p);dq=bez(5*np.diff(p,axis=0));ddq=bez(20*np.diff(p,n=2,axis=0));speed=np.linalg.norm(dq,axis=1);k=np.linalg.norm(np.cross(dq,ddq),axis=1)/speed**3
 return p,q,dq/speed[:,None],k,float(np.trapz(speed,u))
fit=minimize(lambda h:float(np.mean(samples(h)[3]**2)+.00001*np.sum(h[2:]**2)),[22.86,18.39,0,0,0,0,0,0],method='SLSQP',bounds=[(2,50),(2,50)]+[(-8,8)]*6,constraints=[{'type':'eq','fun':lambda h:samples(h)[4]-32.85},{'type':'ineq','fun':lambda h:1/3.7-samples(h)[3]},{'type':'ineq','fun':lambda h:samples(h)[1][1:30,0]-start[0]-4*u[1:30]**2}],options={'maxiter':400,'ftol':1e-10});assert fit.success,fit.message
p,q,t,k,length=samples(fit.x);print('ribbon handles,length,min radius',fit.x,length,1/max(k),flush=True)
curve=Part.BezierCurve();curve.setPoles([A.Vector(*v) for v in p]);count=81;centers=[curve.value(i/(count-1)) for i in range(count)];tangents=[curve.tangent(i/(count-1))[0] for i in range(count)];widths=[A.Vector(0,1,0)]
for a,b in zip(tangents,tangents[1:]):widths.append(A.Rotation(a,b).multVec(widths[-1]))
target=A.Vector(*H[:3,0]);tv=tangents[-1];angle=math.degrees(math.atan2(tv.dot(widths[-1].cross(target)),widths[-1].dot(target)))
normals=[];rw=[];aw=[]
for i,(c,t,w) in enumerate(zip(centers,tangents,widths)):
 v=i/(count-1);w=A.Rotation(t,angle*(3*v*v-2*v**3)).multVec(w);widths[i]=w;n=unit(w.cross(t));normals.append(n)
 rw.append(rectangle(c-n*.125,t,w,4,.25))
 # The arm follows the already-solved ribbon on its negative face.
 aw.append(rectangle(c-n*2.6,t,w,4-1.4*(3*v*v-2*v**3),1.8))
def loft(w):return Part.makeLoft(w,True,False,False,5)
rib=loft(rw[::2]);arm=loft(aw[::2]);assert rib.isValid() and arm.isValid()
names=['RetainedPCBTray','RetainedSocket','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens','FinishedCarrier','skull_mount_Baseplate'];sh={name:world(d.getObject(name)).transformed(M.inverse().toMatrix()) for name in names}
cfg=json.loads((S.parent/'oval-camera-r21/arms.json').read_text())['RearRibbonGuard'];sc=A.Vector(*cfg['socket_center_mm']);axis=unit(cfg['socket_axis']);back=centers[-1]-normals[-1]*2.6;radial=unit(back-sc-axis*(back-sc).dot(axis));terminal=sc+axis*4.6+radial*1.8
root=rectangle(A.Vector(3.43706399647303,12.78,16.0),A.Vector(0,0,1),A.Vector(0,1,0),4,1.8)
arm=arm.fuse(Part.makeLoft([root,aw[0]],True,True))
arm=arm.fuse(Part.makeLoft([aw[-1],rectangle(terminal,tangents[-1],widths[-1],2.6,1.8)],True,True)).removeSplitter();assert arm.isValid() and len(arm.Solids)==1
report={'source':m,'units':'mm','camera_pose':'unchanged from R21','centerline_length_mm':length,'minimum_centerline_radius_mm':float(1/max(k)),'optimization_variables_mm':fit.x.tolist(),'centerline_poles_mm':p.tolist(),'distributed_twist_deg':angle,'arm_offset_mm':2.6,'route_model':'Smooth quintic centerline and distributed frame twist; geometric relaxed-route approximation, not an inextensible shell or physical energy simulation','checks':{}}
for name,s in [('ribbon',rib),('arm',arm)]:
 for key in names:
  if key=='FinishedCarrier':continue
  vol=s.common(sh[key]).Volume;report['checks'][name+'_'+key]=vol
print(json.dumps(report,indent=2),flush=True)
report['arm_ribbon_overlap_mm3']=arm.common(rib).Volume;report['arm_ribbon_gap_mm']=arm.distToShape(rib)[0]
report['seating']={key:arm.common(sh[key]).Volume for key in ['RetainedPCBTray','RetainedSocket']}
(O/'validation.json').write_text(json.dumps(report,indent=2))
assert report['arm_ribbon_overlap_mm3']<1e-6
for name in ['ribbon','arm']:
 for key in names:
  if key in ['FinishedCarrier','RetainedPCBTray','RetainedSocket']:continue
  assert report['checks'][name+'_'+key]<1e-5,(name,key,report['checks'][name+'_'+key])
assert min(report['seating'].values())>.1,report['seating']
carrier=sh['RetainedPCBTray'].fuse(sh['RetainedSocket']).fuse(arm).removeSplitter();carrier=carrier.cut(Part.makeBox(.50677424482636,3.7,5.8,A.Vector(3.2,11.4,-2.9))).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
relief=Part.makeBox(1.0,4.5,3.2,A.Vector(start[0]-.35,start[1]-2.25,start[2]-.1))
carrier=carrier.cut(relief).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
report['finished_carrier_ribbon_overlap_mm3']=carrier.common(rib).Volume;report['finished_carrier_ribbon_gap_mm']=carrier.distToShape(rib)[0];report['exit_relief_box_mm']={'size':[1.0,4.5,3.2],'origin':[float(start[0]-.35),float(start[1]-2.25),float(start[2]-.1)]}
assert report['finished_carrier_ribbon_overlap_mm3']<1e-6
(O/'validation.json').write_text(json.dumps(report,indent=2))
assign(d.FinishedCarrier,carrier.transformed(M.toMatrix()));assign(d.RibbonCandidate,rib.transformed(M.toMatrix()));ob=d.addObject('Part::Feature','SingleTaperedArm');assign(ob,arm.transformed(M.toMatrix()))
for label,s in [('carrier',world(d.FinishedCarrier)),('ribbon',world(d.RibbonCandidate)),('arm',world(ob))]:
 mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/(label+'.stl')))
d.Label='Rat R23 - ribbon-led single support';d.recompute();d.saveAs(str(O/'ET-RAT-RIBBON-LED-R23.FCStd'));print('R23 SAVED',flush=True)

