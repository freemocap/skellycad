import FreeCAD as A, Part, math
from guard import unit,rectangle
def build(p,outer=None):
 a=p['arm']
 root=A.Vector(*a['root_mm']); t0=unit(a['root_tangent']); w0=unit(a['root_width_direction']); radial=unit(a['radial_direction']); n=unit(p['socket_axis'])
 start=root+t0*p['embed_mm']; end=A.Vector(*p['socket_center_mm'])+n*p['attachment_height_mm']+radial*p['attachment_radius_mm']; stop=end+radial*p['socket_lead_mm']
 # One polynomial span: no internal curve junction or tangent/curvature discontinuity.
 poles=[start,start+t0*6,A.Vector(-9,2,17.5),A.Vector(-9,0,30),stop+radial*5,stop]
 c=Part.BezierCurve(); c.setPoles(poles)
 samples=[(c.value(i/48),c.tangent(i/48)[0]) for i in range(49)]
 widths=[w0]
 for (_,u),(_,v) in zip(samples,samples[1:]): widths.append(A.Rotation(u,v).multVec(widths[-1]))
 target=unit(radial.cross(n))
 if widths[-1].dot(target)<0:target=-target
 t=samples[-1][1]; angle=math.degrees(math.atan2(t.dot(widths[-1].cross(target)),widths[-1].dot(target)))
 wires=[]
 for i,((pos,t),w) in enumerate(zip(samples,widths)):
  u=i/48; w=A.Rotation(t,angle*u*u*(3-2*u)).multVec(w)
  q=min(1,2*u);q=q*q*(3-2*q); b=a['root_width_mm']*(1-q)+2.6*q; h=a['root_thickness_mm']*(1-q)+1.8*q
  if u>.5:
   q=2*u-1;q=q*q*(3-2*q);b=2.6*(1-q)+3*q;h=1.8*(1-q)+2.2*q
  wires.append(rectangle(pos,t,w,b,h))
 arm=Part.makeLoft(wires,True,False,False,5)
 arm=arm.fuse(Part.makeLoft([rectangle(root,t0,w0,a['root_width_mm'],a['root_thickness_mm']),wires[0]],True,True))
 arm=arm.fuse(Part.makeLoft([wires[-1],rectangle(end-radial*.8,-radial,target,3,2.2)],True,True)).removeSplitter()
 assert arm.isValid() and len(arm.Solids)==1
 return arm
