"""Open the last two supply escapes without changing the sensor or interface."""
from pathlib import Path
import json,shutil,sys
import pcbnew as p
from repair_r10_head import ALL,uid,xy,v
from route_isolated_head_pads import route
from routing_geometry import add_path,add_via

src,out=map(Path,sys.argv[1:]);assert not out.exists();shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'))
b=p.LoadBoard(str(out/'head.kicad_pcb'));held=[];changed=[];log=[]
for t in b.GetTracks():
    if t.GetNetname()=='/CAM_L_D1_P' and not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.B_Cu:
        for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
            x,y=xy(getter())
            if x==7.375 and y in [7.525,7.975]:setter(v(7.325,y))
    if t.GetNetname()=='/M1_VH':
        if isinstance(t,p.PCB_VIA) and xy(t.GetPosition())==(9.005,6.507):t.SetPosition(v(9.925,6.36));changed.append(t)
        elif not isinstance(t,p.PCB_VIA):
            for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
                if xy(getter())==(9.005,6.507):setter(v(9.925,6.36));changed.append(t)
f=next(f for f in b.GetFootprints() if f.GetReference()=='C20');log.append({'moved':'C20','old':xy(f.GetPosition()),'new':[2.2,10.1]});f.SetPosition(v(2.2,10.1))
q=next(q for q in f.Pads() if q.GetNetname()=='/M1_AVDD');before={uid(t) for t in b.GetTracks()}
add_via(b,v(1.,9.65),q.GetNetCode());add_path(b,[xy(q.GetPosition()),(2.68,9.6),(1.4,9.6),(1.,9.65)],p.B_Cu,q.GetNetCode());changed.extend(t for t in b.GetTracks() if uid(t) not in before)
blockers={};collisions=[]
for a in changed+list(f.Pads()):
    for l in ALL:
        if not a.IsOnLayer(l):continue
        shape=a.GetEffectiveShape(l)
        for t in list(b.GetPads())+list(b.GetTracks()):
            if t.GetNetname()==a.GetNetname() or not t.IsOnLayer(l) or not t.GetEffectiveShape(l).Collide(shape,100000):continue
            if isinstance(t,p.PAD) or isinstance(t,p.PCB_VIA) or t.GetNetname().startswith('/CAM_L_') or (t.GetNetname()=='GND' and t.IsLocked()):collisions.append([a.GetNetname(),t.GetNetname(),xy(t.GetPosition()),b.GetLayerName(l)])
            else:blockers[uid(t)]=t
assert not collisions,collisions
for t in blockers.values():held.append(t);b.Remove(t);log.append({'removed':uid(t),'net':t.GetNetname()})
for t in blockers.values():
    pad=next(q for q in b.GetPads() if q.GetNetname()==t.GetNetname())
    result=route(b,pad,t.GetLayer(),start=t.GetStart(),targets=[t.GetEnd()],max_nodes=150000)
    log.append({'local_repair':t.GetNetname(),**result});print(t.GetNetname(),result['result'],flush=True)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'head.kicad_pcb'),b)
(out/'supply-escape-refinement.json').write_text(json.dumps(log,indent=2)+'\n')
