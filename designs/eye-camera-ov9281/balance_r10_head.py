"""Connect useful inner-layer ground islands with legal through-ground vias."""
import collections,json,math,shutil,sys
from pathlib import Path
import pcbnew as p
from copper_retention import retention
from routing_geometry import add_via
from route_head_dovdd import v,xy

ROOT=Path(__file__).resolve().parents[2];out=ROOT/'generated/ov9281-r10-balanced-03';assert not out.exists();shutil.copytree(ROOT/'generated/ov9281-r10-balanced-01',out)
b=p.LoadBoard(str(out/'head.kicad_pcb'));layers=[p.In2_Cu,p.In3_Cu];zones=[next(z for z in b.Zones() if z.GetLayer()==l) for l in layers];alllayers=[p.F_Cu,p.B_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu]
bins=collections.defaultdict(list)
for t in list(b.GetTracks())+list(b.GetPads()):
    if t.GetNetname()=='GND' and not isinstance(t,p.PAD):continue
    for l in alllayers:
        if not t.IsOnLayer(l):continue
        s=t.GetEffectiveShape(l);bb=s.BBox();aa,zz=xy(bb.GetOrigin()),xy(bb.GetEnd())
        for x in range(math.floor(aa[0]-.31),math.floor(zz[0]+.31)+1):
            for y in range(math.floor(aa[1]-.31),math.floor(zz[1]+.31)+1):bins[x,y].append(s)
code=next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()=='GND');added=[]
for iteration in range(20):
    actual=[p.SHAPE_POLY_SET(z.GetFilledPolysList(l)) for z,l in zip(zones,layers)]
    rates=[retention(b,l,196) for l in layers];print('Retention',[(r['layer'],r['retention_fraction']) for r in rates],flush=True)
    if min(r['retention_fraction'] for r in rates)>.6005:break
    for z in zones:z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_NEVER)
    p.ZONE_FILLER(b).Fill(b.Zones());potential=[p.SHAPE_POLY_SET(z.GetFilledPolysList(l)) for z,l in zip(zones,layers)];candidates=[]
    viaxy=[xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
    step=.1 if iteration<4 else .025
    for ix in range(math.ceil(.7/step),math.floor(13.3/step)+1):
        for iy in range(math.ceil(.7/step),math.floor(13.3/step)+1):
            point=v(ix*step,iy*step)
            gain=sum(abs(poly.COutline(j).Area())/1e12 for old,poly in zip(actual,potential) if not old.Contains(point) for j in range(poly.OutlineCount()) if poly.Contains(point,j))
            if gain<.1:continue
            loc=(ix*step,iy*step)
            if any(math.dist(loc,q)<.40001 for q in viaxy):continue
            shape=p.SHAPE_CIRCLE(point,200000)
            if any(s.Collide(shape,100001) for s in bins[math.floor(loc[0]),math.floor(loc[1])]):continue
            candidates.append((gain,-math.dist(loc,(7,7)),loc))
    assert candidates,'No legal ground stitch reaches remaining useful islands'
    gain,_,loc=max(candidates);t=add_via(b,v(*loc),code);t.SetLocked(True);added.append({'xy_mm':loc,'potential_connected_area_mm2':gain});print('Add ground stitch',loc,flush=True)
    for z in zones:z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    p.SaveBoard(str(out/'head.kicad_pcb'),b)
else:raise RuntimeError('Copper retention did not converge')
p.SaveBoard(str(out/'head.kicad_pcb'),b);(out/'copper-balance.json').write_text(json.dumps({'ground_stitches':added,'after':rates,'scope':'Conservative copper union exceeds 60 percent on each corrected inner layer; supplier compression remains to be confirmed.'},indent=2)+'\n')
