"""Conservative native copper union area, excluding plated drill openings."""
import math
import pcbnew as p

def retention(board,layer,board_area):
    copper=p.SHAPE_POLY_SET()
    for z in board.Zones():
        if z.IsOnLayer(layer):copper.BooleanAdd(z.GetFilledPolysList(layer))
    for item in list(board.GetTracks())+list(board.GetPads()):
        if item.IsOnLayer(layer):
            poly=p.SHAPE_POLY_SET();item.TransformShapeToPolygon(poly,layer,0,1000,p.ERROR_INSIDE);copper.BooleanAdd(poly)
    for t in board.GetTracks():
        if isinstance(t,p.PCB_VIA) and t.IsOnLayer(layer):
            hole=p.SHAPE_POLY_SET();hole.NewOutline();q=t.GetPosition();radius=t.GetDrill()/2
            # Circumscribed hole conservatively subtracts at least the drill area.
            radius/=math.cos(math.pi/64)
            for i in range(64):hole.Append(round(q.x+radius*math.cos(i*2*math.pi/64)),round(q.y+radius*math.sin(i*2*math.pi/64)))
            copper.BooleanSubtract(hole)
    copper.Simplify();area=copper.Area()/1e12
    return {'layer':board.GetLayerName(layer),'copper_union_area_mm2':area,'board_area_mm2':board_area,'retention_fraction':area/board_area,'method':'Native polygon union with 1um inward copper approximation; circumscribed 64-sided drill removal.'}
