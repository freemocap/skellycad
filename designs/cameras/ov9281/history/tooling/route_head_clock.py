"""Connect clock P and reroute the displaced data 1 N path in a new trial.

This establishes connectivity only. Differential routing remains unqualified.
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
    def pad(n):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()==n)
    proposal=route(b,pad('G4'),commit=False,ignore_track_nets=['/CAM_L_D1_N'],max_nodes=300000);assert proposal['result']=='routed';points=proposal['path_xy_mm'];removed=[]
    for t in pool:
        if t.GetNetname()=='/CAM_L_D1_N' and t.IsOnLayer(p.F_Cu) and not isinstance(t,p.PCB_VIA) and any(t.GetEffectiveShape(p.F_Cu).Collide(p.SHAPE_SEGMENT(v(*aa),v(*bb),100000),100000) for aa,bb in zip(points,points[1:])):
            removed.append({'uuid':t.m_Uuid.AsString(),'start':xy(t.GetStart()),'end':xy(t.GetEnd())});b.Remove(t)
    clock=route(b,pad('G4'),max_nodes=300000);assert clock['result']=='routed'
    source=pad('F5');escape=route(b,source,targets=legal_vias(b,source),max_nodes=300000);assert escape['result']=='routed';start=v(*escape['path_xy_mm'][-1]);add_via(b,start,source.GetNetCode())
    connector=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='J201' and q.GetNetname()==source.GetNetname())
    obstruction=next(t for t in pool if t.m_Uuid.AsString()=='656033b8-af64-470d-93ba-f325068ca4af');power_start=obstruction.GetStart();power_end=obstruction.GetEnd();power_changes=[]
    for t in pool:
        if t.GetNetname()!='/M1_AVDD' or t.GetLayer()!=p.B_Cu:continue
        for getter,setter in [(t.GetStart,t.SetStart),(t.GetEnd,t.SetEnd)]:
            q=getter()
            if xy(q) in [xy(power_start),xy(power_end)]:
                moved=v(4.398,q.y/1e6);power_changes.append({'uuid':t.m_Uuid.AsString(),'from':xy(q),'to':xy(moved)});setter(moved)
    end=v(4.75,11.29)
    for item in list(b.GetPads())+list(b.GetTracks()):
        if item.GetNetname()==source.GetNetname():continue
        for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:assert not(item.IsOnLayer(l) and item.GetEffectiveShape(l).Collide(p.SHAPE_CIRCLE(end,200000),100000)),('Terminal via blocked',item.GetNetname())
    for q in b.GetPads():
        for l in [p.F_Cu,p.B_Cu]:assert not(q.IsOnLayer(l) and q.GetEffectiveShape(l).Collide(p.SHAPE_CIRCLE(end,200000),0)), 'Via overlaps a solder pad'
    terminal=route(b,connector,targets=[end],max_nodes=300000);assert terminal['result']=='routed',terminal;add_via(b,end,source.GetNetCode())
    for layer in [p.B_Cu,p.In2_Cu]:
        middle=route(b,source,layer=layer,start=start,targets=[end],max_nodes=300000)
        if middle['result']=='routed':middle['layer']=b.GetLayerName(layer);break
    else:raise AssertionError(middle)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'))
    if (out/'validation.json').exists():(out/'validation.json').rename(out/'source-validation-clock.json')
    p.SaveBoard(str(out/'head.kicad_pcb'),b)
    (out/'clock-routing.json').write_text(json.dumps({'source_head_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(),'removed_D1_N':removed,'clock':clock,'data1_n_escape':escape,'data1_n_terminal':terminal,'data1_n_middle':middle,'AVDD_endpoint_changes':power_changes,'limit':'Connectivity trial: data and clock pairs are not impedance- or delay-qualified.'},indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(out/'checks/clock-drc.json'),str(out/'head.kicad_pcb')],capture_output=True,check=True)
    check=json.loads((out/'checks/clock-drc.json').read_text());print(json.dumps({'unconnected':len(check['unconnected_items']),'violations':[v['type'] for v in check['violations']]},indent=2))
if __name__=='__main__':main()
