"""Repair ordinary head nets around locked R10 pairs using native copper shapes.

Only In2/In3 and outer copper carry ordinary routes. In1/In4 remain ground.
Native DRC and an unchanged locked-copper signature are required afterwards.
"""
from pathlib import Path
import argparse,collections,json,math,subprocess,sys
import pcbnew as p
from route_head_dovdd import v,xy
from route_isolated_head_pads import route
from routing_geometry import add_via,add_path

LAYERS=[p.In2_Cu,p.In3_Cu,p.F_Cu,p.B_Cu]
ALL=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]

def uid(x):return x.m_Uuid.AsString()

def groups(b,net):
    b.BuildConnectivity();c=b.GetConnectivity();native={uid(x):x for x in list(b.GetPads())+list(b.GetTracks())};pads={uid(q):q for q in b.GetPads() if q.GetNetname()==net};pending=set(pads);result=[]
    while pending:
        q=pads[next(iter(pending))];items=[native.get(uid(x),x) for x in c.GetConnectedItems(q)]+[q];ids={uid(x) for x in items};pending-=ids
        result.append((q,items,ids))
    return sorted(result,key=lambda g:sum(isinstance(x,p.PAD) for x in g[1]))

def ends(items,layer):
    points={}
    for x in items:
        if not isinstance(x,(p.PAD,p.PCB_TRACK)) or not x.IsOnLayer(layer):continue
        for q in ([x.GetPosition()] if isinstance(x,(p.PAD,p.PCB_VIA)) else [x.GetStart(),x.GetEnd()]):points[q.x,q.y]=q
    return list(points.values())

def candidates(b,pad):
    bounds=b.GetBoardEdgesBoundingBox();left,top=p.ToMM(bounds.GetLeft())+.7,p.ToMM(bounds.GetTop())+.7;right,bottom=p.ToMM(bounds.GetRight())-.7,p.ToMM(bounds.GetBottom())-.7
    net=pad.GetNetname();bins=collections.defaultdict(list);pads=[];vias=[]
    for x in list(b.GetPads())+list(b.GetTracks()):
        if isinstance(x,p.PCB_VIA):vias.append(xy(x.GetPosition()))
        for layer in ALL:
            if not x.IsOnLayer(layer):continue
            shape=x.GetEffectiveShape(layer)
            if isinstance(x,p.PAD):pads.append(shape)
            if x.GetNetname()==net:continue
            bb=shape.BBox();a=xy(bb.GetOrigin());z=xy(bb.GetEnd())
            for i in range(math.floor(a[0]-.31),math.floor(z[0]+.31)+1):
                for j in range(math.floor(a[1]-.31),math.floor(z[1]+.31)+1):bins[i,j].append(shape)
    sx,sy=xy(pad.GetPosition());points=[]
    points.extend((sx+i*.2,sy+j*.2) for i in range(-12,13) for j in range(-12,13))
    points.extend((sx+.32+i*.64,sy+.25+j*.5) for i in range(-4,5) for j in range(-5,6))
    cx,cy=xy(pad.GetParentFootprint().GetPosition())
    points.extend((cx+dx,cy+dy) for dx in [-.5,-.25,0,.25,.5] for dy in [-.5,-.25,0,.25,.5])
    if pad.GetParentFootprint().GetReference()=='J201':
        points.extend((sx+dx,13.3) for dx in [0,-.05,.05,-.1,.1])
    for x,y in sorted(set(points),key=lambda q:math.dist(q,(sx,sy))):
        if not (left-1e-8<=x<=right+1e-8 and top-1e-8<=y<=bottom+1e-8):continue
        if any(math.dist((x,y),q)<.40001 for q in vias):continue
        point=v(x,y);shape=p.SHAPE_CIRCLE(point,200000)
        if any(s.Collide(shape,100000) for s in bins[math.floor(x),math.floor(y)]):continue
        # Keep drilled vias outside component pads, including pads of this net.
        if any(s.Collide(shape,100000) for s in pads):continue
        yield point

def locked(b):
    return sorted((uid(t),t.GetNetname(),tuple(xy(t.GetStart())),tuple(xy(t.GetEnd())),t.GetLayer()) for t in b.GetTracks() if t.IsLocked())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);ap.add_argument('--board',choices=['head','controller'],default='head');ap.add_argument('--max-nodes',type=int,default=60000);ap.add_argument('--sweeps',type=int,default=6);a=ap.parse_args();folder=a.directory.resolve();path=folder/(a.board+'.kicad_pcb');b=p.LoadBoard(str(path));before=locked(b);record=folder/(a.board+'-ordinary-net-repair.json');log=json.loads(record.read_text()) if record.exists() else []
    def save():
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());assert locked(b)==before
        p.SaveBoard(str(path),b);(folder/'ordinary-net-repair.json').write_text(json.dumps(log,indent=2)+'\n')
    ground=next(z for z in b.Zones() if z.GetNetname()=='GND' and z.GetLayer()==p.In1_Cu)
    for layer in [p.F_Cu,p.B_Cu]:
        if any(z.GetLayer()==layer for z in b.Zones()):continue
        z=p.Cast_to_ZONE(ground.Duplicate(False));z.SetLayer(layer);z.SetLocalClearance(p.FromMM(.35));b.Add(z)
    save()
    nets=sorted({q.GetNetname() for q in b.GetPads() if q.GetNetname() and not q.GetNetname().startswith('/CAM_L_')})
    for sweep in range(a.sweeps):
        progress=False
        for net in nets:
            for attempt in range(20):
                gs=groups(b,net)
                if len(gs)<2:break
                success=False
                for layer in LAYERS:
                    options=[]
                    for i,g in enumerate(gs):
                        targets=ends([x for j,h in enumerate(gs) if j!=i for x in h[1]],layer)
                        if not targets:continue
                        for start in ends(g[1],layer):options.append((min(math.dist(xy(start),xy(t)) for t in targets),g[0],start,targets))
                    for distance,pad,start,targets in sorted(options,key=lambda q:q[0])[:3]:
                        print('Search',net,b.GetLayerName(layer),'gap',round(distance,3),'mm',flush=True)
                        result=route(b,pad,layer,start,targets,max_nodes=a.max_nodes)
                        if result['result']=='routed':
                            log.append({'net':net,'operation':'join','layer':b.GetLayerName(layer),**result});save();success=progress=True
                            print(net,b.GetLayerName(layer),'joined; groups',len(groups(b,net)),flush=True);break
                    if success:break
                if not success:
                    for pad,items,ids in gs:
                        if any(isinstance(x,p.PCB_VIA) for x in items):continue
                        for q in sorted([x for x in items if isinstance(x,p.PAD)],key=lambda x:x.GetParentFootprint().GetReference()=='U1'):
                            layer=p.B_Cu if q.IsOnLayer(p.B_Cu) else p.F_Cu
                            for count,point in enumerate(candidates(b,q)):
                                if count>=18:break
                                result=route(b,q,layer,targets=[point],commit=False,max_nodes=min(15000,a.max_nodes))
                                if result['result']!='routed':continue
                                add_path(b,result['path_xy_mm'],layer,q.GetNetCode());add_via(b,point,q.GetNetCode())
                                log.append({'net':net,'operation':'add escape via','via_xy_mm':xy(point),'layer':b.GetLayerName(layer),**result});save();success=progress=True
                                print(net,'added escape via',xy(point),flush=True);break
                            if success:break
                        if success:break
                if not success:
                    print(net,'needs further local repair;',len(gs),'groups',flush=True);break
        remaining={n:len(groups(b,n)) for n in nets if len(groups(b,n))>1};print('Remaining',remaining,flush=True)
        if not remaining or not progress:break
    save();cli=Path(sys.executable).with_name('kicad-cli.exe');report=folder/'checks'/(a.board+'-drc.json')
    subprocess.run([str(cli),'pcb','drc','--format','json','--output',str(report),str(path)],check=True,capture_output=True)
    d=json.loads(report.read_text());print('Native DRC',collections.Counter(x['type'] for x in d['violations']),'unconnected',len(d['unconnected_items']),flush=True)

if __name__=='__main__':main()
