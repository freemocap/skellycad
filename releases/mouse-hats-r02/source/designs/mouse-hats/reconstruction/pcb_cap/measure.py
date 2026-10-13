"""Recover named extrusion profiles from the pinned cap; units are millimetres."""
from pathlib import Path
import json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/pcb-cap'
s=Part.read(str(OUT/'source.brep'))
items=[];solids=[]
def extrude(name,index,delta):
    points=[v.Point for v in s.Faces[index].OuterWire.OrderedVertexes]
    shape=Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(*delta))
    shape.check(True);solids.append(shape)
    items.append(dict(name=name,source_face_zero_based=index,profile_mm=[list(p) for p in points],extrusion_mm=delta))
extrude('UpperCover',27,[-1,0,0])
extrude('LowerCover',28,[-1,0,0])
extrude('CoverStep',26,[0,0,1])
extrude('SideWall',6,[0,-1,0])
extrude('LongRetainingLip',37,[0,0,-14.065])
extrude('UpperRetainingClip',11,[0,0,7.75941086843613-3.89521200852887])
extrude('LowerRetainingClip',12,[0,0,-7.73370315014155+3.89521189422187])
extrude('BottomFlange',1,[0,2.8,0])
extrude('UpperLocatingTab',49,[0,0,-1.5])
extrude('LowerLocatingTab',56,[0,0,2])
holes=[];tools=[]
for i in [33,64,65,66]:
    f=s.Faces[i];c=f.Surface;lo,hi=f.ParameterRange[2:]
    origin=c.Center+c.Axis*lo
    holes.append(dict(name='SideHole' if i==33 else f'Vent{i-63}',radius_mm=c.Radius,origin_mm=list(origin),axis=list(c.Axis),length_mm=hi-lo))
    tools.append(Part.makeCylinder(c.Radius,hi-lo,origin,c.Axis))
r=solids[0].multiFuse(solids[1:]).removeSplitter().cut(Part.makeCompound(tools)).removeSplitter()
r.check(True)
assert len(r.Solids)==1
missing=s.cut(r);excess=r.cut(s)
print('RESULT',r.Volume,len(r.Faces),'missing',missing.Volume,'excess',excess.Volume,flush=True)
r.exportBrep(str(OUT/'candidate-study.brep'))
(HERE/'parameters.json').write_text(json.dumps(dict(units='mm',source='58nassembly.step / RightCap',features=items,holes=holes),indent=2)+'\n')
