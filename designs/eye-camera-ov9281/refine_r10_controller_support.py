"""Refine crowded support escapes without changing the controller interfaces."""
from pathlib import Path
import argparse,json,math,shutil,subprocess,sys
import pcbnew as p
from route_head_dovdd import v,xy
from routing_geometry import add_via

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();assert not a.output.exists()
    shutil.copytree(a.source,a.output,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','checks'));(a.output/'checks').mkdir();path=a.output/'controller.kicad_pcb';b=p.LoadBoard(str(path));held=list(b.GetTracks());new=[];record=[]
    def remove(t):held.append(t);b.Remove(t)
    def route(net,points,layer=p.F_Cu):
        code=next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net)
        for aa,zz in zip(points,points[1:]):
            t=p.PCB_TRACK(b);t.SetStart(v(*aa));t.SetEnd(v(*zz));t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(code);t.SetLocked(True);b.Add(t);new.append(t)
    def via(net,pos):
        t=add_via(b,v(*pos),next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net));t.SetLocked(True);new.append(t)
    for net,old,pos in [('/FLASH_D',(18.375,4.075),(17.8,4.35)),('/FLASH_D',(23.15,2.525),(23.0,2.525)),('/CAM_SDA_3V3',(18.2,4.5),(16.7,4.35))]:
        for t in list(b.GetTracks()):
            if t.GetNetname()!=net:continue
            if isinstance(t,p.PCB_VIA):
                if math.dist(xy(t.GetPosition()),old)<1e-6:t.SetPosition(v(*pos));new.append(t)
                continue
            if net=='/FLASH_D' and t.GetLayer()==p.F_Cu:remove(t);continue
            if net=='/CAM_SDA_3V3' and t.GetLayer()==p.B_Cu and any(math.dist(xy(pt),old)<1e-6 for pt in [t.GetStart(),t.GetEnd()]):remove(t);continue
            if t.GetLayer() in [p.In2_Cu,p.In3_Cu] and any(math.dist(xy(pt),old)<1e-6 for pt in [t.GetStart(),t.GetEnd()]):remove(t);continue
            changed=False
            for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
                if math.dist(xy(getter()),old)<1e-6:setter(v(*pos));changed=True
            if changed:new.append(t)
        record.append({'net':net,'old_via':old,'new_via':pos})
    # Keep the same added length while narrowing the local D1 compensation box.
    for t in b.GetTracks():
        if t.GetNetname()!='/CAM_L_D1_N' or isinstance(t,p.PCB_VIA) or t.GetLayer()!=p.B_Cu:continue
        changed=False
        for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
            x,y=xy(getter())
            if 6.0<y<6.6 and (abs(x-14.3)<1e-6 or abs(x-14.8)<1e-6):setter(v(14.25 if abs(x-14.3)<1e-6 else 14.5,y));changed=True
        if changed:new.append(t)
    for t in list(b.GetTracks()):
        if t.GetNetname()=='/FLASH_WP' and ((isinstance(t,p.PCB_VIA) and math.dist(xy(t.GetPosition()),(19.8,5.85))<1e-6) or (not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.F_Cu)):remove(t)
        elif not isinstance(t,p.PCB_VIA) and t.IsLocked() and t.GetLayer()==p.B_Cu and t.GetNetname() in ['+3V3','/CAM_SDA_3V3'] and abs(xy(t.GetStart())[1]-3.6)<1e-6 and abs(xy(t.GetEnd())[1]-4.0)<1e-6:remove(t)
    f=next(f for f in b.GetFootprints() if f.GetReference()=='R115');f.SetPosition(v(17.25,3.1));record.append({'ref':'R115','new':[17.25,3.1]})
    route('/FLASH_D',[(18.775,5.125),(18.775,4.65),(17.8,4.35)])
    route('/CAM_SDA_3V3',[(17.76,3.1),(17.76,3.6),(16.7,4.35)],p.B_Cu)
    route('+3V3',[(16.74,3.1),(16.74,4.0)],p.B_Cu)
    for net,points in [
        ('/FLASH_CLK',[(19.125,5.125),(19.125,4.35),(18.35,3.9)]),
        ('/FLASH_WP',[(20.175,5.125),(20.175,6.09),(20.41,6.09),(20.41,6.9),(20.6,7.1)]),
        ('/P4_FLASH_VDD',[(19.825,5.125),(19.825,5.6),(19.8,5.85)]),
        ('/P4_CSI_REXT',[(13.525,5.125),(13.525,5.601),(14.97,5.601),(14.97,5.85)])]:route(net,points);via(net,points[-1]);record.append({'net':net,'escape':points})
    route('/P4_FLASH_VDD',[(19.75,5.23),(19.75,5.6),(19.8,5.85)],p.B_Cu)
    route('/P4_VDD_HP',[(21.27,5.5),(21.27,4.95),(22.9,4.95),(22.9,5.7)],p.B_Cu)
    blockers={};conflicts=[];layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
    for item in new+list(f.Pads()):
        for layer in layers:
            if not item.IsOnLayer(layer):continue
            shape=item.GetEffectiveShape(layer)
            for q in b.GetPads():
                if q.GetNetname()!=item.GetNetname() and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(shape,100000):conflicts.append({'net':item.GetNetname(),'xy':xy(item.GetPosition()),'pad':q.GetParentFootprint().GetReference()+'.'+q.GetNumber(),'layer':b.GetLayerName(layer)})
            for t in b.GetTracks():
                if t.GetNetname()==item.GetNetname() or not t.IsOnLayer(layer) or not t.GetEffectiveShape(layer).Collide(shape,100000):continue
                if t in new or t.GetNetname().startswith('/CAM_L_') or (t.IsLocked() and t.GetNetname()=='GND'):conflicts.append({'net':item.GetNetname(),'xy':xy(item.GetPosition()),'other':t.GetNetname(),'other_xy':xy(t.GetPosition()),'layer':b.GetLayerName(layer)})
                else:blockers[t.m_Uuid.AsString()]=t
    if conflicts:print(json.dumps(conflicts,indent=2));raise AssertionError('Support refinement conflicts; trial not saved')
    for t in blockers.values():remove(t)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    (a.output/'controller-support-refinement.json').write_text(json.dumps({'operations':record,'removed':list(blockers)},indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(a.output/'checks/controller-drc.json'),str(path)],check=True,capture_output=True)
    print('Saved support refinement; removed',len(blockers),'ordinary obstructions')

if __name__=='__main__':main()
