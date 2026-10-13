"""Measure planar construction profiles from the pinned 58 carrier (millimetres)."""
from pathlib import Path
import json
import FreeCAD as App
import Part

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/main-carrier'
OUT.mkdir(parents=True,exist_ok=True)
source_file=ROOT/'designs/mouse-hats/old/58nassembly.step'
import hashlib
assert hashlib.sha256(source_file.read_bytes()).hexdigest()=='3286036e4cbd6b1c993e96079f24afc29d375bedddda2e24fd93b2d18c3c9260'
assembly=Part.read(str(source_file))
matches=[s for s in assembly.Solids if len(s.Faces)==89 and abs(s.Volume-936.0813969186243)<1e-5]
assert len(matches)==1,'Pinned carrier identity did not match'
source=matches[0]
cache=ROOT/'generated/mouse-hats/inspection/carrier-source.brep'
cache.parent.mkdir(parents=True,exist_ok=True);source.exportBrep(str(cache))

def plane(f):
    n=f.normalAt(0,0);return n,n.dot(f.CenterOfMass)

def intersect(a,b,c):
    n,d=a;m,e=b;k,f=c
    return (m.cross(k)*d+k.cross(n)*e+n.cross(m)*f)/n.dot(m.cross(k))

def loop(points):
    clean=[]
    for p in points:
        if not clean or p.distanceToPoint(clean[-1])>1e-7:clean.append(p)
    if clean[0].distanceToPoint(clean[-1])<1e-7:clean.pop()
    return clean

def loft(a,b):
    wires=[Part.makePolygon(loop(p)+[loop(p)[0]]) for p in [a,b]]
    return Part.makeLoft(wires,True,True)

features=[]
solids=[]
def add(name,a,b):
    shape=loft(a,b)
    assert shape.isValid(),name
    features.append(dict(name=name,profiles_mm=[[list(v) for v in loop(p)] for p in [a,b]]))
    solids.append(shape)
    return shape

def extrude_face(name,index,delta):
    pts=[v.Point for v in source.Faces[index].OuterWire.OrderedVertexes]
    return add(name,pts,[v+delta for v in pts])

# Tray backing outline. The two circular openings are cut as explicit holes later.
xback=source.Faces[14].CenterOfMass.x
xfront=source.Faces[13].CenterOfMass.x
rear=[v.Point for v in source.Faces[14].OuterWire.OrderedVertexes]
forward=[p+App.Vector(xfront-xback,0,0) for p in rear]
bottom_n,bottom_d=plane(source.Faces[52])
for p in forward:
    if p.z < -20:
        p.z=(bottom_d-bottom_n.x*p.x-bottom_n.y*p.y)/bottom_n.z
add('TrayBacking',rear,forward)

def box(name,x0,x1,y0,y1,z0,z1):
    p=[App.Vector(x0,y0,z0),App.Vector(x1,y0,z0),App.Vector(x1,y1,z0),App.Vector(x0,y1,z0)]
    return add(name,p,[v+App.Vector(0,0,z1-z0) for v in p])

box('LeftPCBRebate',xfront-1,xfront,7.565882,9.065882,-8.033704,9.266714)
box('RightPCBRebate',xfront-1,xfront,16.091885,17.591885,-8.033704,9.331296)
extrude_face('LowerPCBStop',71,App.Vector(0,0,-2))

# The old arm is intentionally excluded: user will replace it in a later phase.

# Top PCB retention lips have two extrusion levels.
for name,idx in [('LeftLip',55),('RightLip',31)]:
    extrude_face(name,idx,App.Vector(0,0,1))
for name,idx in [('LeftLipCap',54),('RightLipCap',15)]:
    extrude_face(name,idx,App.Vector(0,0,-1))
extrude_face('PCBLocatingRamp',49,App.Vector(0,0,16.7662968498584-10.1230333430244))

# Isolate the mating stem, including a short overlap with the tray backing.
mount=source.common(Part.makeBox(8,7.565883,10.2,App.Vector(-1,1.5,-5.1))).removeSplitter()
planes=[plane(f) for f in mount.Faces]
levels=[]
for y in sorted(v.Point.y for v in mount.Vertexes):
    if not levels or y-levels[-1]>1e-5:levels.append(y)
print('STEM LEVELS',levels,flush=True)
for number,(lo,hi) in enumerate(zip(levels,levels[1:])):
    if lo>5.999:break
    mid=(lo+hi)/2
    section=mount.section(Part.makePlane(30,30,App.Vector(-10,mid,-10),App.Vector(0,1,0)))
    for j,edges in enumerate(Part.sortEdges(section.Edges)):
        wire=Part.Wire(edges)
        assert wire.isClosed(),number
        pts=[v.Point for v in wire.OrderedVertexes]
        sides=[]
        for p,q in zip(pts,pts[1:]+pts[:1]):
            options=[pl for pl in planes if abs(pl[0].y)<1-1e-9 and abs(pl[0].dot(p)-pl[1])<1e-6 and abs(pl[0].dot(q)-pl[1])<1e-6]
            assert options,(number,p,q)
            sides.append(options[0])
        sides=[pl for i,pl in enumerate(sides) if abs(sides[i-1][0].cross(pl[0]).y)>1e-9]
        profiles=[[intersect(sides[i-1],sides[i],(App.Vector(0,1,0),y)) for i in range(len(sides))] for y in [lo,hi]]
        add(f'MountSection{number:02d}_{j}',*profiles)

core=Part.makeBox(8,9.06588286441312-6,8,App.Vector(-1,6,-4))
core_planes=[]
for i in [74,75,76,78,79,80,25,27]:
    n,d=plane(source.Faces[i])
    rotation=App.Rotation(App.Vector(0,0,1),n)
    origin=n*d+rotation.multVec(App.Vector(-50,-50,0))
    tool=Part.makeBox(100,100,100)
    tool.Placement=App.Placement(origin,rotation)
    core=core.cut(tool)
    core_planes.append(dict(normal=list(n),offset_mm=d))
core=core.cut(Part.makeBox(10,10,20,App.Vector(xfront-1,8.16835866236362,-10))).removeSplitter();core.check(True)
solids.append(core)

result=solids[0].multiFuse(solids[1:],0.001).removeSplitter()
holes=[Part.makeCylinder(2,5,App.Vector(2,11.9423591269588,z),App.Vector(1,0,0)) for z in [-12.9033786820894,12.0966213179106]]
result=result.cut(Part.makeCompound(holes),0.001).removeSplitter()
result.exportBrep(str(OUT/'prototype.brep'))
print('PROTOTYPE',result.isValid(),len(result.Solids),result.Volume,
      'missing (includes omitted arm)',source.cut(result,0.001).Volume,'extra',result.cut(source,0.001).Volume,flush=True)
(HERE/'profiles.json').write_text(json.dumps(dict(units='mm',features=features,core_planes=core_planes),indent=2)+'\n')
