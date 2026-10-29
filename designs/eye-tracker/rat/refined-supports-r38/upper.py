from common import *
import itertools
d=load();obs=obstacles(d);central=local(d.CentralCarrier);report={}
for side in ['Right','Left']:
 old,w,rad,axis=params(side,'UpperSupport');root=old[0];tip=old[-1];socket=local(d.getObject(side+'RetainedSocket'));other=local(d.getObject(side+'LowerSupport'));sign=1 if side=='Right' else -1;candidates=[];rejections={}
 for lift,out,handle in itertools.product([0,2,4,6],[3,5,8,11],[2.5,4,6]):
  poles=[root,root+A.Vector(0,lift,sign*out),tip+rad*handle,tip];length=curve(poles).toShape().Length;candidates.append((length,poles))
 for length,poles in sorted(candidates,key=lambda q:q[0]):
  try:s=make(poles,w,rad,axis)
  except Exception:continue
  if not s.isValid() or len(s.Solids)!=1:continue
  bad=next((n for n,b in obs.items() if s.common(b).Volume>1e-5),None)
  if bad:rejections[bad]=rejections.get(bad,0)+1;continue
  seats={'central':s.common(central).Volume,'socket':s.common(socket).Volume}
  if min(seats.values())<.1:continue
  gap=s.distToShape(obs[side+'ribbon'])[0]
  if gap<.5:continue
  if s.cut(central).cut(socket).distToShape(other.cut(central).cut(socket))[0]<.3:continue
  trial=central.multiFuse([s,socket,other]).removeSplitter()
  if not trial.isValid() or len(trial.Solids)!=1:continue
  assert length<curve(old).toShape().Length*.8
  assign(d.getObject(side+'UpperSupport'),moved(s,T));report[side]={'poles_mm':[list(p) for p in poles],'old_length_mm':curve(old).toShape().Length,'new_length_mm':length,'ribbon_gap_mm':gap,'seating_mm3':seats};print('UPPER_ACCEPTED',side,report[side],flush=True);break
 else:raise RuntimeError((side,rejections))
rebuild(d);save(d,'01-upper',report)
