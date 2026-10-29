"""Add clock guards and free the final head connector escapes in a new trial."""
from pathlib import Path
import json,math,shutil,sys
import pcbnew as p
from route_r10_head import offset
from repair_r10_head import ALL,uid,v,xy
from routing_geometry import add_via

src,out=map(Path,sys.argv[1:]);assert not out.exists();shutil.copytree(src,out);b=p.LoadBoard(str(out/'head.kicad_pcb'));held=[];new=[];changes=[]
def pad(ref,number):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()==ref and q.GetNumber()==number)
def path(net,points,layer=p.F_Cu):
    code=next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net)
    for a,z in zip(points,points[1:]):
        if math.dist(a,z)<1e-8:continue
        t=p.PCB_TRACK(b);t.SetNetCode(code);t.SetLayer(layer);t.SetWidth(100000);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetLocked(True);b.Add(t);new.append(t)
def via(net,point):
    t=add_via(b,v(*point),next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net));t.SetLocked(True);new.append(t)

# Give the two clock guards clearance at the neighboring lane bends.
for stem,points,threshold,pins in [('D0',[(6,8.6),(6,8.9),(2,10.15),(2,11.2)],8.59999,{'P':'3','N':'2'}),('D1',[(8.6,8.9),(8.6,9.9),(5,11.06),(5,11.3)],8.89999,{'P':'9','N':'8'})]:
    for t in list(b.GetTracks()):
        if t.GetNetname().startswith('/CAM_L_'+stem) and not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.F_Cu and min(t.GetStart().y,t.GetEnd().y)>=p.FromMM(threshold):held.append(t);b.Remove(t)
    for polarity,sign in [('P',1),('N',-1)]:
        q=offset(points,.225*sign)
        if stem=='D1':q=[(8.6+.25*sign,8.9)]+q
        path('/CAM_L_'+stem+'_'+polarity,q+[xy(pad('J201',pins[polarity]).GetPosition())])

f=next(f for f in b.GetFootprints() if f.GetReference()=='R9');changes.append({'move':'R9','old':xy(f.GetPosition()),'new':[12.3,12.4]});f.SetPosition(v(12.3,12.4))
for t in b.GetTracks():
    if t.GetNetname()!='/M1_CAM_SCL_1V8':continue
    if isinstance(t,p.PCB_VIA) and xy(t.GetPosition())==(6.5,13.3):t.SetPosition(v(6.75,13.3));t.SetLocked(True);new.append(t)
    elif not isinstance(t,p.PCB_VIA) and any(xy(q)==(6.5,13.3) for q in [t.GetStart(),t.GetEnd()]):
        other=xy(t.GetEnd()) if xy(t.GetStart())==(6.5,13.3) else xy(t.GetStart());layer=t.GetLayer();held.append(t);b.Remove(t)
        path('/M1_CAM_SCL_1V8',[other]+([(6.75,13.0)] if layer!=p.F_Cu else [])+[(6.75,13.3)],layer)

target=sum(t.GetLength()/1e6 for t in b.GetTracks() if t.GetNetname()=='/CAM_L_CLK_P')
for t in list(b.GetTracks()):
    if t.GetNetname()=='/CAM_L_CLK_N' and min(t.GetStart().y,t.GetEnd().y)>=p.FromMM(8.59999):held.append(t);b.Remove(t)
stem=[(7.3,8.6),(7.3,9.4),(3.5,10.6),(3.5,11.2)];q=offset(stem,-.225);tail=xy(pad('J201','5').GetPosition())
remaining=sum(t.GetLength()/1e6 for t in b.GetTracks() if t.GetNetname()=='/CAM_L_CLK_N');base=sum(math.dist(a,z) for a,z in zip(q+[tail],(q+[tail])[1:]));extra=target-remaining-base
bulge=math.sqrt(((extra+.4)/2)**2-.2**2);x,y=q[2];q=q[:3]+[(x-bulge,y+.2),(x-bulge,y+.4),(x,y+.6)]+q[3:];path('/CAM_L_CLK_N',q+[tail])
negative=offset(q,-.201);negative[0]=(negative[0][0],8.7);positive=offset(stem,.426)
path('GND',negative+[(2.75,11.3),(2.75,12.25)]);path('GND',positive+[(4.25,11.3),(4.25,12.25)])
via('GND',(6.65,8.8));path('GND',[(6.65,8.8),(6.874,8.8)]);path('GND',[(7.726,9.3),(7.95,9.3)])
via('GND',(4.25,13.3));path('GND',[(4.25,13.1517),(4.25,13.3)])
for number,point in [('11',(6.25,13.3)),('16',(8.75,13.3))]:
    q=pad('J201',number);via(q.GetNetname(),point);path(q.GetNetname(),[xy(q.GetPosition()),point])

blockers={};collisions=[];newids={uid(x) for x in new};moved=list(f.Pads())
for a in new+moved:
    for layer in ALL:
        if not a.IsOnLayer(layer):continue
        shape=a.GetEffectiveShape(layer)
        for x in list(b.GetPads())+list(b.GetTracks()):
            if x.GetNetname()==a.GetNetname() or not x.IsOnLayer(layer) or not x.GetEffectiveShape(layer).Collide(shape,100000):continue
            if isinstance(x,p.PAD) or x.IsLocked() or uid(x) in newids:collisions.append([a.GetNetname(),xy(a.GetPosition()),x.GetNetname(),xy(x.GetPosition()),b.GetLayerName(layer)])
            else:blockers[uid(x)]=x
for key,t in blockers.items():held.append(t);b.Remove(t);changes.append({'removed':key,'net':t.GetNetname()})
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'head.kicad_pcb'),b)
(out/'clock-guard-refinement.json').write_text(json.dumps({'changes':changes,'clock_guard_width_mm':.1,'clock_guard_gap_mm':.101,'local_tuning_extra_mm':extra,'collisions':collisions},indent=2)+'\n');print(json.dumps({'removed':len(blockers),'collisions':collisions},indent=2))
