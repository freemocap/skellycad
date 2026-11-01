"""Move SCL off the sensor's MIPI escape channels in an isolated routing trial.

Ground-plane continuity and signal-integrity qualification are separate checks.
"""
from pathlib import Path
import argparse,json,shutil,hashlib,subprocess,sys
import pcbnew as p
from route_isolated_head_pads import route
from routing_geometry import add_via
from route_head_dovdd import v,xy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    b=p.LoadBoard(str(src/'head.kicad_pcb'));pool=list(b.GetTracks());removed=[]
    def pad(n):return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()==n)
    escape=v(6.445,6.007);circle=p.SHAPE_CIRCLE(escape,200000);segment=p.SHAPE_SEGMENT(pad('E4').GetPosition(),escape,100000)
    for t in pool:
        remove=False
        if t.GetNetname()=='/M1_CAM_SCL_1V8':
            keep=(isinstance(t,p.PCB_VIA) and xy(t.GetPosition())==(6.5,13.3)) or (not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.F_Cu and min(t.GetStart().y,t.GetEnd().y)>=11000000)
            remove=not keep
        if t.GetNetname() in ['/M1_SID','/M1_VN1'] and t.GetLayer()==p.In2_Cu and not isinstance(t,p.PCB_VIA):remove=True
        if t.GetNetname()=='GND' and t.GetLayer()==p.F_Cu and not isinstance(t,p.PCB_VIA) and (t.GetEffectiveShape(p.F_Cu).Collide(circle,100000) or t.GetEffectiveShape(p.F_Cu).Collide(segment,100000)):remove=True
        if remove:removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'start':xy(t.GetStart()),'end':xy(t.GetEnd())});b.Remove(t)
    for item in list(b.GetPads())+list(b.GetTracks()):
        if item.GetNetname()==pad('E4').GetNetname():continue
        for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]:
            assert not (item.IsOnLayer(layer) and item.GetEffectiveShape(layer).Collide(circle,100000)),('Via blocked',item.GetNetname(),b.GetLayerName(layer))
    results={};results['SCL_F']=route(b,pad('E4'),targets=[escape]);assert results['SCL_F']['result']=='routed';add_via(b,escape,pad('E4').GetNetCode())
    results['SCL_In1']=route(b,pad('E4'),layer=p.In1_Cu,start=escape,targets=[v(6.5,13.3)],max_nodes=300000);assert results['SCL_In1']['result']=='routed',results['SCL_In1']
    for net,start,end in [('/M1_VN1',(3.7624,6.5325),(10.4476,6.3457)),('/M1_SID',(.9282,6.0706),(12.715,8.1028))]:
        source=next(q for q in b.GetPads() if q.GetNetname()==net)
        for layer in [p.In2_Cu,p.B_Cu,p.In1_Cu]:
            result=route(b,source,layer=layer,start=v(*start),targets=[v(*end)],max_nodes=300000)
            if result['result']=='routed':results[net]={'layer':b.GetLayerName(layer),**result};break
        else:raise AssertionError((net,result))
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    results['GND_E5']=route(b,pad('E5'),max_nodes=300000);assert results['GND_E5']['result']=='routed',results['GND_E5']
    results['GND_E3']=route(b,pad('E3'),max_nodes=300000);assert results['GND_E3']['result']=='routed',results['GND_E3']
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'));(out/'validation.json').rename(out/'source-validation-mipi-escape.json');p.SaveBoard(str(out/'head.kicad_pcb'),b)
    report={'source_head_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(),'removed':removed,'routes':results,'limit':'In1 control/bias routes cut the ground pour. Native continuity does not qualify return-path quality.'}
    (out/'mipi-escape-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(out/'checks/escape-drc.json'),str(out/'head.kicad_pcb')],capture_output=True,check=True)
    check=json.loads((out/'checks/escape-drc.json').read_text());print(json.dumps({'unconnected':len(check['unconnected_items']),'violations':[v['type'] for v in check['violations']]},indent=2))
if __name__=='__main__':main()
