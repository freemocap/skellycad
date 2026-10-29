"""Remove the connector-launch return bend and rematch complete USB paths."""
import json,math,shutil
from pathlib import Path
import pcbnew as p
from route_r10_head import offset
from route_head_dovdd import v,xy

ROOT=Path(__file__).resolve().parents[2];out=ROOT/'generated/ov9281-r10-usb-09'
assert not out.exists();shutil.copytree(ROOT/'generated/ov9281-r10-usb-08',out)
b=p.LoadBoard(str(out/'controller.kicad_pcb'));held=[];new=[]
for t in b.GetTracks():
    if t.GetNetname().startswith('/USB_D'):held.append(t);b.Remove(t)
def pad(ref,num):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()==ref and q.GetNumber()==str(num))
def length(q):return sum(math.dist(a,z) for a,z in zip(q,q[1:]))
paths={}
for pol,ref,sign,pin in [('DP','R110',1,50),('DM','R109',-1,49)]:
    start=xy(pad('U101',pin).GetPosition());paths['/USB_'+pol+'_CHIP']=[start,(start[0],4.8)]+offset([(12.7,4.45),(12.7,2.9),(12.3,2.9)],sign*.125)+[xy(pad(ref,2).GetPosition())]
    yy=3.5375 if pol=='DP' else 2.4625;xx=7.635 if pol=='DP' else 7.385;end_y=4.875 if pol=='DP' else 4.625
    paths['/USB_'+pol]=[xy(pad(ref,1).GetPosition()),(10.1,yy),(8.4,yy),(xx,yy),(xx,end_y),(7.3,end_y),xy(pad('J101',3 if pol=='DP' else 2).GetPosition())]
delta=sum(length(q) for net,q in paths.items() if net.startswith('/USB_DM'))-sum(length(q) for net,q in paths.items() if net.startswith('/USB_DP'))
q=paths['/USB_DP_CHIP'];x=12.575-delta/2;paths['/USB_DP_CHIP']=q[:3]+[(12.575,4.4),(x,4.4),(x,4.15),(12.575,4.15)]+q[3:]
for net,points in paths.items():
    code=next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net)
    for aa,zz in zip(points,points[1:]):
        t=p.PCB_TRACK(b);t.SetNetCode(code);t.SetLayer(p.F_Cu);t.SetWidth(100000);t.SetStart(v(*aa));t.SetEnd(v(*zz));t.SetLocked(True);b.Add(t);new.append(t)
remove=set();collisions=[];newids={t.m_Uuid.AsString() for t in new}
for a in new:
    shape=a.GetEffectiveShape(p.F_Cu)
    for q in b.GetPads():
        if q.IsOnLayer(p.F_Cu) and q.GetNetname()!=a.GetNetname() and q.GetEffectiveShape(p.F_Cu).Collide(shape,100000):collisions.append([a.GetNetname(),q.GetParentFootprint().GetReference(),q.GetNumber()])
    for t in b.GetTracks():
        if t.m_Uuid.AsString() not in newids and t.GetNetname()!=a.GetNetname() and t.IsOnLayer(p.F_Cu) and t.GetEffectiveShape(p.F_Cu).Collide(shape,100000):
            assert not t.GetNetname().startswith('/CAM_L_');remove.add(t.m_Uuid.AsString())
for t in b.GetTracks():
    if t.m_Uuid.AsString() in remove:held.append(t);b.Remove(t)
assert not collisions,collisions
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'controller.kicad_pcb'),b)
(out/'usb-route-refinement.json').write_text(json.dumps({'paths':paths,'compensation_mm':delta,'compensation_x_mm':x,'removed':list(remove)},indent=2)+'\n');print('Removed ordinary conflicts',len(remove),'compensation',delta)
