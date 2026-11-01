"""Keep the left lower guard behind its ribbon in the final top-view review."""
from common import *
import itertools
d=load('04-junctions');obs=obstacles(d);central=local(d.CentralCarrier);socket=local(d.LeftRetainedSocket);other=local(d.LeftUpperSupport);_,w,rad,axis=params('Left','LowerSupport');base,_,_,_=params('Left','LowerSupport');root=base[0];tip=base[-1]
rc=curve([A.Vector(*p) for p in json.loads((S/'ribbons.json').read_text())['Left']['centerline_poles_mm']]);rp=np.array([list(rc.value(i/100)) for i in range(101)])[:,[0,2]];candidates=[];records=json.loads((S/'04-junctions.json').read_text())
rpol=[A.Vector(*p) for p in json.loads((S/'ribbons.json').read_text())['Left']['centerline_poles_mm']]
for back,drop,start_h,end_h in itertools.product([2,4,6,8,10,12],[0,2,4,6],[4,7,10],[4,7,10]):
 p=[root-unit(A.Vector(-2,-1,-start_h))*.35,root+A.Vector(-2,-1,-start_h),rpol[2]+A.Vector(-back,-drop,0),rpol[3]+A.Vector(-back,-drop,0),tip+rad*end_h,tip-rad*.15];c=curve(p);offset=min(rc.value(float(u)).x-c.value(float(u)).x for u in np.linspace(.25,.65,25))
 if offset<.5:continue
 q=np.array([list(c.value(i/60)) for i in range(61)])[:,[0,2]];dist=float(np.sqrt(((q[:,None,:]-rp[None,:,:])**2).sum(axis=2)).min(axis=1).mean());length=c.toShape().Length
 if length>=curve(base).toShape().Length or dist>=5.9128:continue
 candidates.append((dist+length*.01,p,offset,length,dist))
print('OUTER_GUARD_CANDIDATES',len(candidates),flush=True)
for j,(_,p,offset,length,dist) in enumerate(sorted(candidates,key=lambda x:x[0])):
 for scale in [.6,.8]:
  s=make(p,w,rad,axis,scale)
  if not s.isValid() or len(s.Solids)!=1:continue
  for side in ['Right','Left']:
   board=obs[side+'PCB']
   if s.common(board).Volume>1e-5:
    b=board.BoundBox;s=s.cut(Part.makeBox(b.XLength+.1,b.YLength+.1,b.ZLength+.1,A.Vector(b.XMin-.05,b.YMin-.05,b.ZMin-.05))).removeSplitter()
  if not s.isValid() or len(s.Solids)!=1:continue
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
  if not mesh.isSolid() or mesh.hasSelfIntersections():continue
  if any(s.common(b).Volume>1e-5 for b in obs.values()):continue
  gap=s.distToShape(obs['Leftribbon'])[0]
  if gap<.65:continue
  seats=[s.common(central).Volume,s.common(socket).Volume]
  if min(seats)<2:continue
  free=s.cut(central).cut(socket).cut(Part.makeSphere(4,p[-1]));freeother=other.cut(central).cut(socket).cut(Part.makeSphere(4,p[-1]));freegap=free.distToShape(freeother)[0]
  if freegap<.3:continue
  assign(d.LeftLowerSupport,moved(s,T))
  try:carrier=rebuild(d)
  except Exception:continue
  records['LeftLowerSupport'].update(flare_scale=scale,root_width_mm=3+1.6*scale,root_thickness_mm=1.8+.7*scale,tip_width_mm=2.2+1.2*scale,tip_thickness_mm=1.8+.6*scale,poles_mm=[list(v) for v in p],new_engagement_mm3=seats,arm_free_gap_mm=freegap,ribbon_gap_mm=gap,minimum_plan_caudal_offset_mm=offset,finished_length_mm=length,mean_plan_distance_to_ribbon_mm=dist)
  (S/'04-junctions.json').write_text(json.dumps(records,indent=2));print('OUTER_GUARD_ACCEPTED',records['LeftLowerSupport'],flush=True);save(d,'visual-arm-working',records);raise SystemExit(0)
 if j%10==0:print('candidate',j,flush=True)
raise RuntimeError('No outer guard route passed')

