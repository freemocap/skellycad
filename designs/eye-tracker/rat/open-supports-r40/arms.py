from support import *
import itertools
sys.path.insert(0,str(S.parent/'refined-supports-r38'));from common import unit,curve,section
import math
def make(poles,w0,radial,axis,reinforced=.6):
 c=curve(poles);frames=[];w=A.Vector(w0);prev=None
 for i in range(49):
  t=c.tangent(i/48)[0]
  if prev is not None:w=A.Rotation(prev,t).multVec(w)
  w=unit(w-t*w.dot(t));frames.append((c.value(i/48),t,w));prev=t
 target=unit(radial.cross(axis))
 if target.dot(w)<0:target=-target
 angle=math.degrees(math.atan2(t.dot(w.cross(target)),w.dot(target)));wires=[]
 for i,(p,t,w) in enumerate(frames):
  u=i/48;w=A.Rotation(t,angle*u*u*(3-2*u)).multVec(w);width=3.4+.6*(1-u)**2+.6*(1.6*math.exp(-(u/.16)**2)+1.2*math.exp(-((1-u)/.18)**2));thick=2.3+.6*(.7*math.exp(-(u/.16)**2)+.6*math.exp(-((1-u)/.18)**2));wires.append(section(p,t,w,width,thick,False))
 return Part.makeLoft(wires[::3],True,False,False,3)
source=json.loads((S.parent/'forward-mount-r39/review.json').read_text());d=load('source');central=local(d.CentralCarrier);old=json.loads((R/'generated/eye-tracker/rat/forward-mount-r39/04-arms.json').read_text());obs={n:v for n,v in obstacles(d).items() if 'keepout' not in n};obmeshes={n:MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False) for n,s in obs.items()};records={};accepted=[]
for side in ['Right','Left']:
 H=np.array(cfg['sides'][side]['head']);HP=pose(H);HI=HP.inverse();socket=local(d.getObject(side+'RetainedSocket'));headsocket=socket.transformed(HI.toMatrix());cyl=max([f.Surface for f in headsocket.Faces if isinstance(f.Surface,Part.Cylinder)],key=lambda s:s.Radius);center=cyl.Center;axis=HP.Rotation.multVec(A.Vector(0,0,1));keep=Part.makeBox(15,19,14.8,A.Vector(-7.5,-1.5,-6.8)).transformed(HP.toMatrix());keep.exportBrep(str(O/(side+'-camera-access-keepout.brep')))
 for tail in ['UpperSupport']:
  name=side+tail
  if name in records:accepted.append(local(d.getObject(name)));continue
  root=A.Vector(*old[name]['poles_mm'][0]);rh=HI.multVec(root);phi=0;angle=np.deg2rad(phi);rdir=A.Vector(float(np.cos(angle)),float(np.sin(angle)),0);th=A.Vector(center.x,center.y,-8.7)+rdir*2.0;tip=HP.multVec(th);rad=HP.Rotation.multVec(rdir);w=A.Vector(0,1,0);candidates=[];fail={}
  for back,reach,out,along in itertools.product([4,7,10,14,18,24],[3,5,8,12,16],[0,3,6,10,16],[-12,-8,-3,0,3,8,12]):
   p1=HP.multVec(rh+A.Vector(out,along,-back));p2=tip+rad*reach;poles=[root,p1,p2,tip];candidates.append((curve(poles).toShape().Length,poles))
  for i,(length,poles) in enumerate(sorted(candidates,key=lambda r:r[0])):
   pp=np.array([list(p) for p in poles]);u=np.linspace(0,1,101)[:,None];v=3*(1-u)**2*(pp[1]-pp[0])+6*(1-u)*u*(pp[2]-pp[1])+3*u*u*(pp[3]-pp[2]);a=6*(1-u)*(pp[2]-2*pp[1]+pp[0])+6*u*(pp[3]-2*pp[2]+pp[1]);k=np.linalg.norm(np.cross(v,a),axis=1)/np.maximum(np.linalg.norm(v,axis=1),1e-9)**3
   if max(k)>.5:continue
   if i%40==0:print('SEARCH',name,i,fail,flush=True)
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
   if min(seats)<1.5:fail['seat']=fail.get('seat',0)+1;continue
   if tail=='LowerSupport':
    other=accepted[-1];zone=socket.makeOffsetShape(1.,.01)
    gap=s.cut(central).cut(zone).distToShape(other.cut(central).cut(zone))[0]
    if gap<.3:fail['arm_gap']=fail.get('arm_gap',0)+1;continue
   fused=central.multiFuse([s,socket]);
   if not fused.isValid() or len(fused.Solids)!=1:fail['fusion']=fail.get('fusion',0)+1;continue
   assign(d.getObject(name),moved(s,T));accepted.append(s);records[name]={'poles_mm':[list(p) for p in poles],'length_mm':length,'root_width_mm':4.96,'root_thickness_mm':2.72,'tip_width_mm':4.12,'tip_thickness_mm':2.66,'engagement_mm3':seats,'socket_attachment_head_mm':list(th),'socket_radial_head':list(rdir),'camera_access_keepout_overlap_mm3':s.common(keep).Volume};print('ACCEPT',name,records[name],flush=True);break
  else:raise RuntimeError((name,fail))
  d.recompute();d.saveAs(str(O/'04-arms-working.FCStd'));(O/'04-arms.json').write_text(json.dumps(records,indent=2))
for side in ['Right','Left']:d.removeObject(side+'LowerSupport')
carrier=central.multiFuse(accepted+[local(d.getObject(s+'RetainedSocket')) for s in ['Right','Left']]).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1;assign(d.FinishedCarrier,moved(carrier,T));save(d,'04-arms',records)

