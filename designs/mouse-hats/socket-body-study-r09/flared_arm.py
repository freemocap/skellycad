"""Face-aligned root leads, smooth routing, and collar-contained end sections."""
import json,math
import FreeCAD as App
import Part

def unit(v):
    v=App.Vector(*v) if not isinstance(v,App.Vector) else App.Vector(v)
    v.normalize();return v

def rectangle(center,tangent,width_axis,width,thickness):
    h=unit(width_axis.cross(tangent))
    pts=[center+width_axis*(sx*width/2)+h*(sy*thickness/2)
         for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return Part.makePolygon(pts+[pts[0]])

def geometry(d,width,thickness):
    if width<=0 or thickness<=0:raise ValueError('Positive dimensions required')
    a=d['arm'];n=unit(d['socket_axis']);radial=unit(a['radial_direction'])
    root=App.Vector(*a['root_mm']);t0=unit(a['root_tangent']);w0=unit(a['root_width_direction'])
    # Keep root section straight and constant past the parent face before bending.
    start=root+t0*(d['embed_mm']+d['root_lead_mm'])
    flare=math.radians(d.get('plugward_flare_deg',0))
    if flare:
        # Keep X/depth and plate intersection center exactly at B's locations.
        # Plugward is negative assembly Z; width axis is assembly Y.
        root.z += d['embed_mm']*math.tan(flare)
        start.z -= d['root_lead_mm']*math.tan(flare)
        t0=unit(App.Vector(-1,0,-math.tan(flare)))
    end=App.Vector(*d['socket_center_mm'])+n*d['attachment_height_mm']+radial*d['attachment_radius_mm']
    stop=end+radial*d['socket_lead_mm']
    curve=Part.BezierCurve();curve.setPoles([start,start+t0*(a['root_handle_mm']/math.cos(flare)),
                                          stop+radial*a['socket_handle_mm'],stop])
    count=d['sections'];centers=[curve.value(i/(count-1)) for i in range(count)]
    tangents=[curve.tangent(i/(count-1))[0] for i in range(count)]
    widths=[w0]
    for b,c in zip(tangents,tangents[1:]):widths.append(App.Rotation(b,c).multVec(widths[-1]))
    target=unit(radial.cross(n))
    # A rectangle is invariant under 180-degree reversal: choose the smaller turn.
    if widths[-1].dot(target)<0:target=-target
    angle=math.degrees(math.atan2(tangents[-1].dot(widths[-1].cross(target)),widths[-1].dot(target)))
    wires=[]
    for i,(c,t,w) in enumerate(zip(centers,tangents,widths)):
        u=i/(count-1);smooth=u*u*(3-2*u)
        w=App.Rotation(t,angle*smooth).multVec(w)
        # End dimensions are boundary conditions, separate from body dimensions.
        if u<=.5:
            q=2*u;q=q*q*(3-2*q)
            bw=a['root_width_mm']*(1-q)+width*q;bt=a['root_thickness_mm']*(1-q)+thickness*q
        else:
            q=2*u-1;q=q*q*(3-2*q)
            bw=width*(1-q)+d['socket_width_mm']*q;bt=thickness*(1-q)+d['socket_thickness_mm']*q
        wires.append(rectangle(c,t,w,bw,bt))
    rootcap=rectangle(root,unit(a['root_tangent']),w0,a['root_width_mm'],a['root_thickness_mm'])
    endcap=rectangle(end,-radial,target,d['socket_width_mm'],d['socket_thickness_mm'])
    lead=Part.makeLoft([rootcap,wires[0]],True,True)
    body=Part.makeLoft(wires,True,False)
    tip=Part.makeLoft([wires[-1],endcap],True,True)
    solid=lead.fuse(body).fuse(tip).removeSplitter();solid.check(True)
    if len(solid.Solids)!=1:raise ValueError('Expected one arm solid')
    return solid,rootcap,endcap,curve.toShape(),angle

class SmoothArm:
    def __init__(self,obj,data):
        obj.addProperty('App::PropertyString','DesignJSON','Construction');obj.DesignJSON=json.dumps(data)
        for name,value in [('Width',data['width_mm']),('Thickness',data['thickness_mm']),
                           ('RootReach',data['arm']['root_handle_mm']),('SocketReach',data['arm']['socket_handle_mm'])]:
            obj.addProperty('App::PropertyLength',name,'Body controls');setattr(obj,name,value)
        obj.Proxy=self
    def execute(self,obj):
        d=json.loads(obj.DesignJSON);d['arm']['root_handle_mm']=obj.RootReach.Value;d['arm']['socket_handle_mm']=obj.SocketReach.Value
        obj.Shape=geometry(d,obj.Width.Value,obj.Thickness.Value)[0]
    def dumps(self):return None
    def loads(self,state):pass
