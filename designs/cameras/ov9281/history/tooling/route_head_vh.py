"""Complete VH using a checked inner-layer detour; preserve source checkpoint.

In1 also carries the ground pour. Refill and native continuity checks are required;
this trial does not establish return-path quality or signal integrity.
"""
from pathlib import Path
import argparse,json,shutil,hashlib,subprocess,sys
import pcbnew as p
from route_isolated_head_pads import route
from routing_geometry import legal_vias,add_via
from route_head_dovdd import v,xy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    b=p.LoadBoard(str(src/'head.kicad_pcb'));pool=list(b.GetTracks())
    old=next(t for t in pool if t.m_Uuid.AsString()=='6b7bc895-8728-4f58-87ea-c1fd5061284f');start=old.GetStart();end=old.GetEnd();b.Remove(old)
    shifts=[]
    for t in pool:
        if t.GetNetname()=='/M1_SID' and t.GetLayer()==p.In2_Cu:
            for get,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
                point=get()
                if xy(point) in [(1.0105,5.9883),(10.6005,5.9883)]:
                    new=v(point.x/1e6,point.y/1e6-.05);shifts.append({'uuid':t.m_Uuid.AsString(),'from':xy(point),'to':xy(new)});setter(new)
    pad=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()=='E8')
    via=v(9.005,6.507);assert (via.x,via.y) in {(q.x,q.y) for q in legal_vias(b,pad)}
    front=route(b,pad,targets=[via]);assert front['result']=='routed';add_via(b,via,pad.GetNetCode())
    destination=v(11.0276,10.6073);assert (destination.x,destination.y) in {(q.x,q.y) for q in legal_vias(b,pad)}
    tail=route(b,pad,layer=p.In1_Cu,start=via,targets=[destination],max_nodes=300000);assert tail['result']=='routed';add_via(b,destination,pad.GetNetCode())
    other=next(q for q in b.GetPads() if q.GetNetname()=='/M1_VN1')
    repair=route(b,other,layer=p.In2_Cu,start=start,targets=[end],max_nodes=300000);assert repair['result']=='routed'
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'));(out/'validation.json').rename(out/'source-validation-vh.json')
    p.SaveBoard(str(out/'head.kicad_pcb'),b)
    (out/'vh-routing.json').write_text(json.dumps({'source_head_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(),'front':front,'In1_VH_path':tail,'SID_endpoint_changes':shifts,'VN1_repair':repair,'limit':'Added In1 bias routing interrupts the ground pour; continuity is checked separately from return-path qualification.'},indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(out/'checks/vh-drc.json'),str(out/'head.kicad_pcb')],capture_output=True,check=True)
    check=json.loads((out/'checks/vh-drc.json').read_text());print(json.dumps({'unconnected':len(check['unconnected_items']),'violations':[v['type'] for v in check['violations']]},indent=2))
if __name__=='__main__':main()
