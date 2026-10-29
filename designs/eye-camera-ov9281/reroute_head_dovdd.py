"""Connect U1.B7 and replace its obstructing DVDD branch with a via escape.

Preserves footprints, nets and design rules. Native DRC remains authoritative.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
import pcbnew as p
from route_isolated_head_pads import route
from routing_geometry import legal_vias,add_via
from route_head_dovdd import v,xy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    b=p.LoadBoard(str(src/'head.kicad_pcb'))
    track=next(t for t in b.GetTracks() if t.m_Uuid.AsString()=='d90cdf89-2192-4f9f-8054-d8dd4a8faa4e')
    assert track.GetNetname()=='/M1_DVDD'
    removed={'uuid':track.m_Uuid.AsString(),'net':track.GetNetname(),'start':xy(track.GetStart()),'end':xy(track.GetEnd())};b.Remove(track)
    def pad(n):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()==n)
    dovdd=route(b,pad('B7'));assert dovdd['result']=='routed',dovdd
    dvdd_pad=pad('D8');escape=route(b,dvdd_pad,targets=legal_vias(b,dvdd_pad));assert escape['result']=='routed',escape
    via_position=v(*escape['path_xy_mm'][-1]);via=add_via(b,via_position,dvdd_pad.GetNetCode())
    back=route(b,dvdd_pad,layer=p.B_Cu,start=via_position);assert back['result']=='routed',back
    # Refill first: the new DVDD via divides a narrow ground-plane connection
    # serving A7. Bridge its existing via to ground on B.Cu explicitly.
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    ground_pad=pad('A7');assert ground_pad.GetNetname()=='GND'
    ground=route(b,ground_pad,layer=p.B_Cu,start=v(8.806,3.8503));assert ground['result']=='routed',ground
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'))
    if (out/'validation.json').exists():(out/'validation.json').rename(out/'source-validation-dovdd.json')
    p.SaveBoard(str(out/'head.kicad_pcb'),b)
    pruned=[]
    for attempt in range(8):
        report_path=out/'checks'/f'dovdd-cleanup-{attempt}.json'
        subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(report_path),str(out/'head.kicad_pcb')],capture_output=True,check=True)
        native=json.loads(report_path.read_text())
        ids={i['uuid'] for violation in native['violations'] if violation['type']=='track_dangling' for i in violation['items'] if '[/M1_DVDD]' in i['description']}
        if not ids:break
        for t in list(b.GetTracks()):
            if t.m_Uuid.AsString() in ids:
                assert t.GetNetname()=='/M1_DVDD' and not isinstance(t,p.PCB_VIA)
                pruned.append({'uuid':t.m_Uuid.AsString(),'start':xy(t.GetStart()),'end':xy(t.GetEnd())});b.Remove(t)
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'head.kicad_pcb'),b)
    else:raise AssertionError('DVDD cleanup did not converge')
    previous=json.loads((src/'checks/head-drc.json').read_text())
    assert len(native['unconnected_items'])==len(previous['unconnected_items'])-1
    assert {i['uuid'] for violation in native['violations'] for i in violation['items']}=={i['uuid'] for violation in previous['violations'] for i in violation['items']},'New native DRC violations'
    assert all(violation['type']=='track_dangling' for violation in native['violations'])
    report={'source':str(src),'source_head_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(),'removed':removed,'dovdd':dovdd,'dvdd_escape':escape,'dvdd_back':back,'new_via':via.m_Uuid.AsString(),'ground_bridge':ground,'pruned_dvdd_stubs':pruned,'requires_native_drc':True}
    (out/'dovdd-reroute.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
