"""Extract native coating, solder-land and filled-via geometry for mass screening."""
import json,math,hashlib
import pcbnew as p
from export_r11_geometry import ROOT,OUT,SPEC
from routing_r11 import LAYERS,v
def main():
    b=p.LoadBoard(str(OUT/'camera.kicad_pcb'));coatings={};lands={}
    for mask,cu in [(p.F_Mask,p.F_Cu),(p.B_Mask,p.B_Cu)]:
        openings=p.SHAPE_POLY_SET();b.ConvertBrdLayerToPolygonalContours(mask,openings)
        exposed=p.SHAPE_POLY_SET();paste=p.SHAPE_POLY_SET();b.ConvertBrdLayerToPolygonalContours(p.F_Paste if cu==p.F_Cu else p.B_Paste,paste)
        for pad in b.GetPads():
            if pad.IsOnLayer(cu) and pad.IsOnLayer(mask):
                s=p.SHAPE_POLY_SET();pad.TransformShapeToPolygon(s,cu,0,p.FromMM(.002),p.ERROR_INSIDE);exposed.BooleanAdd(s)
        for region,x0,x1 in [('controller',0,28),('head',60.85,74.85)]:
            clip=p.SHAPE_POLY_SET();clip.NewOutline()
            for x,y in [(x0,0),(x1,0),(x1,14),(x0,14)]:clip.Append(v(x,y))
            a=p.SHAPE_POLY_SET(openings);a.BooleanIntersection(clip);e=p.SHAPE_POLY_SET(exposed);e.BooleanIntersection(clip);s=p.SHAPE_POLY_SET(paste);s.BooleanIntersection(clip)
            coatings[region+'/'+b.GetLayerName(cu)]={'mask_opening_area_mm2':a.Area()*1e-12,'exposed_pad_area_mm2':e.Area()*1e-12,'paste_aperture_area_mm2':s.Area()*1e-12}
    via_volume=0;count=0;via_regions={'controller':0.,'head':0.,'flex':0.}
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):
            a,z=sorted([LAYERS.index(t.TopLayer()),LAYERS.index(t.BottomLayer())]);assert z==a+1
            vol=math.pi*(p.ToMM(t.GetDrillValue())/2)**2*[.02,.02,.05,.02,.02][a];via_volume+=vol;count+=1
            x=p.ToMM(t.GetPosition().x);region='controller' if x<28 else 'head' if x>60.85 else 'flex';via_regions[region]+=vol
    r={'board_sha256':hashlib.sha256((OUT/'camera.kicad_pcb').read_bytes()).hexdigest(),'surfaces':coatings,'filled_laser_segments':count,'filled_via_volume_between_foils_mm3':via_volume,'scope':'Pad copper and paste/mask geometry, not solder-joint measurements. Filled via cylinders cover dielectric gaps only; land copper is already in layer areas. Coatings clipped to region rectangles; tiny tapered-edge differences retained as mass uncertainty.'}
    r['filled_via_volume_by_region_mm3']=via_regions
    (SPEC/'material-geometry.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
