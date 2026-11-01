"""Create R10's six-layer plane repair without changing nets or XY geometry."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
import pcbnew as p
from extract_head import children
from audit_interconnect import checked_inputs

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'generated/ov9281-r10-planes'
CLI=Path(sys.executable).with_name('kicad-cli.exe')

def stackup():
    layers=['F.Cu','In1.Cu','In2.Cu','In3.Cu','In4.Cu','B.Cu'];die=[.0705,.065,.060,.065,.0705];er=[4.21,4.6,4.21,4.6,4.21]
    s='(stackup\n'
    for i,name in enumerate(layers):
        s+=f'(layer "{name}" (type "copper") (thickness 0.035))\n'
        if i<5:s+=f'(layer "dielectric {i+1}" (type "'+('core' if i in [1,3] else 'prepreg')+f'") (thickness {die[i]}) (material "PCBWay entry 21 - design basis") (epsilon_r {er[i]}) (loss_tangent 0.02))\n'
    return s+'(copper_finish "ENIG") (dielectric_constraints yes))'

def identity(q):return q.m_Uuid.AsString()

def connectivity(b):
    b.BuildConnectivity();c=b.GetConnectivity();result={}
    for net in {q.GetNetname() for q in b.GetPads() if q.GetNetname()}:
        pads={identity(q):q for q in b.GetPads() if q.GetNetname()==net};pending=set(pads);groups=[]
        while pending:
            uid=next(iter(pending));group=pending&({identity(x) for x in c.GetConnectedItems(pads[uid])}|{uid});pending-=group;groups.append(sorted(group))
        result[net]=sorted(groups)
    return result

def main():
    global OUT
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=OUT);args=ap.parse_args();OUT=args.output.resolve()
    source_record,src=checked_inputs();assert not OUT.exists();OUT.mkdir();(OUT/'checks').mkdir()
    for f in src.iterdir():
        if f.name=='Camera.pretty':shutil.copytree(f,OUT/f.name)
        elif f.is_file() and (f.suffix in ['.kicad_pcb','.kicad_pro','.kicad_dru','.kicad_sch','.kicad_sym'] or f.name in ['fp-lib-table','sym-lib-table','source-netlist.xml','interface.json'] or f.name.startswith('LICENSE')):
            if 'assembly' not in f.name:shutil.copy2(f,OUT/f.name)
    results={}
    for name in ['head','controller']:
        path=OUT/(name+'.kicad_pcb');b=p.LoadBoard(str(path));before=connectivity(b);moves=[]
        b.SetCopperLayerCount(6)
        for t in b.GetTracks():
            if isinstance(t,p.PCB_VIA):continue
            old=t.GetLayer();new={p.In1_Cu:p.In2_Cu,p.In2_Cu:p.In3_Cu}.get(old)
            if new is not None:t.SetLayer(new);moves.append({'uuid':identity(t),'net':t.GetNetname(),'from':b.GetLayerName(old),'to':b.GetLayerName(new)})
        original=list(b.Zones());ground=next(z for z in original if z.GetNetname()=='GND' and z.GetLayer()==p.In1_Cu)
        for z in original:
            if z.GetLayer()==p.In2_Cu:z.SetLayer(p.In3_Cu)
        # Additional reference plane plus copper balancing on the slow layers.
        for layer in [p.In4_Cu,p.In2_Cu]+([] if any(z.GetLayer()==p.In3_Cu for z in b.Zones()) else [p.In3_Cu]):
            z=p.Cast_to_ZONE(ground.Duplicate(False));z.SetLayer(layer);b.Add(z)
        b.GetDesignSettings().SetBoardThickness(p.FromMM(.541))
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
        text=path.read_text();setup=next(x for x in children(text) if x.startswith('(setup'));old=next(x for x in children(setup) if x.startswith('(stackup'));path.write_text(text.replace(old,stackup(),1))
        b=p.LoadBoard(str(path));assert b.GetCopperLayerCount()==6
        assert connectivity(b)==before,(name,'pad connectivity changed')
        assert not any(t.GetNetname()!='GND' and t.GetLayer() in [p.In1_Cu,p.In4_Cu] for t in b.GetTracks() if not isinstance(t,p.PCB_VIA))
        report=OUT/'checks'/(name+'-drc.json')
        subprocess.run([str(CLI),'pcb','drc','--format','json','--output',str(report),str(path)],check=True,capture_output=True)
        drc=json.loads(report.read_text());assert not drc['violations'] and not drc['unconnected_items'],(name,len(drc['violations']),len(drc['unconnected_items']))
        results[name]={'moved_segments':moves,'all_pad_groups_preserved':True,'ground_planes':['In1.Cu','In4.Cu'],'drc_violations':0,'unconnected_items':0,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        print(name,len(moves),'segments moved; native DRC and connectivity passed',flush=True)
    checked_inputs()
    (OUT/'plane-repair.json').write_text(json.dumps({'source':source_record,'boards':results,'scope':'Plane restoration; pair rerouting still pending'},indent=2)+'\n')

if __name__=='__main__':main()
