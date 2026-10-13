"""Extract 58 baseplate construction planes and test the proposed decomposition."""
from pathlib import Path
import json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/baseplate'
s=Part.read(str(OUT/'source.brep'))
def plane(i,flip=False):
    f=s.Faces[i];n=f.normalAt(0,0)
    if flip:n=-n
    return dict(normal=list(n),offset_mm=n.dot(f.CenterOfMass))
def cell(planes,bounds):
    x,y,z,dx,dy,dz=bounds
    r=Part.makeBox(dx,dy,dz,App.Vector(x,y,z))
    for p in planes:
        n=App.Vector(*p['normal']);rot=App.Rotation(App.Vector(0,0,1),n)
        tool=Part.makeBox(100,100,100)
        tool.Placement=App.Placement(n*p['offset_mm']+rot.multVec(App.Vector(-50,-50,0)),rot)
        r=r.cut(tool)
    return r.removeSplitter()
def cylinder(i):
    f=s.Faces[i];surf=f.Surface
    v0,v1=f.ParameterRange[2:]
    return dict(origin_mm=list(surf.Center+surf.Axis*v0),axis=list(surf.Axis),radius_mm=surf.Radius,length_mm=v1-v0)
def cyl(p):return Part.makeCylinder(p['radius_mm'],p['length_mm'],App.Vector(*p['origin_mm']),App.Vector(*p['axis']))
p=dict(units='mm',source='58nassembly.step / Baseplate',
    outer_profile_mm=[list(v.Point) for v in s.Faces[0].OuterWire.OrderedVertexes],
    body_depth_mm=10, lug_planes=[plane(i) for i in [2,3,4,12,13,15,16]],
    lug_cap_planes=[plane(i) for i in [2,7,8,12,13,15,16]],
    mouth_planes=[plane(i,True) for i in [11,13]],
    lug_bounds_mm=[-10,-5,-10,20,15,20],lug_round=cylinder(14),bore=cylinder(1),
    socket_floor_y_mm=1.5,socket_transition_y_mm=4.00380530190825,socket_open_y_mm=5,
    socket_planes_a=[plane(i,True) for i in [6,10,13,20,21,25,26]],
    socket_planes_b=[plane(i,True) for i in [6,10,13,20,21,30,31]],
    socket_round=cylinder(33),groove_profile_mm=[list(v.Point) for v in s.Faces[9].OuterWire.OrderedVertexes][7:10])
base=Part.Face(s.Faces[0].OuterWire).extrude(App.Vector(0,10,0))
lug=cell(p['lug_planes'],p['lug_bounds_mm']).fuse(cell(p['lug_cap_planes'],p['lug_bounds_mm'])).fuse(cyl(p['lug_round'])).removeSplitter()
outer=base.fuse(lug).removeSplitter()
# The opening begins at y=1.5 and its lip draft changes at y=4.0038053.
tools=[]
for key,a,b in [('socket_planes_a',1.5,p['socket_transition_y_mm']),('socket_planes_b',p['socket_transition_y_mm'],5)]:
    tools.append(cell(p[key],[-5,a,-8,11.35370164442004,b-a,16]))
tools.append(cyl(p['socket_round']))
socket=tools[0].multiFuse(tools[1:]).removeSplitter()
r=outer.cut(socket).cut(cyl(p['bore'])).removeSplitter()
r=r.cut(cell(p['mouth_planes'],[-5,-5,-10,20,15,20])).removeSplitter()
points=[App.Vector(*v) for v in p['groove_profile_mm']]
groove=Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(0,3.5,0))
r=r.cut(groove).removeSplitter()
for name,shape in [('base',base),('lug',lug),('outer',outer),('socket',socket),('candidate',r)]:
    print(name,shape.Volume,len(shape.Faces),len(shape.Solids),shape.isValid(),flush=True)
    shape.check(True)
r.exportBrep(str(OUT/'candidate-study.brep'))
print('DIFF',s.cut(r,0.001).Volume,r.cut(s,0.001).Volume,flush=True)
(HERE/'parameters.json').write_text(json.dumps(p,indent=2)+'\n')
