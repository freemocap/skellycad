"""Free explicit sensor supply and connector escapes in the R10 head trial."""
import json,shutil,sys
from pathlib import Path
import pcbnew as p
from repair_r10_head import ALL,uid,v,xy
from routing_geometry import add_path,add_via

src=Path(sys.argv[1]);out=Path(sys.argv[2]);assert not out.exists();shutil.copytree(src,out)
b=p.LoadBoard(str(out/'head.kicad_pcb'));held=[];log=[]
for t in b.GetTracks():
    if t.GetNetname()!='/CAM_L_D1_P' or isinstance(t,p.PCB_VIA) or t.GetLayer()!=p.B_Cu:continue
    for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
        x,y=xy(getter())
        if x in [7.2,7.8] and y in [7.525,7.975]:setter(v({7.2:7.05,7.8:7.375}[x],y))
for t in list(b.GetTracks()):
    if t.GetNetname()=='GND' and not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.F_Cu:
        a,z=xy(t.GetStart()),xy(t.GetEnd())
        if min(a[1],z[1])>13 and min(a[0],z[0])>=5 and abs(a[1]-z[1])<1e-7:
            held.append(t);log.append({'removed':uid(t),'net':t.GetNetname(),'reason':'replace connector ground rail with local plane connections'});b.Remove(t)
for point,ref,num in [((7.725,7.507),'U1','G6'),((3.525,2.675),'C7','1')]:
    q=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()==ref and q.GetNumber()==num);shape=p.SHAPE_CIRCLE(v(*point),200000)
    for x in list(b.GetTracks()):
        if x.GetNetname()==q.GetNetname():continue
        if any(x.IsOnLayer(l) and x.GetEffectiveShape(l).Collide(shape,100000) for l in ALL):
            assert not x.IsLocked(),('Protected route blocks escape',point,x.GetNetname());held.append(x);b.Remove(x);log.append({'removed':uid(x),'net':x.GetNetname(),'reason':'supply escape via'})
    add_path(b,[xy(q.GetPosition()),point],q.GetParentFootprint().GetLayer(),q.GetNetCode());add_via(b,v(*point),q.GetNetCode());log.append({'added_via':point,'net':q.GetNetname()})
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'head.kicad_pcb'),b)
(out/'explicit-escapes.json').write_text(json.dumps(log,indent=2)+'\n');print(json.dumps(log,indent=2))
