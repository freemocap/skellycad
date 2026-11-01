"""Independently check R09 native net correspondence, connectivity and lineage.

Connectivity success is distinct from impedance, component and optical release.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, subprocess
import pcbnew as p
from validate_r05 import netlist, findpad, key, xy, v, connected
ROOT=Path(__file__).resolve().parent
CLI='C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);a=ap.parse_args();out=a.directory.resolve()
    parent=ROOT/'electronics/r08';lineage=json.loads((out/'revision.json').read_text())
    for name,digest in lineage['parent_sha256'].items():assert sha(parent/name)==digest,name
    expected=netlist(out/'source-netlist.xml');oldnets=netlist(parent/'source-netlist.xml')
    assert all(expected.get(k)==n for k,n in oldnets.items()),'Existing schematic nets changed'
    extra=set(expected)-set(oldnets)
    assert len(extra)==15,extra
    reports=out/'checks';reports.mkdir(exist_ok=True);summary={};boards={};checked=0
    for name in ['controller','head','flex-study']:
        b=p.LoadBoard(str(out/(name+'.kicad_pcb')));b.BuildConnectivity();boards[name]=b
        old=p.LoadBoard(str(parent/(name+'.kicad_pcb')))
        fps={f.GetReference():f for f in b.GetFootprints()}
        for f in old.GetFootprints():
            new=fps[f.GetReference()]
            assert new.GetAttributes()==f.GetAttributes(),f.GetReference()
            if f.GetReference() not in ['Y1','C33']:
                assert (key(f.GetPosition()),f.GetLayer(),f.GetOrientationDegrees())==(key(new.GetPosition()),new.GetLayer(),new.GetOrientationDegrees()),f.GetReference()
                assert sorted((q.GetNumber(),key(q.GetPosition()),key(q.GetSize()),q.GetNetname()) for q in f.Pads())==sorted((q.GetNumber(),key(q.GetPosition()),key(q.GetSize()),q.GetNetname()) for q in new.Pads())
        for f in b.GetFootprints():
            for q in f.Pads():
                k=(f.GetReference(),q.GetNumber())
                if name!='flex-study' and k in expected:
                    assert q.GetNetname()==expected[k],(k,q.GetNetname(),expected[k]);checked+=1
                elif name!='flex-study':assert not q.GetNetname(),k
        subprocess.run([CLI,'pcb','drc','--format','json','--output',str(reports/(name+'-drc.json')),str(out/(name+'.kicad_pcb'))],check=True)
        drc=json.loads((reports/(name+'-drc.json')).read_text())
        counts=collections.Counter(x['type'] for x in drc['violations'])
        connectivity={};c=b.GetConnectivity()
        for net in sorted({q.GetNetname() for q in b.GetPads() if q.GetNetname()}):
            targets={q.m_Uuid.AsString():q for q in b.GetPads() if q.GetNetname()==net};remaining=set(targets);sizes=[]
            while remaining:
                uid=next(iter(remaining));found=remaining & ({x.m_Uuid.AsString() for x in c.GetConnectedItems(targets[uid])}|{uid})
                sizes.append(len(found));remaining-=found
            connectivity[net]={'pads':len(targets),'connected_pad_groups':sorted(sizes,reverse=True),'complete_on_this_board':len(sizes)==1}
        highspeed={}
        for stem in ['/CAM_L_CLK_','/CAM_L_D0_','/CAM_L_D1_','/USB_D']:
            entries={}
            for suffix in ['N','P']:
                net=stem+suffix
                if net not in connectivity:continue
                tracks=[t for t in b.GetTracks() if t.GetNetname()==net]
                entries[suffix]={'copper_centerline_sum_mm':sum(p.ToMM(t.GetLength()) for t in tracks if not isinstance(t,p.PCB_VIA)),
                    'vias':sum(isinstance(t,p.PCB_VIA) for t in tracks),
                    'layers':sorted({b.GetLayerName(t.GetLayer()) for t in tracks if not isinstance(t,p.PCB_VIA)})}
            if len(entries)==2:
                entries['sum_difference_mm']=abs(entries['N']['copper_centerline_sum_mm']-entries['P']['copper_centerline_sum_mm'])
                highspeed[stem]=entries
        summary[name]={'footprints':len(fps),'vias':sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks()),
            'unconnected_items':len(drc['unconnected_items']),'violations_by_type':dict(counts),'net_connectivity':connectivity,
            'highspeed_copper_inventory_not_delay_or_impedance':highspeed}
    assert checked==471,checked
    assert not summary['flex-study']['unconnected_items'] and not summary['flex-study']['violations_by_type']
    for i in range(1,25):
        connected(boards['flex-study'],'J301',i,'J302',i)
        x,y=xy(findpad(boards['head'],'J201',i).GetPosition());fx,fy=xy(findpad(boards['flex-study'],'J302',i).GetPosition())
        assert math.dist((76-y,1.25+x),(fx+29.2,fy+2))<1e-6
        assert abs(xy(findpad(boards['controller'],'J102',i).GetPosition())[1]-(.5+(i-1)*.5+2))<1e-6
    subprocess.run([CLI,'sch','erc','--exit-code-violations','--output',str(reports/'erc.rpt'),str(out/'camera.kicad_sch')],check=True)
    assembly=p.BOARD();assembly.SetCopperLayerCount(4);nets={}
    for b in boards.values():
        for q in b.GetPads():
            n=q.GetNetname()
            if n and n not in nets:
                net=p.NETINFO_ITEM(assembly,n);assembly.Add(net);nets[n]=net
    for name,angle,offset in [('controller',0,(50,50)),('head',270,(126,51.25)),('flex-study',0,(79.2,52))]:
        b=boards[name]
        for original in b.GetFootprints():
            assignments={q.GetNumber():q.GetNetname() for q in original.Pads()}
            f=p.FOOTPRINT(original);assembly.Add(f);f.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));f.Move(v(*offset))
            for q in f.Pads():
                if assignments[q.GetNumber()]:q.SetNet(nets[assignments[q.GetNumber()]])
        for original in list(b.GetTracks())+list(b.Zones()):
            item=p.Cast_to_ZONE(original.Duplicate(False)) if isinstance(original,p.ZONE) else original.Duplicate()
            assembly.Add(item);item.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));item.Move(v(*offset));item.SetNet(nets[original.GetNetname()])
        for original in b.GetDrawings():
            if isinstance(original,p.PCB_SHAPE):
                item=original.Duplicate();assembly.Add(item);item.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));item.Move(v(*offset))
    assemblyname='OV9281-P4-R09-assembly';p.SaveBoard(str(out/(assemblyname+'.kicad_pcb')),assembly)
    for name in list(boards)+[assemblyname]:
        svg='assembly-interconnect-study' if name==assemblyname else name
        subprocess.run([CLI,'pcb','export','svg','--layers','F.Cu,B.Cu,F.Fab,Edge.Cuts','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--output',str(out/(svg+'.svg')),str(out/(name+'.kicad_pcb'))],check=True)
    result={'revision':'OV9281-P4-R09','fabrication_ready':False,'parent_native_files_unchanged':True,
        'rigid_board_pad_net_checks':checked,'assembled_pin_alignment_checks':24,'flex_contact_paths_verified':24,
        'schematic_erc_errors':0,'schematic_erc_warnings':0,'boards':summary,
        'sha256':{n:sha(out/n) for n in ['controller.kicad_pcb','head.kicad_pcb','flex-study.kicad_pcb','camera.kicad_sch',assemblyname+'.kicad_pcb']}}
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({n:{k:v for k,v in d.items() if k not in ['net_connectivity','highspeed_copper_inventory_not_delay_or_impedance']} for n,d in summary.items()},indent=2))
if __name__=='__main__':main()
