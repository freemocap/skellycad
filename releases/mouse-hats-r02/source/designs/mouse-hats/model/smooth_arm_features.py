"""Two cubic bends, controlled rectangular sections, and collar-aligned ends."""
import json,math
import FreeCAD as App
import Part

def unit(v):
    v=App.Vector(*v) if not isinstance(v,App.Vector) else App.Vector(v)
    v.normalize();return v

def geometry(data,width,thickness):
    if width<=0 or thickness<=0:raise ValueError('Arm dimensions must be positive')
    n=unit(data['socket_axis']);radial=unit(data['arm']['radial_direction'])
    arm=data['arm'];root=App.Vector(*arm['root_mm']);bend=App.Vector(*arm['bend_mm'])
    end=App.Vector(*data['socket_center_mm'])+n*data['attachment_height_mm']+radial*data['attachment_radius_mm']
    t0=unit(arm['root_tangent']);tm=unit(arm['bend_tangent'])
    poles=[root,root+t0*arm['root_handle_mm'],bend-tm*arm['bend_handle_mm'],bend,
           bend+tm*arm['bend_handle_mm'],end+radial*arm['socket_handle_mm'],end]
    curve=Part.BSplineCurve()
    curve.buildFromPolesMultsKnots(poles,[4,3,4],[0.,1.,2.],False,3)
    centers=[curve.value(2*i/(data['sections']-1)) for i in range(data['sections'])]
    tangents=[curve.tangent(2*i/(data['sections']-1))[0] for i in range(data['sections'])]
    # Parallel transport avoids frame flips as a bend passes parallel to the socket axis.
    initial=tangents[0].cross(n)
    if initial.Length<1e-6:initial=tangents[0].cross(App.Vector(1,0,0))
    widths=[unit(initial)]
    for before,after in zip(tangents,tangents[1:]):
        widths.append(App.Rotation(before,after).multVec(widths[-1]))
    target=unit(tangents[-1].cross(n))
    angle=math.degrees(math.atan2(tangents[-1].dot(widths[-1].cross(target)),widths[-1].dot(target)))
    wires=[]
    for i,(center,tangent,w) in enumerate(zip(centers,tangents,widths)):
        fraction=i/(len(centers)-1)
        w=App.Rotation(tangent,angle*fraction*fraction*(3-2*fraction)).multVec(w)
        h=w.cross(tangent);h.normalize()
        pts=[center+w*(sx*width/2)+h*(sy*thickness/2) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        wires.append(Part.makePolygon(pts+[pts[0]]))
    solid=Part.makeLoft(wires,True,False)
    solid.check(True)
    if len(solid.Solids)!=1:raise ValueError('Arm must be one solid')
    return solid,curve.toShape()

class SmoothArm:
    def __init__(self,obj,data):
        obj.addProperty('App::PropertyString','DesignJSON','Construction');obj.DesignJSON=json.dumps(data)
        for name in ['Width','Thickness']:
            obj.addProperty('App::PropertyLength',name,'Arm dimensions');setattr(obj,name,data[name.lower()+'_mm'])
        for name,key in [('Root','root_mm'),('Bend','bend_mm')]:
            obj.addProperty('App::PropertyVector',name,'Arm path');setattr(obj,name,App.Vector(*data['arm'][key]))
        obj.addProperty('App::PropertyLength','AttachmentHeight','Socket attachment');obj.AttachmentHeight=data['attachment_height_mm']
        obj.Proxy=self
    def execute(self,obj):
        data=json.loads(obj.DesignJSON);data['arm']['root_mm']=list(obj.Root);data['arm']['bend_mm']=list(obj.Bend)
        data['attachment_height_mm']=obj.AttachmentHeight.Value
        obj.Shape=geometry(data,obj.Width.Value,obj.Thickness.Value)[0]
    def dumps(self):return None
    def loads(self,state):pass
