from pathlib import Path
import sys,json,hashlib,zipfile,math
import numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/refined-supports-r38';O=R/'generated/eye-tracker/rat/refined-supports-r38';O.mkdir(parents=True,exist_ok=True)
P=S.parent/'symmetric-binocular-r37';PO=R/'generated/eye-tracker/rat/symmetric-binocular-r37'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
cfg=json.loads((P/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);inv=np.linalg.inv(T)
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):return s.transformed(pose(t).toMatrix())
def local(o):return moved(world(o),inv)
def mirrorpoint(p):return pose(inv).multVec(A.Vector(*(np.array(list(pose(T).multVec(p)))*[1,-1,1])))
def mirrorvec(v):return pose(inv).Rotation.multVec(A.Vector(*(np.array(list(pose(T).Rotation.multVec(v)))*[1,-1,1])))
def unit(v):v=A.Vector(v);v.normalize();return v
def load(stage=None):
 m=json.loads((P/'review.json').read_text());p=R/m['native_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256']
 return A.openDocument(str(O/(stage+'.FCStd') if stage else p))
def obstacles(d):
 obs={}
 for side in ['Right','Left']:
  for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','ribbon']:
   s=Part.Shape();s.read(str((O if (O/(side+'-'+n+'.brep')).exists() else PO)/(side+'-'+n+'.brep')));obs[side+n]=s
  for n in ['eye_primary_Holder','eye_primary_Clip']:obs[side+n]=local(d.getObject(side+n))
 return obs
def curve(poles):c=Part.BezierCurve();c.setPoles(poles);return c
def section(c,t,w,width,thick,rounded=False):
 if rounded:
  n=unit(w.cross(t));a=width/2;b=thick/2;r=.3;v=lambda x,y:c+w*x+n*y;k=r/math.sqrt(2)
  points=[(a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r),(-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r)]
  mids={1:(-a+r-k,b-r+k),3:(-a+r-k,-b+r-k),5:(a-r+k,-b+r-k),7:(a-r+k,b-r+k)};edges=[]
  for i in range(8):
   p=v(*points[i]);q=v(*points[(i+1)%8]);edges.append(Part.Arc(p,v(*mids[i]),q).toShape() if i in mids else Part.makeLine(p,q))
  return Part.Wire(edges)
 n=unit(w.cross(t));a=width/2;b=thick/2;r=.2;xy=[(a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r),(-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r)];vs=[c+w*x+n*y for x,y in xy];return Part.makePolygon(vs+[vs[0]])
def make(poles,w0,radial,axis,reinforced=False):
 c=curve(poles);frames=[];w=A.Vector(w0);prev=None
 for i in range(49):
  t=c.tangent(i/48)[0]
  if prev is not None:w=A.Rotation(prev,t).multVec(w)
  w=unit(w-t*w.dot(t));frames.append((c.value(i/48),t,w));prev=t
 target=unit(radial.cross(axis))
 if target.dot(w)<0:target=-target
 angle=math.degrees(math.atan2(t.dot(w.cross(target)),w.dot(target)));wires=[]
 for i,(p,t,w) in enumerate(frames):
  u=i/48;w=A.Rotation(t,angle*u*u*(3-2*u)).multVec(w)
  width=2.2+.8*(1-u)**2;thick=1.8
  if reinforced:width+=float(reinforced)*(1.6*math.exp(-(u/.16)**2)+1.2*math.exp(-((1-u)/.18)**2));thick+=float(reinforced)*(.7*math.exp(-(u/.16)**2)+.6*math.exp(-((1-u)/.18)**2))
  wires.append(section(p,t,w,width,thick,False))
 return Part.makeLoft(wires[::3],True,False,False,3)
oldarms=json.loads((S.parent/'compact-binocular-r32/arms.json').read_text());oldsocket=json.loads((S.parent/'oval-camera-r21/arms.json').read_text())['RearRibbonGuard']
def params(side,tail):
 poles=[A.Vector(*v) for v in oldarms['Right'+tail]['poles_mm']];D=pose(cfg['sides']['Right']['head_delta']);axis=D.Rotation.multVec(A.Vector(*oldsocket['socket_axis']));rad=unit(poles[-2]-poles[-1]);w=A.Vector(0,1,0)
 if side=='Left':poles=[mirrorpoint(p) for p in poles];axis=mirrorvec(axis);rad=mirrorvec(rad);w=mirrorvec(w)
 return poles,w,rad,axis
def rebuild(d):
 pieces=[local(d.getObject(side+tail)) for side in ['Right','Left'] for tail in ['RetainedSocket','UpperSupport','LowerSupport']]
 s=local(d.CentralCarrier).multiFuse(pieces)
 if not s.isValid():
  s=local(d.CentralCarrier)
  for p in pieces:s=s.fuse(p,1e-5)
 refined=s.removeSplitter()
 if refined.isValid():s=refined
 assert s.isValid() and len(s.Solids)==1,(s.isValid(),len(s.Solids));assign(d.FinishedCarrier,moved(s,T));return s
def save(d,stage,report):
 d.recompute();p=O/(stage+'.FCStd');d.saveAs(str(p))
 with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
 (O/(stage+'.json')).write_text(json.dumps(report,indent=2));(S/(stage+'.json')).write_text(json.dumps(report,indent=2));A.closeDocument(d.Name)
