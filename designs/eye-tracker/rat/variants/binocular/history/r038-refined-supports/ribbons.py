"""Fit finite-thickness ribbons between fixed board and camera endpoint frames."""
from pathlib import Path
import sys,json,math,zipfile
import numpy as np
from scipy.optimize import minimize
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/refined-supports-r38';O=R/'generated/eye-tracker/rat/refined-supports-r38'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
sys.path.insert(0,str(R/'designs/eye-tracker/shared/compact-guard-r02'));from guard import unit,rectangle
cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);d=A.openDocument(str(O/'plate-working.FCStd'))
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):
 s=s.copy();s.Placement=pose(t).multiply(s.Placement);return s
central=Part.Shape();central.read(str(O/'carrier.brep'));u=np.linspace(0,1,201);report={}
for side,rec in cfg['sides'].items():
 B=np.array(rec['board_transform']);H=np.array(rec['head']);start=(B@np.array([5.53706399647303,12.78,16.5,1]))[:3];end=H[:3,3];t0=B[:3,2];t1=H[:3,1];w0=B[:3,1];outward=B[:3,0]
 def samples(h):
  p=np.array([start,start+t0*h[0],end-t1*h[1],end])
  for degree in [3,4]:p=np.array([p[0]]+[p[i-1]*i/(degree+1)+p[i]*(1-i/(degree+1)) for i in range(1,degree+1)]+[p[-1]])
  p[2]+=h[2:5];p[3]+=h[5:8]
  def bez(p):
   n=len(p)-1;return sum(math.comb(n,i)*(1-u[:,None])**(n-i)*u[:,None]**i*v for i,v in enumerate(p))
  q=bez(p);dq=bez(5*np.diff(p,axis=0));ddq=bez(20*np.diff(p,n=2,axis=0));speed=np.linalg.norm(dq,axis=1);k=np.linalg.norm(np.cross(dq,ddq),axis=1)/speed**3
  return p,q,k,float(np.trapz(speed,u))
 obstacles={'central':central}
 for other in cfg['sides']:
  for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
   s=Part.Shape();s.read(str(O/(other+'-'+n+'.brep')));obstacles[other+n]=s
  for n in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:obstacles[other+n]=world(d.getObject(other+n)).transformed(pose(T).inverse().toMatrix())
 rng=np.random.default_rng(41);best=None
 for trial in range(16):
  seed=np.r_[20.,18.,np.zeros(6)] if trial==0 else np.r_[rng.uniform(10,30,2),rng.uniform(-6,6,6)]
  fit=minimize(lambda h:np.mean(samples(h)[2]**2)+.00001*np.sum(h[2:]**2),seed,method='SLSQP',bounds=[(2,50),(2,50)]+[(-12,12)]*6,constraints=[{'type':'eq','fun':lambda h:samples(h)[3]-32.85},{'type':'ineq','fun':lambda h:1/3.7-samples(h)[2]},{'type':'ineq','fun':lambda h:(samples(h)[1][1:30]-start)@outward-4*u[1:30]**2}],options={'maxiter':500,'ftol':1e-10})
  if not fit.success:print(side,trial,fit.message,flush=True);continue
  p,q,k,length=samples(fit.x);curve=Part.BezierCurve();curve.setPoles([A.Vector(*v) for v in p]);centers=[curve.value(i/80) for i in range(81)];tangents=[curve.tangent(i/80)[0] for i in range(81)];widths=[A.Vector(*w0)]
  for a,b in zip(tangents,tangents[1:]):widths.append(A.Rotation(a,b).multVec(widths[-1]))
  target=A.Vector(*H[:3,0]);tv=tangents[-1];angle=math.degrees(math.atan2(tv.dot(widths[-1].cross(target)),widths[-1].dot(target)));wires=[]
  for i,(c,t,w) in enumerate(zip(centers,tangents,widths)):
   v=i/80;w=A.Rotation(t,angle*(3*v*v-2*v**3)).multVec(w);n=unit(w.cross(t));wires.append(rectangle(c-n*.125,t,w,4,.25))
  rib=Part.makeLoft(wires[::2],True,False,False,5)
  if not rib.isValid():continue
  checks={n:rib.common(s).Volume for n,s in obstacles.items()};bad={n:v for n,v in checks.items() if v>1e-5};print(side,trial,'radius',1/max(k),'twist',angle,'collisions',bad,flush=True)
  if bad:continue
  best=rib;report[side]={'centerline_length_mm':length,'minimum_sampled_centerline_radius_mm':float(1/max(k)),'centerline_poles_mm':p.tolist(),'distributed_twist_deg':angle,'width_mm':4,'thickness_mm':.25,'checks_mm3':checks,'model_limit':'Relaxed geometric strip; centerline length and sampled curvature constrained; not an inextensible shell or physical ribbon validation'};break
 if best is None:
  (O/'ribbon-failure.json').write_text(json.dumps(report,indent=2));raise RuntimeError(side+' ribbon has no accepted fit')
 best.exportBrep(str(O/(side+'-ribbon.brep')));cam=d.getObject(side+'Camera');cam.PhysicalParts[3].Shape=best
 (S/'ribbons.json').write_text(json.dumps(report,indent=2));d.recompute();d.saveAs(str(O/'03-plate.FCStd'))
with zipfile.ZipFile(O/'03-plate.FCStd') as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);print('RIBBONS_SAVED')

