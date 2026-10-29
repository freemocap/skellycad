from common import *
import itertools
d=load('01-upper');obs=obstacles(d);central=local(d.CentralCarrier);report={};ribbons=json.loads((P/'ribbons.json').read_text())
for side in ['Right','Left']:
 old,w,rad,axis=params(side,'LowerSupport');root=old[0];tip=old[-1];socket=local(d.getObject(side+'RetainedSocket'));other=local(d.getObject(side+'UpperSupport'));sign=1 if side=='Right' else -1
 rc=curve([A.Vector(*p) for p in ribbons[side]['centerline_poles_mm']]);rp=np.array([list(rc.value(i/100)) for i in range(101)])[:,[0,2]]
 def metrics(poles):
  c=curve(poles);q=np.array([list(c.value(i/60)) for i in range(61)])[:,[0,2]];dist=np.sqrt(((q[:,None,:]-rp[None,:,:])**2).sum(axis=2)).min(axis=1)
  return float(dist.mean()),c.toShape().Length
 candidates=[];rejections={}
 for back,out,handle,dy in itertools.product([4,7,10,12],[9,12,15,18],[5,8,11,14,17],[0,-2]):
  poles=[root,root+A.Vector(-back,dy,sign*out),tip+rad*handle,tip];gap,length=metrics(poles);candidates.append((gap+length*.015,poles,gap,length))
 oldgap,oldlength=metrics(old)
 for _,poles,avg,length in sorted(candidates,key=lambda q:q[0]):
  if avg>=oldgap or length>=oldlength:continue
  try:s=make(poles,w,rad,axis)
  except Exception:continue
  if not s.isValid() or len(s.Solids)!=1:continue
  bad=next((n for n,b in obs.items() if s.common(b).Volume>1e-5),None)
  if bad:rejections[bad]=rejections.get(bad,0)+1;continue
  seats={'central':s.common(central).Volume,'socket':s.common(socket).Volume}
  if min(seats.values())<.1:continue
  gap=s.distToShape(obs[side+'ribbon'])[0]
  if gap<.65:continue
  if s.cut(central).cut(socket).distToShape(other.cut(central).cut(socket))[0]<.3:continue
  trial=central.multiFuse([s,socket,other]).removeSplitter()
  if not trial.isValid() or len(trial.Solids)!=1:continue
  assign(d.getObject(side+'LowerSupport'),moved(s,T));report[side]={'poles_mm':[list(p) for p in poles],'old_length_mm':oldlength,'new_length_mm':length,'old_mean_plan_distance_to_ribbon_mm':oldgap,'new_mean_plan_distance_to_ribbon_mm':avg,'ribbon_gap_mm':gap,'seating_mm3':seats};print('LOWER_ACCEPTED',side,report[side],flush=True);break
 else:raise RuntimeError((side,rejections))
rebuild(d);save(d,'02-lower',report)
