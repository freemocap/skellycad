"""Complete one isolated DOVDD branch with a checked escape and local B.Cu search.

Native DRC remains authoritative. Plane voids are regenerated; no In1 tracks are added.
"""
from pathlib import Path
import argparse, collections, hashlib, heapq, itertools, json, math, shutil
import pcbnew as p

def v(x,y):return p.VECTOR2I(round(x*1e6),round(y*1e6))
def xy(q):return (q.x/1e6,q.y/1e6)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    b=p.LoadBoard(str(src/'head.kicad_pcb'));net='/M1_DOVDD'
    start_pad=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()=='D3')
    target_pad=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='C13' and q.GetNumber()=='1')
    assert start_pad.GetNetname()==target_pad.GetNetname()==net
    start=v(6.445,5.507);target=target_pad.GetPosition()
    layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
    items=list(b.GetPads())+list(b.GetTracks())
    obstacles={layer:[i.GetEffectiveShape(layer) for i in items if i.GetNetname()!=net and i.IsOnLayer(layer)] for layer in layers}
    escape=p.SHAPE_SEGMENT(start_pad.GetPosition(),start,p.FromMM(.1));via=p.SHAPE_CIRCLE(start,p.FromMM(.2))
    assert not any(s.Collide(escape,p.FromMM(.1)) for s in obstacles[p.F_Cu]),'Escape blocked'
    assert not any(s.Collide(via,p.FromMM(.1)) for shapes in obstacles.values() for s in shapes),'Via blocked'
    assert not any(math.dist(xy(start),xy(t.GetPosition()))<.4 for t in b.GetTracks() if isinstance(t,p.PCB_VIA))
    # Hash spatial bins bound collision work while using native copper shapes.
    bins=collections.defaultdict(list)
    for shape in obstacles[p.B_Cu]:
        bb=shape.BBox();x0,y0=xy(bb.GetOrigin());x1,y1=xy(bb.GetEnd())
        for x in range(math.floor(x0-.16),math.floor(x1+.16)+1):
            for y in range(math.floor(y0-.16),math.floor(y1+.16)+1):bins[x,y].append(shape)
    def clear(a,b):
        ax,ay=xy(a);bx,by=xy(b)
        if min(ax,bx,ay,by)<.55 or max(ax,bx,ay,by)>13.45:return False
        shape=p.SHAPE_SEGMENT(a,b,p.FromMM(.1));seen=set()
        for x in range(math.floor(min(ax,bx)),math.floor(max(ax,bx))+1):
            for y in range(math.floor(min(ay,by)),math.floor(max(ay,by))+1):
                for obstacle in bins[x,y]:
                    identity=id(obstacle)
                    if identity in seen:continue
                    seen.add(identity)
                    if obstacle.Collide(shape,p.FromMM(.1)):return False
        return True
    step=.025;sx,sy=xy(start);tx,ty=xy(target)
    def point(node):return v(sx+node[0]*step,sy+node[1]*step)
    def h(node):return math.hypot(sx+node[0]*step-tx,sy+node[1]*step-ty)
    origin=(0,0);cost={origin:0};parent={};counter=itertools.count();queue=[(h(origin),next(counter),origin)]
    visited=set();end=None
    while queue and len(visited)<150000:
        _,_,node=heapq.heappop(queue)
        if node in visited:continue
        visited.add(node);a_point=point(node)
        if h(node)<.3 and clear(a_point,target):end=node;break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            nxt=(node[0]+dx,node[1]+dy)
            if nxt in visited:continue
            newcost=cost[node]+step*math.hypot(dx,dy)
            if newcost>=cost.get(nxt,float('inf')):continue
            if not clear(a_point,point(nxt)):continue
            cost[nxt]=newcost;parent[nxt]=node
            heapq.heappush(queue,(newcost+h(nxt),next(counter),nxt))
    assert end is not None,('No route found',len(visited))
    nodes=[end]
    while nodes[-1]!=origin:nodes.append(parent[nodes[-1]])
    points=[point(n) for n in reversed(nodes)]+[target]
    # Merge only exactly collinear consecutive grid segments.
    merged=[points[0]]
    for i in range(1,len(points)-1):
        aa,bb,cc=points[i-1],points[i],points[i+1]
        if (bb.x-aa.x)*(cc.y-bb.y)!=(bb.y-aa.y)*(cc.x-bb.x):merged.append(bb)
    merged.append(points[-1])
    for aa,bb in zip(merged,merged[1:]):assert clear(aa,bb)
    added=[]
    def track(aa,bb,layer):
        t=p.PCB_TRACK(b);t.SetStart(aa);t.SetEnd(bb);t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(start_pad.GetNetCode());b.Add(t);added.append(t.m_Uuid.AsString())
    track(start_pad.GetPosition(),start,p.F_Cu)
    for aa,bb in zip(merged,merged[1:]):track(aa,bb,p.B_Cu)
    t=p.PCB_VIA(b);t.SetPosition(start);t.SetWidth(p.FromMM(.4));t.SetDrill(p.FromMM(.2));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNetCode(start_pad.GetNetCode());b.Add(t)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'))
    if (out/'validation.json').exists():(out/'validation.json').rename(out/'previous-validation.json')
    p.SaveBoard(str(out/'head.kicad_pcb'),b)
    record={'parent_board_sha256':sha(src/'head.kicad_pcb'),'net':net,'from':'U1.D3','to':'C13.1','track_width_mm':.1,'clearance_mm':.1,'via_mm':[.4,.2],
            'grid_step_mm':step,'visited_nodes':len(visited),'path_xy_mm':[xy(q) for q in merged],'added_tracks':added,'added_via':t.m_Uuid.AsString(),
            'native_drc_required':True,'impedance_qualified':False}
    (out/'dovdd-route.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':main()
