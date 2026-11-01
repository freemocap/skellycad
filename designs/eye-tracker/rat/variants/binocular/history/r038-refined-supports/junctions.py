from common import *
import itertools
d=load('03-plate');obs=obstacles(d);central=local(d.CentralCarrier);records={}
cuts=[]
for side in ['Right','Left']:
 b=obs[side+'PCB'].BoundBox;cuts.append(Part.makeBox(b.XLength+.1,b.YLength+.1,b.ZLength+.1,A.Vector(b.XMin-.05,b.YMin-.05,b.ZMin-.05)))
for side in ['Right','Left']:
 socket=local(d.getObject(side+'RetainedSocket'))
 for tail,stage in [('UpperSupport','01-upper'),('LowerSupport','02-lower')]:
  o=d.getObject(side+tail);old=local(o);poles=[A.Vector(*p) for p in json.loads((S/(stage+'.json')).read_text())[side]['poles_mm']];_,w,rad,axis=params(side,tail);oldseat=[old.common(central).Volume,old.common(socket).Volume];fail=[]
  original_poles=[A.Vector(p) for p in poles]
  candidates=[(2.,2.5,.6),(2.,2.5,.8),(2.5,2.5,.6),(3.,3.5,.6)] if tail=='UpperSupport' else list(itertools.product([1.,.85,1.15],[1.,.8,1.2],[.6,.8,1.]))
  for rf,tf,scale in candidates:
   print('TRY_JOINT',side+tail,rf,tf,scale,flush=True)
   poles=[original_poles[0]-unit(original_poles[1]-original_poles[0])*.35,original_poles[0]+(original_poles[1]-original_poles[0])*rf,original_poles[-1]+(original_poles[-2]-original_poles[-1])*tf,original_poles[-1]-rad*.15]
   try:s=make(poles,w,rad,axis,scale).cut(Part.makeCompound(cuts)).removeSplitter()
   except Exception as e:fail.append(str(e));continue
   if not s.isValid() or len(s.Solids)!=1:fail.append('invalid arm');continue
   mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
   if not mesh.isSolid() or mesh.hasSelfIntersections():fail.append('mesh');continue
   bad={n:s.common(b).Volume for n,b in obs.items() if s.common(b).Volume>1e-5}
   if bad:fail.append(bad);continue
   seat=[s.common(central).Volume,s.common(socket).Volume]
   if any(a<b*1.2 for a,b in zip(seat,oldseat)):fail.append(('seat',seat,oldseat));continue
   assign(o,moved(s,T))
   try:fused=rebuild(d)
   except Exception:assign(o,moved(old,T));fail.append('invalid fusion');continue
   other=local(d.getObject(side+('LowerSupport' if tail=='UpperSupport' else 'UpperSupport')))
   junction_zone=Part.makeSphere(4.,original_poles[-1])
   freegap=s.cut(central).cut(socket).cut(junction_zone).distToShape(other.cut(central).cut(socket).cut(junction_zone))[0]
   if freegap<.3:assign(o,moved(old,T));fail.append(('arm gap',freegap));continue
   records[side+tail]={'flare_scale':scale,'root_width_mm':3+1.6*scale,'root_thickness_mm':1.8+.7*scale,'tip_width_mm':2.2+1.2*scale,'tip_thickness_mm':1.8+.6*scale,'section_edge_chamfer_mm':.2,'poles_mm':[list(p) for p in poles],'root_handle_scale':rf,'socket_handle_scale':tf,'old_engagement_mm3':oldseat,'new_engagement_mm3':seat,'arm_free_gap_mm':freegap,'ribbon_gap_mm':s.distToShape(obs[side+'ribbon'])[0],'transition':'Continuous loft with smooth flared root and socket end, tangent-transported sections and chamfered longitudinal edges'};print('STRENGTHENED',side+tail,records[side+tail],flush=True);break
  else:raise RuntimeError((side+tail,fail[-15:]))
carrier=rebuild(d)
for name,s in obs.items():assert carrier.common(s).Volume<1e-5,(name,carrier.common(s).Volume)
save(d,'04-junctions',records)
