"""Constrain the two-layer free-flex region and export native placement evidence."""
from pathlib import Path
import json,subprocess,hashlib,collections
import pcbnew as p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'generated/three-board-e01';CLI=Path('C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe')
D=json.loads((HERE/'placement.json').read_text());report=json.loads((OUT/'pcb-validation.json').read_text())
for name in ['head-interface','base']:
    folder=OUT/name;path=folder/'camera.kicad_pcb';board=p.LoadBoard(str(path))
    if name=='head-interface' and not list(board.Zones()):
        hw,hh=D['boards']['head']['size'];ix=D['boards']['interface']['origin'][0];lo=(hh-5.5)/2;hi=lo+5.5
        for title,layers,tracks,fills in [('E01 flex: no inner copper',[p.In1_Cu,p.In2_Cu],True,True),('E01 flex: no components or vias',[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu],False,False)]:
            zone=p.ZONE(board);zone.SetIsRuleArea(True);zone.SetZoneName(title);ls=p.LSET()
            for layer in layers:ls.AddLayer(layer)
            zone.SetLayerSet(ls);zone.SetDoNotAllowTracks(tracks);zone.SetDoNotAllowZoneFills(fills);zone.SetDoNotAllowPads(True);zone.SetDoNotAllowVias(True);zone.SetDoNotAllowFootprints(True)
            polygon=zone.Outline();polygon.NewOutline()
            for x,y in [(hw,lo),(ix,lo),(ix,hi),(hw,hi)]:polygon.Append(p.FromMM(100+x),p.FromMM(100+y))
            board.Add(zone)
        p.SaveBoard(str(path),board)
    pro={'board':{'design_settings':{'rules':{'min_clearance':.10,'min_copper_edge_clearance':.20}}},'net_settings':{'classes':[{'name':'Default','clearance':.10,'track_width':.15,'via_diameter':.5,'via_drill':.25}]}}
    (folder/'camera.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
    commands=[['pcb','drc','--format','json','--output',str(folder/'drc.json')],['pcb','export','svg','--layers','F.Cu,F.Fab,Edge.Cuts','--fit-page-to-board','--exclude-drawing-sheet','--mode-single','--output',str(folder/'placement.svg')]]
    for args in commands:
        result=subprocess.run([str(CLI)]+args+[str(path)],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
    drc=json.loads((folder/'drc.json').read_text());summary={k:dict(collections.Counter(v['type'] for v in drc.get(k,[]))) for k in ['violations','unconnected_items','schematic_parity']}
    for item in report['boards']:
        if name in item['file']:item.update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),drc=summary)
    print(name,summary)
report['rules']='0.10 mm clearance / 0.20 mm copper-edge screening values; fabricator approval pending'
report['free_flex']='Inner copper, vias and footprints excluded by native rule areas; global board thickness does not encode the regional flex stack'
(OUT/'pcb-validation.json').write_text(json.dumps(report,indent=2)+'\n')
