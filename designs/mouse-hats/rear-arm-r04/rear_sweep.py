"""Smooth rear sweep with fixed interface sections and a single low-degree path."""
import math
import FreeCAD as App
import Part
from attachment_arm_features import unit,rectangle

def geometry(data,settings,drop):
    a=data['arm'];n=unit(data['socket_axis']);radial=unit(a['radial_direction'])
    root=App.Vector(*a['root_mm']);t0=unit(a['root_tangent']);w0=unit(a['root_width_direction'])
    poles=[App.Vector(*p) for p in settings['poles_mm']]
    # The sum of degree-5 Bernstein weights B2+B3 is 0.625 at u=0.5.
    for i in [2,3]:poles[i]+=App.Vector(0,-drop/.625,0)
    curve=Part.BezierCurve();curve.setPoles(poles)
    count=49;centers=[curve.value(i/(count-1)) for i in range(count)]
    tangents=[curve.tangent(i/(count-1))[0] for i in range(count)]
    widths=[w0]
    for b,c in zip(tangents,tangents[1:]):widths.append(App.Rotation(b,c).multVec(widths[-1]))
    target=unit(radial.cross(n))
    if widths[-1].dot(target)<0:target=-target
    angle=math.degrees(math.atan2(tangents[-1].dot(widths[-1].cross(target)),widths[-1].dot(target)))
    wires=[]
    for i,(c,t,w) in enumerate(zip(centers,tangents,widths)):
        u=i/(count-1);smooth=u*u*(3-2*u);w=App.Rotation(t,angle*smooth).multVec(w)
        if u<=.5:
            q=2*u;q=q*q*(3-2*q);bw=a['root_width_mm']*(1-q)+3*q;bt=a['root_thickness_mm']*(1-q)+1.8*q
        else:
            q=2*u-1;q=q*q*(3-2*q);bw=3;bt=1.8*(1-q)+2.2*q
        wires.append(rectangle(c,t,w,bw,bt))
    end=App.Vector(*data['socket_center_mm'])+n*data['attachment_height_mm']+radial*data['attachment_radius_mm']
    rootcap=rectangle(root,t0,w0,a['root_width_mm'],a['root_thickness_mm'])
    endcap=rectangle(end,-radial,target,3,2.2)
    solid=Part.makeLoft([rootcap,wires[0]],True,True).fuse(Part.makeLoft(wires,True,False)).fuse(Part.makeLoft([wires[-1],endcap],True,True)).removeSplitter()
    solid.check(True)
    if not solid.isValid() or len(solid.Solids)!=1:raise ValueError('Rear sweep must form one valid solid')
    return solid,curve.toShape(),{'frame_twist_deg':angle,'centerline_min_y_mm':min(c.y for c in centers),'path_length_mm':curve.toShape().Length}
