"""Provide explicit controller support escapes around the protected MIPI routes."""
from pathlib import Path
import argparse,json,math,shutil,subprocess,sys
import pcbnew as p
from route_head_dovdd import v,xy
from routing_geometry import add_via

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();assert not a.output.exists()
    shutil.copytree(a.source,a.output,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','checks'));(a.output/'checks').mkdir()
    path=a.output/'controller.kicad_pcb';b=p.LoadBoard(str(path));held=list(b.GetTracks());new=[];record=[]
    def route(net,points,layer=p.F_Cu):
        for aa,zz in zip(points,points[1:]):
            t=p.PCB_TRACK(b);t.SetStart(v(*aa));t.SetEnd(v(*zz));t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net));t.SetLocked(True);b.Add(t);new.append(t)
    def via(net,pos):
        t=add_via(b,v(*pos),next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net));t.SetLocked(True);new.append(t)
    for net,old,pos in [('/FLASH_D',(18.475,4.075),(18.375,4.075))]:
        for t in list(b.GetTracks()):
            if t.GetNetname()!=net:continue
            if net=='/FLASH_D' and not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.F_Cu:held.append(t);b.Remove(t);continue
            if isinstance(t,p.PCB_VIA):
                if math.dist(xy(t.GetPosition()),old)<1e-6:t.SetPosition(v(*pos));new.append(t)
            else:
                changed=False
                if math.dist(xy(t.GetStart()),old)<1e-6:t.SetStart(v(*pos));changed=True
                if math.dist(xy(t.GetEnd()),old)<1e-6:t.SetEnd(v(*pos));changed=True
                if changed:new.append(t)
        record.append({'net':net,'via_old':old,'via_new':pos})
    print("Via moves complete",flush=True)
    route('/FLASH_D',[(18.775,5.125),(18.775,4.6),(18.375,4.075)])
    f=next(f for f in b.GetFootprints() if f.GetReference()=='R115');oldpads={q.GetNumber():xy(q.GetPosition()) for q in f.Pads()};f.SetPosition(v(17.25,3.6))
    for q in f.Pads():route(q.GetNetname(),[xy(q.GetPosition()),oldpads[q.GetNumber()]],p.B_Cu)
    record.append({'ref':'R115','old':[17.25,4.0],'new':[17.25,3.6]})
    print("Support move complete",flush=True)
    escapes=[
        ('/FLASH_HOLD',[(19.475,5.125),(19.475,4.65),(20.4,4.65),(20.4,4.5)],p.F_Cu),
        ('/FLASH_WP',[(20.175,5.125),(20.175,5.6),(19.8,5.85)],p.F_Cu),
        ('/P4_VDD_HP',[(21.375,5.625),(21.85,5.625),(22.9,5.7)],p.F_Cu),
        ('/USB_DM_CHIP',[(13.175,5.125),(13.175,5.5),(13.1,5.8)],p.F_Cu),
        ('/USB_DM_CHIP',[(12.76,2.0),(12.76,2.5),(12.0,2.8)],p.F_Cu),
        ('/M1_CAM_SCL_1V8',[(17.51,5.0),(17.51,4.65),(17.25,4.4)],p.B_Cu)]
    for net,points,layer in escapes:route(net,points,layer);via(net,points[-1]);record.append({'net':net,'escape':points,'layer':b.GetLayerName(layer)})
    print("Escapes built",flush=True)
    blockers={};conflicts=[];layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
    for item in new+list(f.Pads()):
        for layer in layers:
            if not item.IsOnLayer(layer):continue
            shape=item.GetEffectiveShape(layer)
            for q in b.GetPads():
                if q.GetNetname()!=item.GetNetname() and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(shape,100000):conflicts.append({'net':item.GetNetname(),'xy':xy(item.GetPosition()),'pad':q.GetParentFootprint().GetReference()+'.'+q.GetNumber(),'layer':b.GetLayerName(layer)})
            for t in b.GetTracks():
                if t.GetNetname()==item.GetNetname() or not t.IsOnLayer(layer) or not t.GetEffectiveShape(layer).Collide(shape,100000):continue
                if t in new or t.GetNetname().startswith('/CAM_L_') or t.IsLocked():conflicts.append({'net':item.GetNetname(),'xy':xy(item.GetPosition()),'other':t.GetNetname(),'other_xy':xy(t.GetPosition()),'layer':b.GetLayerName(layer)})
                else:blockers[t.m_Uuid.AsString()]=t
    if conflicts:print(json.dumps(conflicts,indent=2));raise AssertionError('Explicit escape conflicts; trial not saved')
    held.extend(blockers.values())
    for t in blockers.values():b.Remove(t)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    (a.output/'controller-explicit-escapes.json').write_text(json.dumps({'operations':record,'removed_copper':list(blockers)},indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(a.output/'checks/controller-drc.json'),str(path)],check=True,capture_output=True)
    print('Saved support escapes; removed',len(blockers),'ordinary obstructions')

if __name__=='__main__':main()

