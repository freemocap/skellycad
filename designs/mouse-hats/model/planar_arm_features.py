"""One planar cubic per arm with a constant rectangular pipe section: no loft twist."""
import json
import FreeCAD as App
import Part

def unit(v):
    v=App.Vector(*v) if not isinstance(v,App.Vector) else App.Vector(v)
    v.normalize();return v

def geometry(data,width,thickness):
    if width<=0 or thickness<=0:raise ValueError('Dimensions must be positive')
    a=data['arm'];root=App.Vector(*a['root_mm']);n=unit(data['socket_axis'])
    radial=unit(a['radial_direction'])
    end=App.Vector(*data['socket_center_mm'])+n*data['attachment_height_mm']+radial*data['attachment_radius_mm']
    normal=unit((end-root).cross(radial))
    tangent=unit(a['root_tangent']);tangent=unit(tangent-normal*tangent.dot(normal))
    poles=[root,root+tangent*a['root_handle_mm'],end+radial*a['socket_handle_mm'],end]
    curve=Part.BezierCurve();curve.setPoles(poles)
    # A planar spine with a fixed plane normal has zero torsion. No distributed roll.
    spine=Part.Wire(curve.toShape());across=normal;inside=unit(normal.cross(tangent))
    pts=[root+across*(sx*width/2)+inside*(sy*thickness/2)
         for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    profile=Part.makePolygon(pts+[pts[0]])
    solid=spine.makePipeShell([profile],True,False)
    solid.check(True)
    if len(solid.Solids)!=1:raise ValueError('Expected one arm solid')
    return solid,curve.toShape()

class SmoothArm:
    def __init__(self,obj,data):
        obj.addProperty('App::PropertyString','DesignJSON','Construction');obj.DesignJSON=json.dumps(data)
        for name,value in [('Width',data['width_mm']),('Thickness',data['thickness_mm']),
                           ('RootReach',data['arm']['root_handle_mm']),('SocketReach',data['arm']['socket_handle_mm'])]:
            obj.addProperty('App::PropertyLength',name,'Arm controls');setattr(obj,name,value)
        obj.addProperty('App::PropertyVector','Root','Arm controls');obj.Root=App.Vector(*data['arm']['root_mm'])
        obj.Proxy=self
    def execute(self,obj):
        d=json.loads(obj.DesignJSON);d['arm']['root_mm']=list(obj.Root)
        d['arm']['root_handle_mm']=obj.RootReach.Value;d['arm']['socket_handle_mm']=obj.SocketReach.Value
        obj.Shape=geometry(d,obj.Width.Value,obj.Thickness.Value)[0]
    def dumps(self):return None
    def loads(self,state):pass
