"""Smooth Bezier spans with a front-edge root and preserved socket terminal."""
import math
import FreeCAD as A,Part

def unit(v):
 v=A.Vector(*v) if not isinstance(v,A.Vector) else A.Vector(v);v.normalize();return v

def rectangle(c,t,w,b,h):
 n=unit(w.cross(t));pts=[c+w*(x*b/2)+n*(y*h/2) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return Part.makePolygon(pts+[pts[0]])

def build(p,outer):
 a=p['arm'];root=A.Vector(*a['root_mm']);t0=unit(a['root_tangent']);w0=unit(a['root_width_direction']);n=unit(p['socket_axis']);radial=unit(a['radial_direction'])
 start=root+t0*(p['embed_mm']+p['root_lead_mm']);end=A.Vector(*p['socket_center_mm'])+n*p['attachment_height_mm']+radial*p['attachment_radius_mm'];stop=end+radial*p['socket_lead_mm']
 mid=A.Vector(*outer);tm=A.Vector(0,0,1)
 curves=[]
 if 'lead_corner_mm' in p:
  corner=A.Vector(*p['lead_corner_mm']);tc=unit(A.Vector(-1,0,-.4))
  spans=[[start,start+t0*2.5,corner-tc*2,corner],[corner,corner+tc*4,mid-tm*5,mid],[mid,mid+tm*p.get('turn_exit_handle_mm',8),stop+radial*5,stop]]
 else:spans=[[start,start+t0*6,mid-tm*p.get("turn_entry_handle_mm",6),mid],[mid,mid+tm*p.get('turn_exit_handle_mm',6),stop+radial*5,stop]]
 for poles in spans:
  c=Part.BezierCurve();c.setPoles(poles);curves.append(c)
 samples=[(c.value(i/32),c.tangent(i/32)[0]) for j,c in enumerate(curves) for i in range(0 if j==0 else 1,33)]
 widths=[w0]
 for (_,t0),(_,t1) in zip(samples,samples[1:]):widths.append(A.Rotation(t0,t1).multVec(widths[-1]))
 target=unit(radial.cross(n))
 if widths[-1].dot(target)<0:target=-target
 tangent=samples[-1][1];angle=math.degrees(math.atan2(tangent.dot(widths[-1].cross(target)),widths[-1].dot(target)))
 wires=[]
 for i,((c,t),w) in enumerate(zip(samples,widths)):
  u=i/(len(samples)-1);w=A.Rotation(t,angle*u*u*(3-2*u)).multVec(w)
  if u<.5:
   q=2*u;q=q*q*(3-2*q);b=a['root_width_mm']*(1-q)+2.6*q;h=a['root_thickness_mm']*(1-q)+1.8*q
  else:
   q=2*u-1;q=q*q*(3-2*q);b=2.6*(1-q)+3*q;h=1.8*(1-q)+2.2*q
  wires.append(rectangle(c,t,w,b,h))
 pieces=[Part.makeLoft(wires[i*32:i*32+33:2],True,False,False,3) for i in range(len(curves))]
 body=pieces[0].multiFuse(pieces[1:])
 lead=Part.makeLoft([rectangle(root,unit(a['root_tangent']),w0,a['root_width_mm'],a['root_thickness_mm']),wires[0]],True,True)
 tip=Part.makeLoft([wires[-1],rectangle(end-radial*.8,-radial,target,3,2.2)],True,True)
 sh=lead.fuse(body).fuse(tip).removeSplitter();sh.check(True);assert sh.isValid() and len(sh.Solids)==1
 return sh


