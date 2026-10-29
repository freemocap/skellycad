"""Open practical support-component escapes around the completed MIPI geometry."""
from pathlib import Path
import argparse,json,math,shutil,subprocess,sys
import pcbnew as p
from route_head_dovdd import v,xy
from routing_geometry import add_via

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();assert not a.output.exists();shutil.copytree(a.source,a.output,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','checks'));(a.output/'checks').mkdir()
    path=a.output/'controller.kicad_pcb';b=p.LoadBoard(str(path));held=list(b.GetTracks());new=[];moves=[]
    def remove(t):held.append(t);b.Remove(t)
    def route(net,points,layer=p.F_Cu):
        code=next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net)
        for aa,zz in zip(points,points[1:]):
            t=p.PCB_TRACK(b);t.SetStart(v(*aa));t.SetEnd(v(*zz));t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(code);t.SetLocked(True);b.Add(t);new.append(t)
    def via(net,pos):
        t=add_via(b,v(*pos),next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net));t.SetLocked(True);new.append(t)
    for t in list(b.GetTracks()):
        net=t.GetNetname()
        if isinstance(t,p.PCB_VIA):
            if net=='/P4_VDD_HP' and math.dist(xy(t.GetPosition()),(22.9,5.7))<1e-6:remove(t)
            continue
        aa,zz=xy(t.GetStart()),xy(t.GetEnd())
        if net=='/P4_VDD_HP' and t.IsLocked() and t.GetLayer() in [p.F_Cu,p.B_Cu]:remove(t)
        elif net=='/M1_CAM_SCL_1V8' and t.GetLayer()==p.B_Cu and all(17.1<=q[0]<=17.9 and 4.3<=q[1]<=5.5 for q in [aa,zz]):remove(t)
        elif net in ['+3V3','/CAM_SDA_3V3'] and t.IsLocked() and t.GetLayer()==p.B_Cu and all(16.4<=q[0]<=18 and 3<=q[1]<=4.5 for q in [aa,zz]):remove(t)
        elif net=='/P4_MIPI_2V5' and t.GetLayer()==p.F_Cu and all(15<=q[0]<=16.5 and 4.5<=q[1]<=6 for q in [aa,zz]):remove(t)
    for net,old,pos in [('/FLASH_WP',(20.6,7.1),(20.55,7.1)),('/FLASH_CLK',(23.8,5.575),(25.365,3.95))]:
        for t in list(b.GetTracks()):
            if t.GetNetname()!=net:continue
            if isinstance(t,p.PCB_VIA):
                if math.dist(xy(t.GetPosition()),old)<1e-6:t.SetPosition(v(*pos));new.append(t)
                continue
            if net=='/FLASH_CLK' and any(math.dist(xy(pt),old)<1e-6 for pt in [t.GetStart(),t.GetEnd()]):remove(t);continue
            changed=False
            for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
                if math.dist(xy(getter()),old)<1e-6:setter(v(*pos));changed=True
            if changed:new.append(t)
    for ref,pos in [('R112',(24,11)),('R115',(24,12)),('C131',(16.5,2.75))]:
        f=next(f for f in b.GetFootprints() if f.GetReference()==ref);moves.append({'ref':ref,'old':xy(f.GetPosition()),'new':pos});f.SetPosition(v(*pos))
        if ref=='C131':f.SetOrientationDegrees(180)
        if ref=='R115':f.Flip(f.GetPosition(),False);f.SetOrientationDegrees(0);moves[-1]['side']='F.Cu'
    for ref,y in [('R112',10.3),('R115',12.7)]:
        f=next(f for f in b.GetFootprints() if f.GetReference()==ref)
        for q in f.Pads():
            pos=xy(q.GetPosition());point=(pos[0],y);route(q.GetNetname(),[pos,point],f.GetLayer());via(q.GetNetname(),point)
    cap=next(f for f in b.GetFootprints() if f.GetReference()=='C131');positive=next(q for q in cap.Pads() if q.GetNumber()=='1');ground=next(q for q in cap.Pads() if q.GetNumber()=='2')
    route('/P4_MIPI_2V5',[(15.975,5.125),(15.975,4.7),(16.35,4.55),(16.35,3.8),(16.5,3.8)]);via('/P4_MIPI_2V5',(16.5,3.8))
    route('/P4_MIPI_2V5',[xy(positive.GetPosition()),(16.98,3.2),(16.5,3.8)],p.B_Cu)
    route('GND',[xy(ground.GetPosition()),(15.95,3.55)],p.B_Cu)
    route('/P4_VDD_HP',[(21.375,5.625),(22.4,5.85),(23.2,6.1),(24.2,6.1),(24.2,5.55)]);via('/P4_VDD_HP',(24.2,5.55))
    route('/P4_VDD_HP',[(21.27,5.5),(21.27,4.95),(24.2,4.95),(24.2,5.55)],p.B_Cu)
    route('GND',[(22.23,5.5),(22.9,5.5)],p.B_Cu);via('GND',(22.9,5.5))
    route('/FLASH_CLK',[(25.365,1.9125),(25.365,3.95)],p.B_Cu)
    route('/FLASH_CS',[(20.9,6.65),(20.9,8.7),(20.6,8.7)]);via('/FLASH_CS',(20.6,8.7))
    blockers={};conflicts=[];layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];moved_pads=[q for q in b.GetPads() if q.GetParentFootprint().GetReference() in ['R112','R115','C131']]
    for item in new+moved_pads:
        for layer in layers:
            if not item.IsOnLayer(layer):continue
            shape=item.GetEffectiveShape(layer)
            for q in b.GetPads():
                if q.GetNetname()!=item.GetNetname() and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(shape,100000):conflicts.append({'net':item.GetNetname(),'xy':xy(item.GetPosition()),'pad':q.GetParentFootprint().GetReference()+'.'+q.GetNumber(),'layer':b.GetLayerName(layer)})
            for t in b.GetTracks():
                if t.GetNetname()==item.GetNetname() or not t.IsOnLayer(layer) or not t.GetEffectiveShape(layer).Collide(shape,100000):continue
                if t in new or t.GetNetname().startswith('/CAM_L_') or (t.IsLocked() and t.GetNetname()=='GND'):conflicts.append({'net':item.GetNetname(),'xy':xy(item.GetPosition()),'other':t.GetNetname(),'other_xy':xy(t.GetPosition()),'layer':b.GetLayerName(layer)})
                else:blockers[t.m_Uuid.AsString()]=t
    if conflicts:print(json.dumps(conflicts,indent=2));raise AssertionError('Support closure conflicts; trial not saved')
    for t in blockers.values():remove(t)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b);(a.output/'controller-support-closure.json').write_text(json.dumps({'moves':moves,'removed':list(blockers)},indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(a.output/'checks/controller-drc.json'),str(path)],check=True,capture_output=True)
    print('Saved support closure; removed',len(blockers),'ordinary obstructions')

if __name__=='__main__':main()
