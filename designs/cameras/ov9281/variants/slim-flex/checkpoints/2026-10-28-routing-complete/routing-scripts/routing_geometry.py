"""Native copper geometry helpers for local routing trials, millimetres."""
import math
import pcbnew as p
from route_head_dovdd import v,xy

def legal_vias(b,pad):
    net=pad.GetNetname();items=list(b.GetPads())+list(b.GetTracks());layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
    obstacles=[i.GetEffectiveShape(layer) for layer in layers for i in items if i.GetNetname()!=net and i.IsOnLayer(layer)]
    vias=[xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
    pads=[q.GetEffectiveShape(layer) for q in b.GetPads() for layer in [p.F_Cu,p.B_Cu] if q.IsOnLayer(layer)]
    def clear(point):
        x,y=xy(point)
        if min(x,y)<.7 or max(x,y)>13.3:return False
        if any(math.dist((x,y),q)<.4-1e-8 for q in vias):return False
        shape=p.SHAPE_CIRCLE(point,200000)
        if any(s.Collide(shape,100000) for s in obstacles):return False
        return not any(s.Collide(shape,0) for s in pads)
    candidates={};sx,sy=xy(pad.GetPosition())
    points=[v(x*.2,y*.2) for x in range(4,66) for y in range(4,66)]
    points.extend(point for t in b.GetTracks() if t.GetNetname()==net for point in [t.GetStart(),t.GetEnd()])
    # A regular grid misses exact-width slots between opposing SMD pads.
    # Include footprint-centred candidates for those native geometry gaps.
    for fp in b.GetFootprints():
        if fp.GetLayer()!=p.B_Cu:continue
        cx,cy=xy(fp.GetPosition())
        points.extend(v(cx+dx,cy+dy) for dx in [-.5,-.25,0,.25,.5] for dy in [-.5,-.25,0,.25,.5])
    points.extend(v(sx+.32+x*.64,sy+.25+y*.5) for x in range(-12,13) for y in range(-12,13))
    for point in points:
        if clear(point):candidates[point.x,point.y]=point
    return list(candidates.values())

def add_via(b,point,code):
    t=p.PCB_VIA(b);t.SetPosition(point);t.SetWidth(400000);t.SetDrill(200000);t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNetCode(code);b.Add(t)
    return t

def add_path(b,points,layer,code):
    for aa,bb in zip(points,points[1:]):
        t=p.PCB_TRACK(b);t.SetStart(v(*aa));t.SetEnd(v(*bb));t.SetWidth(100000);t.SetLayer(layer);t.SetNetCode(code);b.Add(t)
