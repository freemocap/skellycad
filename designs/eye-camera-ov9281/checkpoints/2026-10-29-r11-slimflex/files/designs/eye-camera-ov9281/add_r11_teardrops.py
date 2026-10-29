"""Add clearance-checked copper tapers at accessible pad/via junctions.

SLIM.flex calls for teardrops [@wurthSlimRules2023]. Constrained launches are
listed explicitly for the manufacturing review instead of violating spacing.
"""
import json,math,shutil
from validate_r11_board import OUT,SPEC
from routing_r11 import *

def main():
    path=OUT/'camera.kicad_pcb';backup=OUT/'trials/before-teardrops.kicad_pcb';assert not backup.exists();shutil.copy2(path,backup)
    b=p.LoadBoard(str(path));lands=collections.defaultdict(list)
    for q in list(b.GetPads())+[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]:
        if not q.GetNetname():continue
        for l in LAYERS:
            if q.IsOnLayer(l):lands[q.GetNetname(),l,tuple(round(t,6) for t in xy(q.GetPosition()))].append(q.GetEffectiveShape(l))
    added=[];limited=[];seen=set();clearances={};planes={}
    for z in b.Zones():planes.setdefault((z.GetNetname(),z.GetLayer()),[]).append(z.GetFilledPolysList(z.GetLayer()))
    for t in list(b.GetTracks()):
        if isinstance(t,p.PCB_VIA):continue
        net=t.GetNetname();layer=t.GetLayer();width=p.ToMM(t.GetWidth())
        for a,end in [(xy(t.GetStart()),xy(t.GetEnd())),(xy(t.GetEnd()),xy(t.GetStart()))]:
            a=tuple(round(q,6) for q in a);key=(net,layer,a);shapes=lands.get(key)
            if not shapes or math.dist(a,end)<.15:continue
            delta=math.dist(a,end);dx,dy=(end[0]-a[0])/delta,(end[1]-a[1])/delta;unique=key+(round(dx,3),round(dy,3))
            if unique in seen:continue
            seen.add(unique);shape=max(shapes,key=lambda s:s.BBox().GetWidth()*s.BBox().GetHeight());bb=shape.BBox();radius=min(p.ToMM(bb.GetWidth()),p.ToMM(bb.GetHeight()))/2
            if width>=radius*1.5:continue
            edge=next((i*.01 for i in range(1,301) if not shape.Collide(v(a[0]+dx*i*.01,a[1]+dy*i*.01),0)),3.)
            if delta<edge+.08:continue
            success=False
            for extension,base_ratio in [(e,r) for r in [.8,.6,.5,.4] for e in [.2,.15,.1,.075]]:
                length=min(edge+extension,delta);anchor=edge*.45;base=radius*base_ratio
                points=[(a[0]+dx*anchor-dy*base,a[1]+dy*anchor+dx*base),(a[0]+dx*length-dy*width/2,a[1]+dy*length+dx*width/2),(a[0]+dx*length+dy*width/2,a[1]+dy*length-dx*width/2),(a[0]+dx*anchor+dy*base,a[1]+dy*anchor-dx*base)]
                if any(all(poly.Contains(v(*q)) for q in points) for poly in planes.get((net,layer),[])):success=True;break
                poly=p.SHAPE_POLY_SET();poly.NewOutline()
                for q in points:poly.Append(v(*q))
                if net not in clearances:clearances[net]=Clearance(b,net,width)
                clear=clearances[net];minx,miny,maxx,maxy=min(q[0] for q in points),min(q[1] for q in points),max(q[0] for q in points),max(q[1] for q in points)
                obstacles={id(s):s for i in range(math.floor(minx),math.floor(maxx)+1) for j in range(math.floor(miny),math.floor(maxy)+1) for s in clear.bins[layer,i,j]}
                if any(poly.Collide(s,76000) for s in obstacles.values()):continue
                z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(t.GetNetCode());z.SetLocalClearance(p.FromMM(.075));z.SetMinThickness(p.FromMM(.075));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetAssignedPriority(100)
                z.SetZoneName('R11 junction taper');z.Outline().Append(poly);b.Add(z);added.append({'net':net,'layer':b.GetLayerName(layer),'anchor_mm':a,'polygon_mm':points});success=True;break
            if not success:limited.append({'net':net,'layer':b.GetLayerName(layer),'xy_mm':a,'reason':'Additional taper would violate copper clearance; existing native pad/track junction retained for fabrication review.'})
    combined={}
    for z in list(b.Zones()):
        if z.GetZoneName()!='R11 junction taper':continue
        key=(z.GetNetname(),z.GetLayer())
        if key not in combined:combined[key]=z
        else:combined[key].Outline().BooleanAdd(z.Outline());b.Delete(z)
    for z in b.Zones():z.CacheBoundingBox();z.SetNeedRefill(True)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    report={'added':added,'clearance_constrained':limited,'manufacturing_approved':False};(SPEC/'teardrops.json').write_text(json.dumps(report,indent=2)+'\n');print('Added',len(added),'tapers; constrained',len(limited))
if __name__=='__main__':main()
