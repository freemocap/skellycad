from support import *
import math,itertools
sys.path.insert(0,str(S.parent/'refined-supports-r38'));from common import unit,curve,section
def build(poles,normal):
 c=curve(poles);wires=[]
 for i in range(65):
  u=i/64;t=unit(c.tangent(u)[0]);w=unit(normal.cross(t));width=2.6+.4*math.exp(-(u/.18)**2)+.4*math.exp(-((1-u)/.18)**2);thick=2.-(.8 if abs(normal.x)>.8 else .4)*math.exp(-(u/.12)**2)+.1*math.exp(-((1-u)/.18)**2)
  wires.append(section(c.value(u),t,w,width,thick,False))
 return Part.makeLoft(wires[::4],True,False,False,3)
d=load('04-arms-working' if (O/'04-arms-working.FCStd').exists() else 'source');central=local(d.CentralCarrier);old=json.loads((R/'generated/eye-tracker/rat/clear-view-r41/04-arms.json').read_text());obs=obstacles(d);records=json.loads((O/'04-arms.json').read_text()) if (O/'04-arms.json').exists() else {};accepted=[]
for side in ['Right','Left']:
 H=np.array(cfg['sides'][side]['head']);HP=pose(H);socket=local(d.getObject(side+'RetainedSocket'));q=moved(socket,np.linalg.inv(H));cy=max([f.Surface for f in q.Faces if isinstance(f.Surface,Part.Cylinder)],key=lambda x:x.Radius);cc=HP.multVec(A.Vector(cy.Center.x,cy.Center.y,-8.7));axis=HP.Rotation.multVec(A.Vector(0,0,1));upper=unit(A.Vector(1,0,0).cross(axis));upper=upper if upper.y>0 else -upper;rear=unit(axis.cross(upper));rear=rear if rear.x*(1 if side=='Left' else -1)>0 else -rear
 for tail,rad in [('UpperSupport',upper),('LowerSupport',rear)]:
  name=side+tail
  if name in records:
   existing=local(d.getObject(name));accepted.append(existing);records[name]['engagement_mm3']=[existing.common(central).Volume,existing.common(socket).Volume];continue
  root=A.Vector(*old[name]['poles_mm'][0]);root.z+=(1 if side=='Right' else -1)*(.8 if tail=='UpperSupport' else (1.5 if side=='Right' else 0));tip=cc+rad*2.-axis*(.6 if tail=='LowerSupport' else 0)
  if tail=='UpperSupport':root=A.Vector(3.28706399647303,(15.9 if side=='Right' else 15.2),16.8*(1 if side=='Right' else -1))
  delta=tip-root;normal=unit(delta.cross(rad));cand=[];fail={}
  for fraction,h,reach in itertools.product([.15,.25,.35,.5,.65,.8],[0,2,4,6,9,12,16,22,28],[3,4.5,6,8,11,15,18,22,28]):
   pp=[root,root+delta*fraction+rad*h,tip+rad*reach,tip];cand.append((curve(pp).toShape().Length,pp))
  if tail=='LowerSupport':
   cand=[(q['length'],[A.Vector(*v) for v in q['poles']]) for q in json.loads((O/'rear-candidates.json').read_text())[side]]
  for i,(length,poles) in enumerate(sorted(cand,key=lambda x:x[0])):
   root=poles[0];normal=unit((tip-root).cross(rad))
   pp=np.array([list(p) for p in poles]);u=np.linspace(0,1,101)[:,None];v=3*(1-u)**2*(pp[1]-pp[0])+6*(1-u)*u*(pp[2]-pp[1])+3*u*u*(pp[3]-pp[2]);a=6*(1-u)*(pp[2]-2*pp[1]+pp[0])+6*u*(pp[3]-2*pp[2]+pp[1]);k=np.linalg.norm(np.cross(v,a),axis=1)/np.maximum(np.linalg.norm(v,axis=1),1e-9)**3
   if max(k)>.4:continue
   us=np.linspace(0,1,17)[:,None];centers=(1-us)**3*pp[0]+3*(1-us)**2*us*pp[1]+3*(1-us)*us**2*pp[2]+us**3*pp[3];tangents=3*(1-us)**2*(pp[1]-pp[0])+6*(1-us)*us*(pp[2]-pp[1])+3*us**2*(pp[3]-pp[2]);tangents/=np.linalg.norm(tangents,axis=1)[:,None];nn=np.array(list(normal));ww=np.cross(nn,tangents);widths=2.6+.4*np.exp(-(us/.18)**2)+.4*np.exp(-((1-us)/.18)**2);thicks=2.-(.8 if abs(normal.x)>.8 else .4)*np.exp(-(us/.12)**2)+.1*np.exp(-((1-us)/.18)**2);probes=np.vstack([centers,centers+ww*widths/2,centers-ww*widths/2,centers+nn*thicks/2,centers-nn*thicks/2]);hp=(probes-H[:3,3])@H[:3,:3]
   if np.any(np.all((hp>[-7.5,-1.5,-6.8])&(hp<[7.5,17.5,8]),axis=1)):continue
   try:s=build(poles,normal)
   except Exception:continue
   if not s.isValid() or len(s.Solids)!=1:continue
   seats=[s.common(central).Volume,s.common(socket).Volume]
   if min(seats)<1.:fail['seat']=fail.get('seat',0)+1;continue
   bad=None
   for n,o in obs.items():
    if s.BoundBox.intersect(o.BoundBox) and s.common(o).Volume>1e-5:bad=n;break
   if bad:
    fail[bad]=fail.get(bad,0)+1
    if i%30==0:print(name,i,fail,flush=True)
    continue
   mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
   if not mesh.isSolid() or mesh.hasSelfIntersections():continue
   seats=[s.common(central).Volume,s.common(socket).Volume]
   if min(seats)<1.:fail['seat']=fail.get('seat',0)+1;continue
   if tail=='LowerSupport':
    zone=Part.makeSphere(4.7,cc);overlap=s.common(accepted[-1]);gap_bad=overlap.Volume>1e-6 and overlap.cut(central).cut(zone).Volume>1e-6
    if gap_bad:fail['gap']=fail.get('gap',0)+1;continue
   assign(d.getObject(name),moved(s,T));accepted.append(s);records[name]={'poles_mm':[list(p) for p in poles],'length_mm':length,'plane_normal_mount':list(normal),'socket_outward_direction_mount':list(rad),'engagement_mm3':seats,'pcb_plane_angle_degrees':math.degrees(math.acos(min(1,abs(normal.x)))),'planarity_error_mm':max(abs((p-root).dot(normal)) for p in poles)};print('ACCEPT',name,records[name],flush=True);break
  else:raise RuntimeError((name,fail))
  d.recompute();d.saveAs(str(O/'04-arms-working.FCStd'));(O/'04-arms.json').write_text(json.dumps(records,indent=2))
carrier=central.multiFuse(accepted+[local(d.getObject(s+'RetainedSocket')) for s in ['Right','Left']]).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1;assign(d.FinishedCarrier,moved(carrier,T));save(d,'04-arms',records)

