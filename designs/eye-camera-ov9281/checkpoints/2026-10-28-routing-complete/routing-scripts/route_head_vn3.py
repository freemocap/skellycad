"""Connect VN3 with a capacitor-side via and restore nearby AVDD/SCL paths."""
from pathlib import Path
import argparse,json,shutil,hashlib,subprocess,sys
import pcbnew as p
from route_isolated_head_pads import route
from routing_geometry import legal_vias,add_via
from route_head_dovdd import v,xy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    b=p.LoadBoard(str(src/'head.kicad_pcb'));pool=list(b.GetTracks());removed=[]
    for t in pool:
        if t.m_Uuid.AsString()=='2afd1823-f438-4b9e-ab8c-6cb4f1da34b6' or (t.GetNetname()=='/M1_CAM_SCL_1V8' and t.GetLayer()==p.F_Cu and xy(t.GetStart()) in [(8.59,7.507),(10.765,7.507)]):
            removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'start':xy(t.GetStart()),'end':xy(t.GetEnd())});b.Remove(t)
    assert len(removed)==3
    def pad(n):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()==n)
    via=v(10.275,7.175);assert (via.x,via.y) in {(q.x,q.y) for q in legal_vias(b,pad('F7'))}
    front=route(b,pad('F7'),targets=[via]);assert front['result']=='routed';add_via(b,via,pad('F7').GetNetCode())
    back=route(b,pad('F7'),layer=p.B_Cu,start=via);assert back['result']=='routed'
    avdd=route(b,pad('G8'),max_nodes=300000);assert avdd['result']=='routed'
    scl=route(b,pad('E4'),start=v(8.59,7.507),max_nodes=300000);assert scl['result']=='routed'
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'));(out/'validation.json').rename(out/'source-validation-vn3.json');p.SaveBoard(str(out/'head.kicad_pcb'),b)
    (out/'vn3-routing.json').write_text(json.dumps({'source_head_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(),'removed':removed,'front':front,'back':back,'avdd_repair':avdd,'scl_repair':scl},indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(out/'checks/vn3-drc.json'),str(out/'head.kicad_pcb')],capture_output=True,check=True)
    check=json.loads((out/'checks/vn3-drc.json').read_text());print(json.dumps({'unconnected':len(check['unconnected_items']),'violations':[v['type'] for v in check['violations']]},indent=2))
if __name__=='__main__':main()
