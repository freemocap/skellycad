"""Create an isolated controller pair-routing trial and report native conflicts."""
import argparse,json,math,shutil,subprocess,sys
from pathlib import Path
import pcbnew as p
from route_head_dovdd import v,xy
from route_r10_head import offset
from routing_geometry import add_via

ROOT=Path(__file__).resolve().parents[2]
LAYERS=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();assert not out.exists()
    shutil.copytree(ROOT/'generated/ov9281-r10-head-17',out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','checks'));(out/'checks').mkdir()
    path=out/'controller.kicad_pcb';b=p.LoadBoard(str(path));held=list(b.GetTracks());removed=[];created=[];routes=[];moves=[]
    for t in held:
        if t.GetNetname().startswith('/CAM_L_'):b.Remove(t);removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'reason':'replace independent MIPI route'})
    def pad(ref,net):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()==ref and q.GetNetname()==net)
    def route(net,points,layer):
        routes.append({'net':net,'layer':b.GetLayerName(layer),'points':points})
        for x,y in zip(points,points[1:]):
            if math.dist(x,y)<1e-8:continue
            t=p.PCB_TRACK(b);t.SetStart(v(*x));t.SetEnd(v(*y));t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(pad('U101',net).GetNetCode());t.SetLocked(True);b.Add(t);created.append(t)
    def via(net,point):
        t=add_via(b,v(*point),pad('U101',net).GetNetCode());t.SetLocked(True);created.append(t)
    for stem,center,sv,ev in [
        ('D0',[(15.65,4.3),(15.65,5.9),(19.055,5.9),(19.055,2.0),(20.1,2.0)],{'P':(15.35,4.3),'N':(15.95,4.3)},{'P':(20.1,2.251),'N':(20.1,1.749)}),
        ('D1',[(13.8,4.3),(13.8,6.75),(19.5,6.75),(20.25,6.375),(23,6.375),(24.1,6.25),(25,6.25)],{'P':(13.5,4.3),'N':(14.1,4.3)},{'P':(25,6.501),'N':(25,5.999)})]:
        for suffix,sign in [('P',-1),('N',1)]:
            net='/CAM_L_'+stem+'_'+suffix;start=xy(pad('U101',net).GetPosition());route(net,[start,(start[0],4.7),sv[suffix]],p.F_Cu)
            route(net,[sv[suffix]]+offset(center,.225*sign)+[ev[suffix]],p.B_Cu);via(net,sv[suffix]);via(net,ev[suffix])
            front=[(20.1,2.0),(22,3.25),(27.15,3.25)] if stem=='D0' else [(25,6.25),(27.15,6.25)]
            route(net,[ev[suffix]]+offset(front,.225*sign)+[xy(pad('J102',net).GetPosition())],p.F_Cu)
    clock=[(14.75,4.25),(14.75,2.5),(16.5,2.5),(21.5,4.0),(22.5,4.75),(27.15,4.75)]
    for suffix,sign in [('P',-1),('N',1)]:
        net='/CAM_L_CLK_'+suffix;start=xy(pad('U101',net).GetPosition());route(net,[start,(start[0],4.5)]+offset(clock,.225*sign)+[xy(pad('J102',net).GetPosition())],p.F_Cu)
    for sign,pin in [(-1,'7'),(1,'4')]:
        endpoint=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='J102' and q.GetNumber()==pin)
        guard=offset([(14.75,3.8)]+clock[1:-1]+[(26.9,4.75)],.426*sign)
        route('GND',guard+[(27.15,5.5 if sign<0 else 4.0),xy(endpoint.GetPosition())],p.F_Cu)
        route('GND',[guard[0],(15.35,3.55) if sign<0 else (14.0,3.55)],p.F_Cu)
    for point in [(13.5,3.55),(14.0,3.55),(15.35,3.55),(15.95,3.55),(19.8,1.349),(19.8,2.651),(24.7,5.599),(24.7,6.901),(26.8,4.0),(26.8,5.5)]:via('GND',point)
    route('GND',[(26.8,4.0),(27.15,4.0)],p.F_Cu)
    route('GND',[(26.8,5.5),(27.15,5.5)],p.F_Cu)
    moving=['R112','R115','Q102','C131','C132'];pending=set(moving)
    for ref in moving:
        f=next(f for f in b.GetFootprints() if f.GetReference()==ref);original=xy(f.GetPosition());placed=False
        candidates=sorted(((original[0]+i*.25,original[1]+j*.25) for i in range(-80,81) for j in range(-80,81)),key=lambda q:math.dist(q,original))
        for pos in candidates:
            f.SetPosition(v(*pos));court=f.GetCourtyard(p.B_CrtYd);box=court.BBox()
            if box.GetLeft()<p.FromMM(.5) or box.GetRight()>p.FromMM(31.5) or box.GetTop()<p.FromMM(.5) or box.GetBottom()>p.FromMM(19.5):continue
            if any(g.GetLayer()==p.B_Cu and g.GetReference() not in pending and court.Collide(g.GetCourtyard(p.B_CrtYd),10000) for g in b.GetFootprints()):continue
            if any(q.GetNetname()!=t.GetNetname() and q.IsOnLayer(p.B_Cu) and t.IsOnLayer(p.B_Cu) and q.GetEffectiveShape(p.B_Cu).Collide(t.GetEffectiveShape(p.B_Cu),100000) for q in f.Pads() for t in created):continue
            placed=True;break
        assert placed,ref
        moves.append({'ref':ref,'old':original,'new':pos});pending.remove(ref)
    pad_conflicts=[];pair_conflicts=[];blockers={};moved_pads=[q for q in b.GetPads() if q.GetParentFootprint().GetReference() in [m['ref'] for m in moves]]
    for item in created+moved_pads:
        for layer in LAYERS:
            if not item.IsOnLayer(layer):continue
            shape=item.GetEffectiveShape(layer)
            for q in b.GetPads():
                if q.GetNetname()!=item.GetNetname() and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(shape,100000):pad_conflicts.append({'net':item.GetNetname(),'route_xy':xy(item.GetPosition()),'ref':q.GetParentFootprint().GetReference(),'pad':q.GetNumber(),'xy':xy(q.GetPosition()),'layer':b.GetLayerName(layer)})
            for t in b.GetTracks():
                if t.GetNetname()==item.GetNetname() or not t.IsOnLayer(layer):continue
                if t.GetEffectiveShape(layer).Collide(shape,100000):
                    if t in created:pair_conflicts.append([item.GetNetname(),t.GetNetname(),xy(item.GetPosition()),xy(t.GetPosition())])
                    else:blockers[t.m_Uuid.AsString()]=t
    held.extend(blockers.values())
    for uid,t in blockers.items():b.Remove(t);removed.append({'uuid':uid,'net':t.GetNetname(),'reason':'pair corridor or moved support component'})
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    (out/'controller-pair-routing.json').write_text(json.dumps({'moves':moves,'routes':routes,'removed':removed,'pad_conflicts':pad_conflicts,'pair_conflicts':pair_conflicts},indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(out/'checks/controller-drc.json'),str(path)],check=True,capture_output=True)
    d=json.loads((out/'checks/controller-drc.json').read_text());print(json.dumps({'pad_conflicts':pad_conflicts,'pair_conflicts':pair_conflicts,'removed':len(removed),'violations':len(d['violations']),'unconnected':len(d['unconnected_items'])},indent=2))

if __name__=='__main__':main()

