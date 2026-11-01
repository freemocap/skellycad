"""Join isolated sensor pads to existing same-net F.Cu using native shape checks.

Geometric routing only. DRC, net correspondence and signal-integrity review remain separate.
"""
from pathlib import Path
import argparse, collections, hashlib, heapq, itertools, json, math, shutil
import pcbnew as p
from route_head_dovdd import v, xy

def route(b,pad,layer=None,start=None,targets=None,commit=True,max_nodes=60000,ignore_track_nets=()):
    assert not (commit and ignore_track_nets), 'A relaxed search is a rip-up proposal, never committed copper'
    net=pad.GetNetname();layer=p.F_Cu if layer is None else layer
    start=pad.GetPosition() if start is None else start;sx,sy=xy(start);step=.025
    b.BuildConnectivity();connected={t.m_Uuid.AsString() for t in b.GetConnectivity().GetConnectedItems(pad)}
    connected.add(pad.m_Uuid.AsString())
    if targets is None:
        targets=[]
        for item in list(b.GetPads())+list(b.GetTracks()):
            if item.GetNetname()!=net or not item.IsOnLayer(layer) or item.m_Uuid.AsString() in connected:continue
            if isinstance(item,p.PAD):targets.append(item.GetPosition())
            else:targets.extend([item.GetStart(),item.GetEnd()])
    targets=list({(q.x,q.y):q for q in targets}.values())
    if not targets:return {'result':'no existing destination on '+b.GetLayerName(layer)}
    bins=collections.defaultdict(list)
    for item in list(b.GetPads())+list(b.GetTracks()):
        if item.GetNetname()==net or not item.IsOnLayer(layer):continue
        if isinstance(item,p.PCB_TRACK) and not isinstance(item,p.PCB_VIA) and item.GetNetname() in ignore_track_nets:continue
        shape=item.GetEffectiveShape(layer);bb=shape.BBox();x0,y0=xy(bb.GetOrigin());x1,y1=xy(bb.GetEnd())
        for x in range(math.floor(x0-.16),math.floor(x1+.16)+1):
            for y in range(math.floor(y0-.16),math.floor(y1+.16)+1):bins[x,y].append(shape)
    def clear(a,z):
        ax,ay=xy(a);zx,zy=xy(z)
        if min(ax,zx,ay,zy)<.55 or max(ax,zx,ay,zy)>13.45:return False
        seg=p.SHAPE_SEGMENT(a,z,p.FromMM(.1));seen=set()
        for x in range(math.floor(min(ax,zx)),math.floor(max(ax,zx))+1):
            for y in range(math.floor(min(ay,zy)),math.floor(max(ay,zy))+1):
                for shape in bins[x,y]:
                    if id(shape) in seen:continue
                    seen.add(id(shape))
                    if shape.Collide(seg,p.FromMM(.1)):return False
        return True
    def point(n):return v(sx+n[0]*step,sy+n[1]*step)
    targetxy=[xy(q) for q in targets]
    def h(n):return min(math.hypot(sx+n[0]*step-x,sy+n[1]*step-y) for x,y in targetxy)
    origin=(0,0);cost={origin:0};parent={};counter=itertools.count();queue=[(h(origin),next(counter),origin)];seen=set();end=None;target=None
    while queue and len(seen)<max_nodes:
        _,_,node=heapq.heappop(queue)
        if node in seen:continue
        seen.add(node);pt=point(node)
        for goal in targets:
            if math.dist(xy(pt),xy(goal))<.35 and clear(pt,goal):end=node;target=goal;break
        if end is not None:break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            nxt=(node[0]+dx,node[1]+dy)
            if nxt in seen:continue
            c=cost[node]+step*math.hypot(dx,dy)
            if c>=cost.get(nxt,float('inf')) or not clear(pt,point(nxt)):continue
            cost[nxt]=c;parent[nxt]=node;heapq.heappush(queue,(c+h(nxt),next(counter),nxt))
    if end is None:return {'result':'no path found on 0.025 mm grid','visited':len(seen)}
    nodes=[end]
    while nodes[-1]!=origin:nodes.append(parent[nodes[-1]])
    points=[point(n) for n in reversed(nodes)]+[target];merged=[points[0]]
    for i in range(1,len(points)-1):
        aa,bb,cc=points[i-1],points[i],points[i+1]
        if (bb.x-aa.x)*(cc.y-bb.y)!=(bb.y-aa.y)*(cc.x-bb.x):merged.append(bb)
    merged.append(points[-1])
    # Remove grid stair-steps only when the complete replacement segment clears
    # the same native obstacle shapes at the unchanged 0.1 mm rule.
    simple=[merged[0]];index=0
    while index<len(merged)-1:
        last=next(j for j in range(len(merged)-1,index,-1) if clear(merged[index],merged[j]))
        simple.append(merged[last]);index=last
    merged=simple;added=[]
    for aa,bb in zip(merged,merged[1:]):
        assert clear(aa,bb)
        if commit:
            t=p.PCB_TRACK(b);t.SetStart(aa);t.SetEnd(bb);t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(pad.GetNetCode());b.Add(t);added.append(t.m_Uuid.AsString())
    return {'result':'routed','visited':len(seen),'path_xy_mm':[xy(q) for q in merged],'added_track_uuids':added}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    b=p.LoadBoard(str(src/'head.kicad_pcb'));report={}
    for n in ['B7','C5','E4','E8','F7','G4','G5']:
        pad=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()==n)
        report[n]={'net':pad.GetNetname(),**route(b,pad)};print(n,json.dumps(report[n]),flush=True)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'))
    if (out/'validation.json').exists():(out/'validation.json').rename(out/'previous-validation.json')
    p.SaveBoard(str(out/'head.kicad_pcb'),b)
    (out/'isolated-pad-routing.json').write_text(json.dumps({'parent_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(),'routes':report,'requires_native_drc':True},indent=2)+'\n')
if __name__=='__main__':main()
