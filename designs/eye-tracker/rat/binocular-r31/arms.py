"""Build separated support pairs around the two solved ribbon routes."""
from pathlib import Path
import sys,json,math,zipfile,itertools
import numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/binocular-r31';O=R/'generated/eye-tracker/rat/binocular-r31'
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
 for name,y,ang in [('UpperSupport',17.5,-10),('LowerSupport',8.,50)]:
  root=B.multVec(A.Vector(4.5,y,16.8));rad=D.Rotation.multVec(A.Rotation(axis0,ang).multVec(rad0));tip=sc+axis*3.7+rad*2.3;accepted=None
  for i,(rh,sh,shift) in enumerate(itertools.product([1.,.7,1.3,1.6],[24.,16.,10.,30.],[0.,3.,-3.,6.,-6.])):
   poles=[root,root+B.Rotation.multVec(A.Vector(-14*rh,shift,20*rh)),tip+rad*sh,tip]
   try:arm=make(poles,B.Rotation.multVec(A.Vector(0,1,0)),rad,axis)
   except Exception:continue
   if not arm.isValid() or len(arm.Solids)!=1:continue
   seat={'central':arm.common(central).Volume,'socket':arm.common(socket).Volume}
   if min(seat.values())<.1:continue
   checks={n:arm.common(s).Volume for n,s in obs.items()};bad={n:v for n,v in checks.items() if v>1e-5}
   if bad:
    if i%10==0:print(side,name,i,'collision',bad,flush=True)
    continue
   free=arm.cut(central).cut(socket);gaps=[free.distToShape(a.cut(central).cut(socket))[0] for a in arms];overlaps=[arm.common(a).Volume for a in arms]
   if any(x<.3 for x in gaps) or any(x>1e-6 for x in overlaps):continue
   gap=arm.distToShape(obs[side+'ribbon'])[0]
   if gap<.65:continue
   accepted=arm;report[side+name]={'poles_mm':[list(v) for v in poles],'seating_mm3':seat,'ribbon_gap_mm':gap,'checks_mm3':checks,'free_span_gaps_mm':gaps};print('ACCEPTED',side,name,i,'gap',gap,'seat',seat,flush=True);break
  if accepted is None:raise RuntimeError('No accepted support: '+side+name)
  arms.append(accepted);allarms.append(accepted);o=d.addObject('Part::Feature',side+name);o.Shape=moved(accepted,T);accepted.exportBrep(str(O/(side+'-'+name+'.brep')))
carrier=central.multiFuse([*sockets.values(),*allarms]).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
for n,s in obs.items():
 overlap=carrier.common(s).Volume;assert overlap<1e-5,(n,overlap)
o=d.addObject('Part::Feature','FinishedCarrier');o.Shape=moved(carrier,T);carrier.exportBrep(str(O/'carrier.brep'));(S/'arms.json').write_text(json.dumps(report,indent=2));d.recompute();p=O/'ET-RAT-BINOCULAR-R31.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);print('BRANCHES_SAVED')
