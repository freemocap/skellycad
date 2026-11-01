"""Explicit paired head routing trials; never modify the selected input."""
from pathlib import Path
import argparse,json,math,shutil,subprocess,sys
import pcbnew as p
from route_head_dovdd import v,xy
from routing_geometry import add_via

ROOT=Path(__file__).resolve().parents[2]
CLI=Path(sys.executable).with_name('kicad-cli.exe')

def offset(points,amount):
    lines=[]
    for a,b in zip(points,points[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);n=(dy/length*amount,-dx/length*amount)
        lines.append(((a[0]+n[0],a[1]+n[1]),(b[0]+n[0],b[1]+n[1])))
    out=[lines[0][0]]
    for (a,b),(c,d) in zip(lines,lines[1:]):
        ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=d[0]-c[0],d[1]-c[1];den=ux*vy-uy*vx
        if abs(den)<1e-12:out.append(b);continue
        t=((c[0]-a[0])*vy-(c[1]-a[1])*vx)/den;out.append((a[0]+t*ux,a[1]+t*uy))
    return out+[lines[-1][1]]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();out=args.output.resolve();assert not out.exists()
    src=ROOT/'generated/ov9281-r10-planes-02';shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','checks'));(out/'checks').mkdir()
    b=p.LoadBoard(str(out/'head.kicad_pcb'));held=list(b.GetTracks());removed=[];new=[];routes=[]
    for t in held:
        if t.GetNetname().startswith('/CAM_L_'):b.Remove(t);removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'reason':'old independent signal route'})
    moved=[]
    for ref,pos in [('L1',(3.3,1.1)),('L2',(11.5,1.2))]:
        f=next(f for f in b.GetFootprints() if f.GetReference()==ref);moved.append({'ref':ref,'old':xy(f.GetPosition()),'new':pos});f.SetPosition(v(*pos))
    def pad(ref,net):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()==ref and q.GetNetname()==net)
    def route(net,points,layer):
        code=pad('U1',net).GetNetCode();routes.append({'net':net,'layer':b.GetLayerName(layer),'points':points,'length_mm':sum(math.dist(a,z) for a,z in zip(points,points[1:]))})
        for a,z in zip(points,points[1:]):
            if math.dist(a,z)<1e-8:continue
            t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(code);t.SetLocked(True);b.Add(t);new.append(t)
    def via(net,point):
        t=add_via(b,v(*point),pad('U1',net).GetNetCode());t.SetLocked(True);new.append(t)
    stems={'D0':[(6,8.6),(6,8.9),(2,10.2),(2,11.2)],'CLK':[(7.3,8.6),(7.3,9.4),(3.5,10.6),(3.5,11.2)],'D1':[(8.6,8.9),(8.6,9.9),(5,11.0),(5,11.2)]}
    stubs={
      'D0_P':[(6.125,7.257),(6.445,7.507),(6.445,8.2),(6.225,8.6)],
      'D0_N':[(6.125,7.757),(5.4,8.1),(5.4,8.45),(5.775,8.6)],
      'CLK_P':[(6.765,7.257),(7.085,7.507),(7.085,8.1),(7.525,8.6)],
      'CLK_N':[(6.765,7.757),(6.765,8.2),(7.075,8.6)],
      'D1_P':[(7.405,7.257),(7.085,7.007)],
      'D1_N':[(7.405,6.757),(7.085,6.507)]}
    for suffix,points in stubs.items():route('/CAM_L_'+suffix,points,p.F_Cu)
    for stem,points in stems.items():
        for suffix,sign in [('P',1),('N',-1)]:
            net='/CAM_L_'+stem+'_'+suffix;q=offset(points,.225*sign)
            if stem=='CLK' and suffix=='N':
                # Compensate the unequal sensor-pad escape before the long run.
                extra=sum(math.dist(a,z) for a,z in zip(stubs['CLK_P'],stubs['CLK_P'][1:]))-sum(math.dist(a,z) for a,z in zip(stubs['CLK_N'],stubs['CLK_N'][1:]))
                bulge=math.sqrt(((extra+.4)/2)**2-.2**2)
                q=q[:1]+[(7.075-bulge,8.8),(7.075-bulge,9.0),(7.075,9.2)]+q[1:]
            if stem=='D1':q=[(8.6+.25*sign,8.9)]+q
            route(net,q+[xy(pad('J201',net).GetPosition())],p.F_Cu)
    back=[(7.085,6.757),(6.6,6.757),(6.6,8.2),(8.6,8.2),(8.6,8.9)]
    for suffix,sign in [('P',1),('N',-1)]:
        net='/CAM_L_D1_'+suffix;start=stubs['D1_'+suffix][-1];end=(8.6+.25*sign,8.9)
        q=offset(back,.225*sign)
        if suffix=='P':q=q[:3]+[(7.05,7.975),(7.05,7.525),(7.375,7.525),(7.375,7.975)]+q[3:]
        route(net,[start]+q+[end],p.B_Cu);via(net,start);via(net,end)
    for point in [(7.725,6.507),(7.725,7.007),(7.95,9.3),(9.25,8.55)]:via('GND',point)
    # Remove only obstructing old copper; native pad collisions remain failures.
    pads=[];pair_collisions=[];blockers={}
    layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
    moved_pads=[q for q in b.GetPads() if q.GetParentFootprint().GetReference() in ['L1','L2']]
    for a in new+moved_pads:
        for layer in layers:
            if not a.IsOnLayer(layer):continue
            shape=a.GetEffectiveShape(layer)
            for q in b.GetPads():
                if q.GetNetname()!=a.GetNetname() and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(shape,100000):pads.append({'route':a.GetNetname(),'ref':q.GetParentFootprint().GetReference(),'pad':q.GetNumber(),'net':q.GetNetname(),'xy':xy(q.GetPosition()),'layer':b.GetLayerName(layer)})
            for t in b.GetTracks():
                if t.GetNetname()==a.GetNetname() or not t.IsOnLayer(layer):continue
                if t.GetEffectiveShape(layer).Collide(shape,100000):
                    if t in new:pair_collisions.append([a.GetNetname(),t.GetNetname(),xy(a.GetPosition()),xy(t.GetStart())])
                    else:blockers[t.m_Uuid.AsString()]=t
    held.extend(blockers.values())
    for uid,t in blockers.items():b.Remove(t);removed.append({'uuid':uid,'net':t.GetNetname(),'reason':'paired-route corridor'})
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'head.kicad_pcb'),b)
    report={'moves':moved,'routes':routes,'removed':removed,'pad_collisions':pads,'pair_collisions':pair_collisions}
    (out/'head-pair-routing.json').write_text(json.dumps(report,indent=2)+'\n')
    subprocess.run([str(CLI),'pcb','drc','--format','json','--output',str(out/'checks/head-drc.json'),str(out/'head.kicad_pcb')],capture_output=True,check=True)
    drc=json.loads((out/'checks/head-drc.json').read_text());print(json.dumps({'pad_collisions':pads,'pair_collisions':pair_collisions,'removed':len(removed),'drc':len(drc['violations']),'unconnected':len(drc['unconnected_items'])},indent=2))

if __name__=='__main__':main()
