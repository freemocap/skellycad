"""Deterministic parametric baseplate construction from embedded measured planes."""
import json
import FreeCAD as App
import Part

def plane_cell(planes,bounds):
    """Keep the inside of each outward-facing plane: n dot point <= offset."""
    x,y,z,dx,dy,dz=bounds
    shape=Part.makeBox(dx,dy,dz,App.Vector(x,y,z))
    for plane in planes:
        n=App.Vector(*plane['normal']);rotation=App.Rotation(App.Vector(0,0,1),n)
        tool=Part.makeBox(100,100,100)
        tool.Placement=App.Placement(n*plane['offset_mm']+rotation.multVec(App.Vector(-50,-50,0)),rotation)
        shape=shape.cut(tool)
    return shape.removeSplitter()

def cylinder(p,radius=None):
    return Part.makeCylinder(p['radius_mm'] if radius is None else radius,p['length_mm'],App.Vector(*p['origin_mm']),App.Vector(*p['axis']))

def construct(p,bore_radius,stock_depth):
    points=[App.Vector(*v) for v in p['outer_profile_mm']]
    for v in points:v.y=5-stock_depth
    base=Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(0,stock_depth,0))
    lug=plane_cell(p['lug_planes'],p['lug_bounds_mm'])
    shoulders=plane_cell(p['lug_cap_planes'],p['lug_bounds_mm'])
    lug=lug.fuse(shoulders).fuse(cylinder(p['lug_round'])).removeSplitter()
    outer=base.fuse(lug).removeSplitter()
    tools=[]
    for key,a,b in [('socket_planes_a',p['socket_floor_y_mm'],p['socket_transition_y_mm']),
                    ('socket_planes_b',p['socket_transition_y_mm'],p['socket_open_y_mm'])]:
        tools.append(plane_cell(p[key],[-5,a,-8,11.35370164442004,b-a,16]))
    tools.append(cylinder(p['socket_round']))
    pocket_tool=tools[0].multiFuse(tools[1:]).removeSplitter()
    pocketed=outer.cut(pocket_tool).removeSplitter()
    # Keep this operation order: the STEP contains sensitive near-coincident joins.
    shape=outer.cut(pocket_tool).cut(cylinder(p['bore'],bore_radius)).removeSplitter()
    shape=shape.cut(plane_cell(p['mouth_planes'],[-5,-5,-10,20,15,20])).removeSplitter()
    points=[App.Vector(*v) for v in p['groove_profile_mm']]
    groove=Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(0,3.5,0))
    shape=shape.cut(groove).removeSplitter()
    return {'Stock':base,'Outer body':outer,'Receiving pocket':pocketed,'Finished':shape}

class BaseplateModel:
    def __init__(self,obj,p):
        obj.addProperty('App::PropertyString','ConstructionJSON','Construction')
        obj.ConstructionJSON=json.dumps(p)
        obj.addProperty('App::PropertyLength','BoreRadius','Dimensions');obj.BoreRadius=p['bore']['radius_mm']
        obj.addProperty('App::PropertyLength','SkullStockDepth','Dimensions');obj.SkullStockDepth=p['body_depth_mm']
        obj.addProperty('App::PropertyEnumeration','DisplayStage','Inspection')
        obj.DisplayStage=['Stock','Outer body','Receiving pocket','Finished'];obj.DisplayStage='Finished'
        obj.Proxy=self

    def execute(self,obj):
        p=json.loads(obj.ConstructionJSON)
        stages=construct(p,obj.BoreRadius.Value,obj.SkullStockDepth.Value)
        shape=stages[str(obj.DisplayStage)]
        shape.check(True)
        assert len(shape.Solids)==1
        obj.Shape=shape

    def dumps(self):return None
    def loads(self,state):pass
