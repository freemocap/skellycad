"""Make bounded ordinary-net corridors around protected R10 high-speed copper."""
from pathlib import Path
import json,math,shutil,sys
import pcbnew as p
from repair_r10_head import groups,ends,uid,xy,v,locked
from route_isolated_head_pads import route
from routing_geometry import add_path

src,out=map(Path,sys.argv[1:3]);assert not out.exists();shutil.copytree(src,out)
b=p.LoadBoard(str(out/'head.kicad_pcb'));before=locked(b);held=[];log=[]
jobs=[('/M1_DVDD',(7.725,7.507)),('/M1_VSYNC_1V8_M',(8.75,13.3))]
if '--auto' in sys.argv:
    jobs=[]
    for net in sorted({q.GetNetname() for q in b.GetPads() if q.GetNetname()}):
        gs=groups(b,net)
        if len(gs)<2:continue
        candidates=[(len(g[1]),xy(t.GetPosition())) for g in gs for t in g[1] if isinstance(t,p.PCB_VIA)]
        if candidates:jobs.append((net,min(candidates)[1]))
for net,point in jobs:
    gs=groups(b,net)
    if len(gs)==1:continue
    g=next(g for g in gs if any(isinstance(x,p.PCB_VIA) and xy(x.GetPosition())==point for x in g[1]))
    protected={t.GetNetname() for t in b.GetTracks() if t.IsLocked()}
    ignore={t.GetNetname() for t in b.GetTracks() if not t.IsLocked()}-protected-{net,'GND'}
    options=[]
    for layer in [p.In2_Cu,p.In3_Cu,p.F_Cu,p.B_Cu]:
        targets=ends([x for h in gs if h is not g for x in h[1]],layer)
        result=route(b,g[0],layer,start=v(*point),targets=targets,commit=False,max_nodes=150000,ignore_track_nets=ignore)
        if result['result']!='routed':continue
        shapes=[p.SHAPE_SEGMENT(v(*a),v(*z),100000) for a,z in zip(result['path_xy_mm'],result['path_xy_mm'][1:])]
        blockers=[t for t in b.GetTracks() if t.GetNetname()!=net and t.IsOnLayer(layer) and any(t.GetEffectiveShape(layer).Collide(s,100000) for s in shapes)]
        assert all(not t.IsLocked() and not isinstance(t,p.PCB_VIA) for t in blockers)
        options.append((len(blockers),sum(math.dist(a,z) for a,z in zip(result['path_xy_mm'],result['path_xy_mm'][1:])),layer,result,blockers))
    if not options:print(net,'no relaxed corridor',flush=True);continue
    count,length,layer,result,blockers=min(options,key=lambda x:x[:2]);record={'net':net,'layer':b.GetLayerName(layer),'route':result,'removed':[{'uuid':uid(t),'net':t.GetNetname()} for t in blockers]}
    for t in blockers:held.append(t);b.Remove(t)
    old={uid(t) for t in b.GetTracks()};add_path(b,result['path_xy_mm'],layer,g[0].GetNetCode())
    assert all(item in locked(b) for item in before)
    for t in b.GetTracks():
        if uid(t) not in old:t.SetLocked(True)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'head.kicad_pcb'),b);log.append(record)
    print(net,'corridor',b.GetLayerName(layer),'displaced',count,'segments',flush=True)
(out/'local-corridor-repair.json').write_text(json.dumps(log,indent=2)+'\n')
