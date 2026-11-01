"""Match controller pairs in a new trial; native validation remains mandatory."""
from pathlib import Path
import argparse,json,math,shutil,subprocess,sys
import pcbnew as p
import audit_interconnect as audit
from route_head_dovdd import v,xy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();assert not a.output.exists()
    shutil.copytree(a.source,a.output,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','checks'));(a.output/'checks').mkdir()
    path=a.output/'controller.kicad_pcb';b=p.LoadBoard(str(path));held=list(b.GetTracks());created=[];log=[]
    audit.COPPER=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
    def replace(t,points):
        layer,code,width=t.GetLayer(),t.GetNetCode(),t.GetWidth();b.Remove(t);held.append(t)
        for x,y in zip(points,points[1:]):
            q=p.PCB_TRACK(b);q.SetStart(v(*x));q.SetEnd(v(*y));q.SetLayer(layer);q.SetNetCode(code);q.SetWidth(width);q.SetLocked(True);b.Add(q);created.append(q)
    for pair,suffix,layer,x0,x1,direction in [('D0','N',p.F_Cu,23.5,24.3,-1),('CLK','P',p.F_Cu,25.3,25.9,1),('D1','N',p.B_Cu,14.3,14.8,-1)]:
        g=audit.geometry(b);records={s:audit.route_record(b,g,'controller','/CAM_L_'+pair+'_'+s,['U101','J102']) for s in ['P','N']}
        extra=max(r['path_length_mm'] for r in records.values())-records[suffix]['path_length_mm'];assert extra>0;delta=direction*extra/2
        net='/CAM_L_'+pair+'_'+suffix;t=next(t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()==net and t.GetLayer()==layer and abs(xy(t.GetStart())[1]-xy(t.GetEnd())[1])<1e-8 and xy(t.GetStart())[0]<x0<x1<xy(t.GetEnd())[0]);start,end=xy(t.GetStart()),xy(t.GetEnd());y=start[1]
        replace(t,[start,(x0,y),(x0,y+delta),(x1,y+delta),(x1,y),end]);log.append({'net':net,'added_mm':extra,'amplitude_mm':delta})
        if pair=='CLK':
            guard=next(t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND' and t.GetLayer()==p.F_Cu and abs(xy(t.GetStart())[1]-5.176)<1e-7 and abs(xy(t.GetEnd())[1]-5.176)<1e-7 and xy(t.GetStart())[0]<x0 and xy(t.GetEnd())[0]>x1)
            replace(guard,[xy(guard.GetStart()),(x0-.201,5.176),(x0-.201,y+delta+.201),(x1+.201,y+delta+.201),(x1+.201,5.176),xy(guard.GetEnd())])
    blockers={};conflicts=[]
    for t in created:
        layer=t.GetLayer();shape=t.GetEffectiveShape(layer)
        for q in list(b.GetPads())+list(b.GetTracks()):
            if q.GetNetname()==t.GetNetname() or not q.IsOnLayer(layer) or not q.GetEffectiveShape(layer).Collide(shape,100000):continue
            if isinstance(q,p.PAD) or q.IsLocked():conflicts.append([t.GetNetname(),q.GetNetname(),xy(q.GetPosition())])
            else:blockers[q.m_Uuid.AsString()]=q
    assert not conflicts,conflicts
    held.extend(blockers.values())
    for t in blockers.values():b.Remove(t)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    (a.output/'controller-matching.json').write_text(json.dumps({'adjustments':log,'removed_ordinary_copper':list(blockers)},indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(a.output/'checks/controller-drc.json'),str(path)],check=True,capture_output=True)
    print(json.dumps(log,indent=2))

if __name__=='__main__':main()
