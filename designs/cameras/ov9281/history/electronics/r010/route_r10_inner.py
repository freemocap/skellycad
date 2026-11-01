"""Join ordinary-net islands across the two R10 signal layers without rip-up."""
from pathlib import Path
import collections,heapq,itertools,json,math,sys
import pcbnew as p
from routing_spatial import NearestPoints
from functools import lru_cache
from repair_r10_head import groups,ends,uid,v,xy,locked,ALL
from routing_geometry import add_path,add_via

def join(b,net,max_nodes=1100000):
    bounds=b.GetBoardEdgesBoundingBox();left,top=p.ToMM(bounds.GetLeft()),p.ToMM(bounds.GetTop());right,bottom=p.ToMM(bounds.GetRight()),p.ToMM(bounds.GetBottom())
    gs=groups(b,net)
    if len(gs)<2:return None
    g=min(gs,key=lambda q:len(q[1]));start=g[0];sx=sy=0.;layers=[p.In2_Cu,p.In3_Cu,p.F_Cu,p.B_Cu];step=.025
    targets={l:ends([x for h in gs if h is not g for x in h[1]],l) for l in layers};targetxy={l:[xy(q) for q in targets[l]] for l in layers}
    if not any(targets.values()):return {'result':'needs destination escape'}
    target_cells=collections.defaultdict(list)
    for l,rows in targets.items():
        for q in rows:
            x,y=xy(q);target_cells[l,math.floor(x/.5),math.floor(y/.5)].append(q)
    bins=collections.defaultdict(list);pads=[];vias=[]
    for x in list(b.GetPads())+list(b.GetTracks()):
        if isinstance(x,p.PCB_VIA):vias.append((xy(x.GetPosition()),x.GetNetname()))
        for l in ALL:
            if not x.IsOnLayer(l):continue
            shape=x.GetEffectiveShape(l)
            if isinstance(x,p.PAD):pads.append(shape)
            if x.GetNetname()==net:continue
            bb=shape.BBox();aa,zz=xy(bb.GetOrigin()),xy(bb.GetEnd())
            for i in range(math.floor(aa[0]-.31),math.floor(zz[0]+.31)+1):
                for j in range(math.floor(aa[1]-.31),math.floor(zz[1]+.31)+1):bins[l,i,j].append(shape)
    def point(n):return v(sx+n[0]*step,sy+n[1]*step)
    def clear(aa,zz,layer):
        a,z=xy(aa),xy(zz)
        if min(a[0],z[0])<left+.55 or max(a[0],z[0])>right-.55 or min(a[1],z[1])<top+.55 or max(a[1],z[1])>bottom-.55:return False
        shape=p.SHAPE_SEGMENT(aa,zz,100000);seen=set()
        for i in range(math.floor(min(a[0],z[0])),math.floor(max(a[0],z[0]))+1):
            for j in range(math.floor(min(a[1],z[1])),math.floor(max(a[1],z[1]))+1):
                for s in bins[layer,i,j]:
                    if id(s) in seen:continue
                    seen.add(id(s))
                    if s.Collide(shape,100000):return False
        return True
    high_speed=[t.GetEffectiveShape(l) for t in b.GetTracks() if t.GetNetname().startswith("/CAM_L_") for l in [p.F_Cu,p.B_Cu] if t.IsOnLayer(l)]
    usb=[t.GetEffectiveShape(p.F_Cu) for t in b.GetTracks() if t.GetNetname().startswith('/USB_D') and t.IsOnLayer(p.F_Cu)]
    via_cache={}
    def via_ok(n):
        key=n[:2]
        if key in via_cache:return via_cache[key]
        pt=point(n);x,y=xy(pt);okay=left+.7<=x<=right-.7 and top+.7<=y<=bottom-.7
        if okay:
            for loc,othernet in vias:
                distance=math.dist((x,y),loc)
                if distance<1e-7 and othernet==net:via_cache[key]=True;return True
                if distance<.4-1e-8:okay=False;break
        if okay:
            shape=p.SHAPE_CIRCLE(pt,200000)
            okay=not any(s.Collide(shape,100000) for l in ALL for s in bins[l,math.floor(x),math.floor(y)]) and not any(s.Collide(shape,100000) for s in pads) and (net=='GND' or (not any(s.Collide(shape,200000) for s in high_speed) and not any(s.Collide(shape,350000) for s in usb)))
        via_cache[key]=okay;return okay
    alltargets=[q for rows in targetxy.values() for q in rows]
    nearest=NearestPoints(alltargets)
    @lru_cache(maxsize=None)
    def h(n):return nearest.distance(sx+n[0]*step,sy+n[1]*step)
    cost={};roots={}
    # Every existing connected endpoint is a start. This preserves access through
    # narrow off-grid fanouts instead of asking a grid search to rediscover them.
    for l in layers:
        for origin in ends(g[1],l):
            x,y=xy(origin);ix,iy=round(x/step),round(y/step)
            for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
                n=(ix+dx,iy+dy,l);distance=math.dist(xy(origin),xy(point(n)))
                if distance<cost.get(n,float('inf')) and clear(origin,point(n),l):cost[n]=distance;roots[n]=origin
    parent={};counter=itertools.count();queue=[(c+h(n),next(counter),n) for n,c in cost.items()];heapq.heapify(queue);seen=set();finish=None;goal=None
    while queue and len(seen)<max_nodes:
        _,_,node=heapq.heappop(queue)
        if node in seen:continue
        seen.add(node);pt=point(node);layer=node[2]
        px,py=xy(pt);cx,cy=math.floor(px/.5),math.floor(py/.5)
        for target in (q for i in [-1,0,1] for j in [-1,0,1] for q in target_cells[layer,cx+i,cy+j]):
            if math.dist((px,py),xy(target))<.35 and clear(pt,target,layer):finish=node;goal=target;break
        if finish is not None:break
        choices=[]
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            nxt=(node[0]+dx,node[1]+dy,layer)
            if nxt in seen:continue
            c=cost[node]+step*math.hypot(dx,dy)
            if c<cost.get(nxt,float('inf')) and clear(pt,point(nxt),layer):choices.append((nxt,c))
        for nextlayer in layers:
            if nextlayer==layer:continue
            other=(node[0],node[1],nextlayer);c=cost[node]+1.5
            if other not in seen and c<cost.get(other,float('inf')) and via_ok(node):choices.append((other,c))
        for nxt,c in choices:cost[nxt]=c;parent[nxt]=node;heapq.heappush(queue,(c+h(nxt),next(counter),nxt))
    if finish is None:return {'result':'no multilayer path','visited':len(seen)}
    nodes=[finish]
    while nodes[-1] in parent:nodes.append(parent[nodes[-1]])
    nodes.reverse();runs=[];current=[roots[nodes[0]],point(nodes[0])];layer=nodes[0][2];added=[]
    for n in nodes[1:]:
        if n[2]!=layer:
            runs.append((layer,current));pt=point(n);current=[pt];layer=n[2]
            if not any(othernet==net and math.dist(xy(pt),loc)<1e-7 for loc,othernet in vias):add_via(b,pt,start.GetNetCode());added.append(xy(pt))
        else:current.append(point(n))
    current.append(goal);runs.append((layer,current));saved=[]
    for layer,points in runs:
        simple=[points[0]];i=0
        while i<len(points)-1:
            j=next(j for j in range(len(points)-1,i,-1) if clear(points[i],points[j],layer));simple.append(points[j]);i=j
        add_path(b,[xy(q) for q in simple],layer,start.GetNetCode());saved.append({'layer':b.GetLayerName(layer),'points':[xy(q) for q in simple]})
    return {'result':'routed','visited':len(seen),'added_vias':added,'paths':saved}

def main():
    folder=Path(sys.argv[1]);board=sys.argv[2] if len(sys.argv)>2 else 'head';assert board in ['head','controller'];path=folder/(board+'.kicad_pcb');b=p.LoadBoard(str(path));before=locked(b);log=[]
    for net in sorted({q.GetNetname() for q in b.GetPads() if q.GetNetname()}):
        for i in range(15):
            print("Multilayer search",net,flush=True)
            result=join(b,net,max_nodes=int(sys.argv[3]) if len(sys.argv)>3 else (250000 if board=="controller" else 1100000))
            if result is None:break
            print(net,json.dumps(result),flush=True);log.append({'net':net,**result})
            if result['result']!='routed':break
            b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());assert locked(b)==before;p.SaveBoard(str(path),b)
            (folder/(board+'-inner-layer-repair.json')).write_text(json.dumps(log,indent=2)+'\n')

if __name__=="__main__":main()
