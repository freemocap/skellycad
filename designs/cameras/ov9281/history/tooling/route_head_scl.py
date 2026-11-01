"""Explore a ground-track rip-up to complete SCL, preserving checked inputs."""
from pathlib import Path
import argparse,json,shutil,hashlib,subprocess,sys
import pcbnew as p
from route_isolated_head_pads import route
from routing_geometry import legal_vias,add_via,add_path
from route_head_dovdd import v,xy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    b=p.LoadBoard(str(src/'head.kicad_pcb'));pool=list(b.GetTracks())
    pad=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()=='E4')
    candidates=legal_vias(b,pad);proposal=route(b,pad,targets=candidates,commit=False,max_nodes=300000,ignore_track_nets=['GND']);assert proposal['result']=='routed',proposal
    points=proposal['path_xy_mm'];removed=[]
    for t in pool:
        if t.GetNetname()=='GND' and t.IsOnLayer(p.F_Cu) and not isinstance(t,p.PCB_VIA) and any(t.GetEffectiveShape(p.F_Cu).Collide(p.SHAPE_SEGMENT(v(*aa),v(*bb),100000),100000) for aa,bb in zip(points,points[1:])):
            removed.append({'uuid':t.m_Uuid.AsString(),'start':xy(t.GetStart()),'end':xy(t.GetEnd())});b.Remove(t)
    # Re-run with all remaining obstacles enabled before committing any copper.
    first=route(b,pad,targets=[v(*points[-1])]);assert first['result']=='routed',first
    start=v(*first['path_xy_mm'][-1]);via=add_via(b,start,pad.GetNetCode())
    endpoints={(point.x,point.y) for t in pool if t.GetNetname()==pad.GetNetname() and t.IsOnLayer(p.F_Cu) for point in [t.GetStart(),t.GetEnd()]}
    destinations=[q for q in legal_vias(b,pad) if (q.x,q.y) in endpoints]
    report={'source_head_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(),'removed_ground_tracks':removed,'front':first}
    for layer in [p.B_Cu,p.In2_Cu]:
        tail=route(b,pad,layer=layer,start=start,targets=destinations,max_nodes=300000)
        if tail['result']=='routed':add_via(b,v(*tail['path_xy_mm'][-1]),pad.GetNetCode());report['tail']={'layer':b.GetLayerName(layer),**tail};break
    else:raise AssertionError(tail)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    report['ground_repairs']={}
    for number in ['B2','E5']:
        ground=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()==number)
        fix=route(b,ground,max_nodes=300000);assert fix['result']=='routed',fix
        report['ground_repairs'][number]=fix
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'))
    (out/'validation.json').rename(out/'source-validation-scl.json');p.SaveBoard(str(out/'head.kicad_pcb'),b)
    (out/'scl-routing.json').write_text(json.dumps(report,indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(out/'checks/scl-drc.json'),str(out/'head.kicad_pcb')],capture_output=True,check=True)
    check=json.loads((out/'checks/scl-drc.json').read_text());print(json.dumps({'removed_ground':len(removed),'unconnected':len(check['unconnected_items']),'violations':[v['type'] for v in check['violations']]},indent=2))
if __name__=='__main__':main()
