"""Transfer audited native geometry and package envelopes to FreeCAD."""
from pathlib import Path
import hashlib,json
import pcbnew as p
from routing_r11 import LAYERS,HX,xy,v,POLYGON
from place_r11 import courtyard
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'generated/ov9281-r11-electronics';SPEC=ROOT/'designs/eye-camera-ov9281/electronics/r11'
def points(line):return [xy(line.CPoint(i)) for i in range(line.PointCount())]
def main():
    source=OUT/'camera.kicad_pcb';sha=hashlib.sha256(source.read_bytes()).hexdigest();assert json.loads((SPEC/'board-validation.json').read_text())['board_sha256']==sha
    b=p.LoadBoard(str(source));parts=json.loads((SPEC/'components.json').read_text())['parts'];rows=[]
    for f in b.GetFootprints():
        ref=f.GetReference();fab=[q.GetBoundingBox() for q in f.GraphicalItems() if isinstance(q,p.PCB_SHAPE) and q.GetLayer() in [p.F_Fab,p.B_Fab]]
        if fab:
            bb=fab[0]
            for box in fab[1:]:bb.Merge(box)
            body=[p.ToMM(q) for q in [bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom()]]
        else:body=courtyard(f)
        rows.append({**parts[ref],'xy_mm':xy(f.GetPosition()),'rotation_deg':f.GetOrientationDegrees(),'side':'B' if f.IsFlipped() else 'F','body_bounds_mm':body,'courtyard_mm':courtyard(f),'body_evidence':'Native fabrication-outline bounding prism plus selected maximum package height; not manufacturer component CAD.'})
    copper={};areas={}
    for layer in LAYERS:
        allpoly=p.SHAPE_POLY_SET()
        for q in list(b.GetPads())+list(b.GetTracks()):
            if not q.IsOnLayer(layer):continue
            poly=p.SHAPE_POLY_SET();q.TransformShapeToPolygon(poly,layer,0,p.FromMM(.002),p.ERROR_INSIDE);allpoly.BooleanAdd(poly)
        for zone in b.Zones():
            if zone.IsOnLayer(layer):allpoly.BooleanAdd(zone.GetFilledPolysList(layer))
        areas[b.GetLayerName(layer)]=allpoly.Area()*1e-12
        for region,x0,x1 in [('controller',-.1,28),('flex',28,HX),('head',HX,HX+14.1)]:
            clip=p.SHAPE_POLY_SET();clip.NewOutline()
            for x,y in [(x0,-.1),(x1,-.1),(x1,14.1),(x0,14.1)]:clip.Append(v(x,y))
            poly=p.SHAPE_POLY_SET(allpoly);poly.BooleanIntersection(clip);rings=[]
            for i in range(poly.OutlineCount()):rings.append({'outer':points(poly.Outline(i)),'holes':[points(poly.Hole(i,j)) for j in range(poly.HoleCount(i))]})
            copper.setdefault(region,{})[b.GetLayerName(layer)]={'area_mm2':poly.Area()*1e-12,'polygons':rings}
        print(b.GetLayerName(layer),round(areas[b.GetLayerName(layer)],3),'mm2',flush=True)
    report={'units':'mm','board_sha256':sha,'outline_mm':POLYGON,'components':rows,'copper':copper,'copper_area_mm2':areas,'copper_polygon_max_error_mm':.002,'thickness_mm':{'component':.303,'flex':.166},'frame':'KiCad XY; FreeCAD maps (x,y,z) to (x,14-y,z).'}
    (OUT/'native-geometry.json').write_text(json.dumps(report,separators=(',',':'))+'\n',encoding='utf-8');print('Native geometry exported')
if __name__=='__main__':main()
