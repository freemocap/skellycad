"""Create an isolated, all-front USB pair-routing trial."""
import json,math,shutil,subprocess,sys
from pathlib import Path
import pcbnew as p
from route_head_dovdd import v,xy
from route_r10_head import offset

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'generated/ov9281-r10-usb-03'
def length(points):return sum(math.dist(a,z) for a,z in zip(points,points[1:]))

def main():
    assert not OUT.exists();shutil.copytree(ROOT/'generated/ov9281-r10-flex-03',OUT)
    path=OUT/'controller.kicad_pcb';b=p.LoadBoard(str(path));held=[];created=[];removed=[]
    for t in b.GetTracks():
        if t.GetNetname().startswith('/USB_D'):held.append(t);b.Remove(t)
    for ref,y in [('R109',2.4),('R110',3.4)]:
        f=next(f for f in b.GetFootprints() if f.GetReference()==ref);f.SetPosition(v(11.7,y))
    def pad(ref,num):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()==ref and q.GetNumber()==str(num))
    def route(net,points):
        code=next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net)
        for aa,zz in zip(points,points[1:]):
            if math.dist(aa,zz)<1e-8:continue
            t=p.PCB_TRACK(b);t.SetNetCode(code);t.SetLayer(p.F_Cu);t.SetWidth(p.FromMM(.1));t.SetStart(v(*aa));t.SetEnd(v(*zz));t.SetLocked(True);b.Add(t);created.append(t)
    chip={};connector={}
    for pol,ref,sign,pin in [('DP','R110',1,50),('DM','R109',-1,49)]:
        start=xy(pad('U101',pin).GetPosition());q=offset([(12.7,4.45),(12.7,2.9),(12.3,2.9)],sign*.125)
        chip[pol]=[start,(start[0],4.8)]+q+[xy(pad(ref,2).GetPosition())]
        yy=3.5375 if pol=='DP' else 2.4625
        connector[pol]=[xy(pad(ref,1).GetPosition()),(10.1,yy),(8.4,yy),(7.85,yy)]+offset([(7.7,3),(7.51,3),(7.51,4.75),(7.3,4.75)],sign*.125)+[xy(pad('J101',3 if pol=='DP' else 2).GetPosition())]
    difference=length(chip['DM'])+length(connector['DM'])-length(chip['DP'])-length(connector['DP']);assert difference>0
    q=chip['DP'];xx=12.575;xx2=xx-difference/2;chip['DP']=q[:3]+[(xx,4.4),(xx2,4.4),(xx2,4.15),(xx,4.15)]+q[3:]
    for pol in ['DP','DM']:route('/USB_'+pol+'_CHIP',chip[pol]);route('/USB_'+pol,connector[pol])
    # Only ordinary obstructing copper may be removed; preserve all MIPI routes.
    layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];newids={t.m_Uuid.AsString() for t in created};blockers={};pad_collisions=[]
    changed_pads=[q for q in b.GetPads() if q.GetParentFootprint().GetReference() in ['R109','R110']]
    for aa in created+changed_pads:
        for layer in layers:
            if not aa.IsOnLayer(layer):continue
            shape=aa.GetEffectiveShape(layer)
            for q in b.GetPads():
                if q.GetNetname()!=aa.GetNetname() and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(shape,100000):pad_collisions.append({'net':aa.GetNetname(),'ref':q.GetParentFootprint().GetReference(),'pin':q.GetNumber(),'xy':xy(q.GetPosition())})
            for t in b.GetTracks():
                if t.GetNetname()==aa.GetNetname() or not t.IsOnLayer(layer) or t.m_Uuid.AsString() in newids:continue
                if t.GetEffectiveShape(layer).Collide(shape,100000):
                    assert not t.GetNetname().startswith('/CAM_L_'),('MIPI collision',t.GetNetname())
                    blockers[t.m_Uuid.AsString()]=True
    for t in b.GetTracks():
        if t.m_Uuid.AsString() in blockers:held.append(t);removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'xy':xy(t.GetStart())});b.Remove(t)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    report={'chip_paths':chip,'connector_paths':connector,'p_compensation_mm':difference,'removed':removed,'pad_collisions':pad_collisions};(OUT/'usb-route-construction.json').write_text(json.dumps(report,indent=2)+'\n')
    cli=Path(sys.executable).with_name('kicad-cli.exe');drc=OUT/'checks/controller-drc.json';subprocess.run([str(cli),'pcb','drc','--format','json','--output',str(drc),str(path)],capture_output=True,check=True);d=json.loads(drc.read_text());print(json.dumps({'removed':removed,'pad_collisions':pad_collisions,'drc':len(d['violations']),'unconnected':len(d['unconnected_items']),'compensation_mm':difference},indent=2))

if __name__=='__main__':main()
