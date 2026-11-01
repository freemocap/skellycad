from support import *
import itertools
sys.path.insert(0,str(S.parent/'refined-supports-r38'));from common import unit,curve,section,make
import math
source=json.loads((S.parent/'forward-mount-r39/review.json').read_text());d=load('04-arms-working' if (O/'04-arms-working.FCStd').exists() else '02-camera-and-ribbon-study');central=local(d.CentralCarrier);old=json.loads((R/'generated/eye-tracker/rat/forward-mount-r39/04-arms.json').read_text());obs={n:v for n,v in obstacles(d).items() if 'camera-access-keepout' not in n};obmeshes={n:MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False) for n,s in obs.items()};records=json.loads((O/'04-arms.json').read_text()) if (O/'04-arms.json').exists() else {};accepted=[]
for side in ['Right','Left']:
 H=np.array(cfg['sides'][side]['head']);HP=pose(H);HI=HP.inverse();socket=local(d.getObject(side+'RetainedSocket'));headsocket=socket.transformed(HI.toMatrix());cyl=max([f.Surface for f in headsocket.Faces if isinstance(f.Surface,Part.Cylinder)],key=lambda s:s.Radius);center=cyl.Center;axis=HP.Rotation.multVec(A.Vector(0,0,1));keep=Part.makeBox(15,19,14.8,A.Vector(-7.5,-1.5,-6.8)).transformed(HP.toMatrix());keep.exportBrep(str(O/(side+'-camera-access-keepout.brep')))
 for tail in ['UpperSupport','LowerSupport']:
  name=side+tail
  if name in records:accepted.append(local(d.getObject(name)));continue
  root=A.Vector(*old[name]['poles_mm'][0]);root.z-=1.5 if name=='LeftLowerSupport' else 0;rh=HI.multVec(root);phi=(60 if tail=='UpperSupport' else -60)*(1 if side=='Right' else -1);angle=np.deg2rad(phi);rdir=A.Vector(float(np.cos(angle)),float(np.sin(angle)),0);th=A.Vector(center.x,center.y,-8.7)+rdir*2.0;tip=HP.multVec(th);rad=HP.Rotation.multVec(rdir);w=A.Vector(0,1,0);candidates=[];fail={}
  for back,reach,out,along in itertools.product([4,8,12,18,24,32],[4,7,10,14,20,26,34],[4,8,12,18,24,32],[-30,-22,-16,-10,-5,0,5,10,16,22,30]):
   p1=HP.multVec(rh+A.Vector(out,along,-back));p2=tip+HP.Rotation.multVec(A.Vector(1.,.7 if phi>0 else -.7,0))*reach;poles=[root,p1,p2,tip];candidates.append((curve(poles).toShape().Length,poles))
  if side=='Left' and tail=='LowerSupport':
   M=np.diag([1.,-1.,1.,1.]);Q=inv@M@T;rp=np.array(records['Right'+tail]['poles_mm']);mp=(np.c_[rp,np.ones(len(rp))]@Q.T)[:,:3];dr=np.array(list(root))-mp[0];dt=np.array(list(tip))-mp[-1];base=mp+np.linspace(1,0,len(mp))[:,None]*dr+np.linspace(0,1,len(mp))[:,None]*dt
   for x1,z1,x2,z2 in itertools.product([-4,-2,0,2,4],repeat=4):
    pp=base.copy();pp[1]+=H[:3,:3]@np.array([x1,0,z1]);pp[2]+=H[:3,:3]@np.array([x2,0,z2]);poles=[A.Vector(*v) for v in pp];candidates.append((curve(poles).toShape().Length,poles))
  if tail=='LowerSupport':
   for exitlen,dy,backx,backy,backz,reach in itertools.product([4,7,10],[0,4],[11,15,20],[-5,5,14,22],[-10,-16],[4,8]):
    p1=root+A.Vector(0,dy,exitlen*(1 if side=='Right' else -1))
    p2=HP.multVec(A.Vector(backx,backy,backz))
    p3=tip+HP.Rotation.multVec(A.Vector(1.,.7 if phi>0 else -.7,0))*reach
    poles=[root,p1,p2,p3,tip];candidates.append((curve(poles).toShape().Length,poles))
  for i,(length,poles) in enumerate(sorted(candidates,key=lambda r:r[0])):
   pp=np.array([list(p) for p in poles]);u=np.linspace(0,1,101)[:,None];degree=len(pp)-1
   def bez(q):
    n=len(q)-1
    return sum(math.comb(n,j)*(1-u)**(n-j)*u**j*q[j] for j in range(n+1))
   v=degree*bez(np.diff(pp,axis=0));a=degree*(degree-1)*bez(np.diff(pp,n=2,axis=0));k=np.linalg.norm(np.cross(v,a),axis=1)/np.maximum(np.linalg.norm(v,axis=1),1e-9)**3
   if max(k)>.45:continue
   centers=bez(pp)
   hc=(centers-H[:3,3])@H[:3,:3]
   if np.any(np.all((hc>[-9,-3,-8])&(hc<[9,19,9.2]),axis=1)):continue
   if i%20==0:print('SEARCH',name,i,fail,flush=True)
   try:s=make(poles,w,rad,axis,.6)
   except Exception:continue
   if not s.isValid() or len(s.Solids)!=1:continue
   # Keep the camera body and its front/side access envelope out of the arm loop.
   if s.common(keep).Volume>1e-6:fail['camera_access']=fail.get('camera_access',0)+1;continue
   mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
   if not mesh.isSolid() or mesh.hasSelfIntersections():continue
   bad=None
   for n,om in obmeshes.items():
    if not s.BoundBox.intersect(obs[n].BoundBox):continue
    both=mesh.copy();count=both.CountFacets;both.addMesh(om)
    if any((p[0]<count)!=(p[1]<count) for p in both.getSelfIntersections()):bad=n;break
   if bad:fail[bad]=fail.get(bad,0)+1;continue
   seats=[s.common(central).Volume,s.common(socket).Volume]
   if min(seats)<.7:fail['seat']=fail.get('seat',0)+1;continue
   if tail=='LowerSupport':
    other=accepted[-1];zone=Part.makeSphere(4.7,HP.multVec(A.Vector(center.x,center.y,-8.7)))
    gap=s.cut(central).cut(zone).distToShape(other.cut(central).cut(zone))[0]
    if gap<.3:fail['arm_gap']=fail.get('arm_gap',0)+1;continue
   fused=central.multiFuse([s,socket]);
   if not fused.isValid() or len(fused.Solids)!=1:fail['fusion']=fail.get('fusion',0)+1;continue
   assign(d.getObject(name),moved(s,T));accepted.append(s);records[name]={'poles_mm':[list(p) for p in poles],'length_mm':length,'root_width_mm':3.96,'root_thickness_mm':2.22,'tip_width_mm':2.92,'tip_thickness_mm':2.16,'engagement_mm3':seats,'socket_attachment_head_mm':list(th),'socket_radial_head':list(rdir),'camera_access_keepout_overlap_mm3':s.common(keep).Volume,'root_adjustment_mount_mm':[0,0,-1.5] if name=='LeftLowerSupport' else [0,0,0]};print('ACCEPT',name,records[name],flush=True);break
  else:raise RuntimeError((name,fail))
  d.recompute();d.saveAs(str(O/'04-arms-working.FCStd'));(O/'04-arms.json').write_text(json.dumps(records,indent=2))
assert len(records)==4
carrier=central.multiFuse(accepted+[local(d.getObject(s+'RetainedSocket')) for s in ['Right','Left']]).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1;assign(d.FinishedCarrier,moved(carrier,T));save(d,'04-arms',records)

