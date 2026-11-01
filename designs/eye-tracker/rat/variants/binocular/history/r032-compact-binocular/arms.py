"""Build separated support pairs around the two solved ribbon routes."""
from pathlib import Path
import sys,json,math,zipfile,itertools
import numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/compact-binocular-r32';O=R/'generated/eye-tracker/rat/compact-binocular-r32'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);d=A.openDocument(str(O/'ribbons.FCStd'))
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):
 s=s.copy();s.Placement=pose(t).multiply(s.Placement);return s
def unit(v):
 v=A.Vector(v);v.normalize();return v
def section(c,t,w,width,thick):
 n=unit(w.cross(t));a=width/2;b=thick/2;r=.2;xy=[(a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r),(-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r)];vs=[c+w*x+n*y for x,y in xy];return Part.makePolygon(vs+[vs[0]])
def make(poles,w0,radial,axis):
 curve=Part.BezierCurve();curve.setPoles(poles);frames=[];w=A.Vector(w0);old=None
 for i in range(65):
  t=curve.tangent(i/64)[0]
  if old is not None:w=A.Rotation(old,t).multVec(w)
  w=unit(w-t*w.dot(t));frames.append((curve.value(i/64),t,w));old=t
 target=unit(radial.cross(axis))
 if target.dot(w)<0:target=-target
 angle=math.degrees(math.atan2(t.dot(w.cross(target)),w.dot(target)));wires=[]
 for i,(c,t,w) in enumerate(frames):
  u=i/64;w=A.Rotation(t,angle*u*u*(3-2*u)).multVec(w);wires.append(section(c,t,w,2.2+.8*(1-u)**2,1.8))
 return Part.makeLoft(wires[::4],True,False,False,3)
central=Part.Shape();central.read(str(O/'central.brep'));obs={};sockets={}
for side in cfg['sides']:
 for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','ribbon']:
  s=Part.Shape();s.read(str(O/(side+'-'+n+'.brep')));obs[side+n]=s
 for n in ['eye_primary_Holder','eye_primary_Clip']:obs[side+n]=world(d.getObject(side+n)).transformed(pose(T).inverse().toMatrix())
 sockets[side]=world(d.getObject(side+'RetainedSocket')).transformed(pose(T).inverse().toMatrix())
old=json.loads((S.parent/'oval-camera-r21/arms.json').read_text())['RearRibbonGuard'];sc0=A.Vector(*old['socket_center_mm']);axis0=unit(A.Vector(*old['socket_axis']));rad0=unit(A.Vector(-.85483722,-.29828025,.42459653));rad0=unit(rad0-axis0*rad0.dot(axis0));allarms=[];report={}
for side,rec in cfg['sides'].items():
 B=pose(rec['board_transform']);D=pose(rec['head_delta']);sc=D.multVec(sc0);axis=D.Rotation.multVec(axis0);socket=sockets[side];arms=[]
 # Both protective arches must depart caudally (-mount X), regardless of board handedness.
 back=unit(A.Vector(-1,0,0)-axis*axis.dot(A.Vector(-1,0,0)));sign=1 if side=='Right' else -1
 ribbon_curve=Part.BezierCurve();ribbon_curve.setPoles([A.Vector(*v) for v in json.loads((S/'ribbons.json').read_text())[side]['centerline_poles_mm']])
 for name,y,ang in [('UpperSupport',17.5,-10),('LowerSupport',8.,50)]:
  if side=='Left':ang=50 if name=='UpperSupport' else -10
  root=B.multVec(A.Vector(4.5,y,16.8));rad=unit(A.Rotation(axis,ang).multVec(back));tip=sc+axis*3.7+rad*2.3;accepted=None;reasons={};maxgap=0
  def reject(reason):reasons[reason]=reasons.get(reason,0)+1
  for i,(rh,sh,shift) in enumerate(itertools.product([1.,.7,1.3,1.6],[16.,24.,10.,30.],[0.,3.,-3.,6.,-6.])):
   poles=[root,root+A.Vector(-14*rh,shift,sign*20*rh),tip+rad*sh,tip]
   if side=='Left':poles=[root,root+A.Vector(0,0,sign*4),root+A.Vector(-14*rh,shift,sign*20*rh),tip+rad*sh,tip]
   route=Part.BezierCurve();route.setPoles(poles);back_offsets=[ribbon_curve.value(float(u)).x-route.value(float(u)).x for u in np.linspace(.25,.65,24)]
   if min(back_offsets)<.5:reject('not_caudad');continue
   try:arm=make(poles,B.Rotation.multVec(A.Vector(0,1,0)),rad,axis)
   except Exception:continue
   if not arm.isValid() or len(arm.Solids)!=1:continue
   seat={'central':arm.common(central).Volume,'socket':arm.common(socket).Volume}
   if min(seat.values())<.1:reject('seating '+str(seat));continue
   checks={n:arm.common(s).Volume for n,s in obs.items()};bad={n:v for n,v in checks.items() if v>1e-5}
   if bad:
    reject('collision '+','.join(bad))
    if i%10==0:print(side,name,i,'collision',bad,flush=True)
    continue
   free=arm.cut(central).cut(socket);gaps=[free.distToShape(a.cut(central).cut(socket))[0] for a in arms];overlaps=[arm.common(a).Volume for a in arms]
   if any(x<.3 for x in gaps) or any(x>1e-6 for x in overlaps):reject('arm_pair');continue
   order_gap=None
   if arms:
    uppercurve=Part.BezierCurve();uppercurve.setPoles([A.Vector(*v) for v in report[side+'UpperSupport']['poles_mm']]);order_gap=min(uppercurve.value(float(u)).y-route.value(float(u)).y for u in np.linspace(0,1,101))
    if order_gap<.3:reject('crossed_vertical_order');continue
   gap=arm.distToShape(obs[side+'ribbon'])[0]
   maxgap=max(maxgap,gap)
   if gap<.65:reject('ribbon_gap');continue
   accepted=arm;report[side+name]={'poles_mm':[list(v) for v in poles],'minimum_caudal_offset_mm':min(back_offsets),'upper_lower_order_gap_mm':order_gap,'routing_check':'Arm centerline remains at least 0.5 mm caudal to corresponding ribbon centerline samples over 25-65 percent of its span','seating_mm3':seat,'ribbon_gap_mm':gap,'checks_mm3':checks,'free_span_gaps_mm':gaps};print('ACCEPTED',side,name,i,'gap',gap,'seat',seat,flush=True);break
  if accepted is None:print('REJECT_REASONS',side,name,reasons,'maxgap',maxgap,flush=True);raise RuntimeError('No accepted support: '+side+name)
  arms.append(accepted);allarms.append(accepted);o=d.addObject('Part::Feature',side+name);o.Shape=moved(accepted,T);accepted.exportBrep(str(O/(side+'-'+name+'.brep')));d.recompute();d.saveAs(str(O/'arms-working.FCStd'))
carrier=central.multiFuse([*sockets.values(),*allarms]).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
for n,s in obs.items():
 overlap=carrier.common(s).Volume;assert overlap<1e-5,(n,overlap)
o=d.addObject('Part::Feature','FinishedCarrier');o.Shape=moved(carrier,T);carrier.exportBrep(str(O/'carrier.brep'));(S/'arms.json').write_text(json.dumps(report,indent=2));d.recompute();p=O/'ET-RAT-COMPACT-BINOCULAR-R32.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);print('BRANCHES_SAVED')

