"""Check saved R06 copper with native KiCad DRC and connectivity, then export review.

Run with KiCad Python and --directory pointing to a newly built R06 directory.
This validates a routing draft, not a fabrication release or working camera.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, re, subprocess
import pcbnew as p
from validate_r05 import netlist, findpad, key, xy, v, connected

ROOT=Path(__file__).resolve().parent
CLI='C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def track_signature(t):
    return (t.GetNetname(),key(t.GetStart()),key(t.GetEnd()),t.GetWidth(),t.GetLayer())
def identity(item): return item.m_Uuid.AsString()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--parent',type=Path,default=ROOT/'electronics/r05')
    ap.add_argument('--revision',default='OV9281-P4-R06')
    args=ap.parse_args();out=args.directory.resolve();src=args.parent.resolve()
    record=json.loads((out/'power-routing.json').read_text())
    r08=json.loads((out/'routing-r08.json').read_text()) if (out/'routing-r08.json').exists() else None
    surface=r08 or (json.loads((out/'surface-routing.json').read_text()) if (out/'surface-routing.json').exists() else None)
    lineage=surface or record
    baseline=json.loads((src/'validation.json').read_text())
    for name,h in lineage['parent_sha256'].items(): assert sha(src/name)==h,('Parent changed',name)
    if r08:
        # Export the changed assembly population directly from the native schematic.
        subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','--output',str(out/'source-netlist.xml'),str(out/'camera.kicad_sch')],check=True)
        assert netlist(out/'source-netlist.xml')==netlist(src/'source-netlist.xml')
        from extract_head import children
        def r8_variant(text):
            for block in children(text):
                if re.match(r'\(symbol\s',block) and re.search(r'\(property\s+"Reference"\s+"R8"',block):
                    assert '(dnp yes)' in block
                    return text.replace(block,block.replace('(dnp yes)','(dnp no)').replace('(in_bom no)','(in_bom yes)'))
            raise AssertionError('R8 missing')
        assert (out/'camera.kicad_sch').read_text()==r8_variant((src/'camera.kicad_sch').read_text())
    else:
        assert sha(out/'camera.kicad_sch')==sha(src/'camera.kicad_sch')
        assert sha(out/'source-netlist.xml')==sha(src/'source-netlist.xml')
    expected=netlist(out/'source-netlist.xml');checked=0;summary={};boards={}
    reports=out/'checks';reports.mkdir(exist_ok=True)
    for name in ['controller','head','flex-study']:
        b=p.LoadBoard(str(out/f'{name}.kicad_pcb'));boards[name]=b;b.BuildConnectivity();c=b.GetConnectivity()
        old=p.LoadBoard(str(src/f'{name}.kicad_pcb'))
        fps={f.GetReference():f for f in b.GetFootprints()}
        assert set(fps)=={f.GetReference() for f in old.GetFootprints()}
        for f in old.GetFootprints():
            new=fps[f.GetReference()]
            assert (key(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer())==(key(new.GetPosition()),new.GetOrientationDegrees(),new.GetLayer())
            def pads(fp): return sorted((q.GetNumber(),q.GetNetname(),key(q.GetPosition()),key(q.GetSize()),q.GetShape(),q.GetLayerSet().FmtHex()) for q in fp.Pads())
            assert pads(f)==pads(new),('Pad geometry or net changed',f.GetReference())
            expected_attributes=f.GetAttributes()
            if r08 and name=='head' and f.GetReference()=='R8':
                expected_attributes &= ~p.FP_DNP & ~p.FP_EXCLUDE_FROM_BOM
            assert new.GetAttributes()==expected_attributes,('Unexpected assembly population change',name,f.GetReference())
        prior=collections.Counter(track_signature(t) for t in old.GetTracks() if not isinstance(t,p.PCB_VIA))
        current=collections.Counter(track_signature(t) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA))
        assert not prior-current,('Existing copper changed',name)
        if surface:
            declared=collections.Counter()
            for route in surface['boards'].get(name,{}).get('routes',[]):
                for a,z in zip(route['points_mm'],route['points_mm'][1:]):
                    if math.dist(a,z)<1e-6:continue
                    declared[(route['net'],key(v(*a)),key(v(*z)),p.FromMM(route['width_mm']),b.GetLayerID(route['layer']))]+=1
            assert current-prior==declared,('Unrecorded or missing added copper',name)
        def via_signature(t):return (t.GetNetname(),key(t.GetPosition()),t.GetWidth(p.F_Cu),t.GetDrillValue())
        old_vias=collections.Counter(via_signature(t) for t in old.GetTracks() if isinstance(t,p.PCB_VIA))
        new_vias=collections.Counter(via_signature(t) for t in b.GetTracks() if isinstance(t,p.PCB_VIA))
        assert not old_vias-new_vias,('Existing vias changed',name)
        if r08:
            declared_vias=collections.Counter((x['net'],key(v(*x['xy_mm'])),p.FromMM(x['diameter_mm']),p.FromMM(x['drill_mm'])) for x in r08['boards'].get(name,{}).get('added_vias',[]))
            assert new_vias-old_vias==declared_vias,('Unrecorded added vias',name)
        elif surface:assert old_vias==new_vias,('Unexpected new vias',name)
        pads_all=[q for f in b.GetFootprints() for q in f.Pads()]
        for f in b.GetFootprints():
            for q in f.Pads():
                k=(f.GetReference(),q.GetNumber())
                if name!='flex-study' and k in expected:
                    assert q.GetNetname()==expected[k];checked+=1
        subprocess.run([CLI,'pcb','drc','--format','json','--output',str(reports/f'{name}-drc.json'),str(out/f'{name}.kicad_pcb')],check=True)
        drc=json.loads((reports/f'{name}-drc.json').read_text())
        counts=collections.Counter(x['type'] for x in drc['violations'])
        assert not (set(counts)-{'track_dangling','via_dangling'}),(name,counts)
        assert counts.get('track_dangling',0)==(6 if name=='controller' else 0),(name,counts)
        if name=='flex-study': assert not counts and not drc['unconnected_items']
        assert len(drc['unconnected_items'])<=baseline['boards'][name]['unconnected_items']
        # Connected-item traversal includes tracks, vias, pads and filled zones.
        # Use physical UUIDs: the P4 exposed pad has multiple lands numbered 105.
        connectivity={}
        for net in sorted({q.GetNetname() for q in pads_all if q.GetNetname()}):
            targets={identity(q):q for q in pads_all if q.GetNetname()==net};remaining=set(targets);sizes=[]
            while remaining:
                uid=next(iter(remaining));reached={identity(x) for x in c.GetConnectedItems(targets[uid])}|{uid}
                found=remaining & reached;sizes.append(len(found));remaining-=found
            connectivity[net]={'pads':len(targets),'connected_pad_groups':sorted(sizes,reverse=True),'complete_on_this_board':len(sizes)==1}
            if surface:
                old_groups=baseline['boards'][name]['net_connectivity'][net]['connected_pad_groups']
                assert len(sizes)<=len(old_groups),('Connectivity regression',name,net,old_groups,sizes)
        zones=[]
        for z in b.Zones():
            count=z.GetFilledPolysList(z.GetLayer()).OutlineCount()
            assert count>0,(name,z.GetNetname(),'empty zone')
            zones.append({'net':z.GetNetname(),'layer':b.GetLayerName(z.GetLayer()),'filled_regions':count})
        if name=='flex-study':
            assert connectivity['GND']['connected_pad_groups']==[18]
            assert zones==[{'net':'GND','layer':'F.Cu','filled_regions':1}]
        # Confirm every claimed pad escape actually reaches its recorded via.
        attachments=record['boards'][name].get('pad_attachments',[])
        vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
        for a in attachments:
            q=next(q for q in fps[a['reference']].Pads() if q.GetNumber()==a['pad'] and math.dist(xy(q.GetPosition()),a['pad_xy_mm'])<1e-5)
            via=next(t for t in vias if t.GetNetname()==a['net'] and math.dist(xy(t.GetPosition()),a['via_xy_mm'])<1e-5)
            assert identity(via) in {identity(x) for x in c.GetConnectedItems(q)},a
        if surface and name in surface['boards']:
            anchors={identity(q):q for q in pads_all+vias}
            for route in surface['boards'][name]['routes']:
                a,z=anchors[route['from_uuid']],anchors[route['to_uuid']]
                assert a.GetNetname()==z.GetNetname()==route['net']
                assert identity(z) in {identity(x) for x in c.GetConnectedItems(a)},route
                if route['width_mm']<.15 and r08:
                    assert name=='head' and route['width_mm']==.1
                elif route['width_mm']<.15:
                    assert name=='head' and route['purpose']=='Local sensor fan-out' and route['width_mm']==.1
                    assert route['length_mm']<=4.0001
                    x0,y0,x1,y1=route['region_mm']
                    assert all(x0<=x<=x1 and y0<=y<=y1 for x,y in route['points_mm'])
        text=(out/f'{name}.kicad_pcb').read_text()
        stack=text.split('(stackup',1)[1].split('(copper_finish',1)[0]
        thickness=sum(float(x) for x in re.findall(r'\(thickness\s+([\d.]+)\)',stack))
        assert abs(thickness-(.1 if name=='flex-study' else .6))<1e-6
        summary[name]={'footprints':len(fps),'vias':len(vias),'pad_to_via_paths_checked':len(attachments),
                       'violations_by_type':dict(counts),'unconnected_items':len(drc['unconnected_items']),
                       'zones':zones,'copper_and_dielectric_thickness_mm':thickness,'net_connectivity':connectivity}
    assert checked==456,checked
    # Keep the preceding physical pin mapping and whole straight flex paths.
    for i in range(1,25):
        connected(boards['flex-study'],'J301',i,'J302',i)
        x,y=xy(findpad(boards['head'],'J201',i).GetPosition())
        fx,fy=xy(findpad(boards['flex-study'],'J302',i).GetPosition())
        assert math.dist((76-y,1.25+x),(fx+29.2,fy+2))<1e-6
        assert abs(xy(findpad(boards['controller'],'J102',i).GetPosition())[1]-(.5+(i-1)*.5+2))<1e-6
    subprocess.run([CLI,'sch','erc','--exit-code-violations','--output',str(reports/'erc.rpt'),str(out/'camera.kicad_sch')],check=True)
    # This combined document is a flat assembly inspection, never a fab input.
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
    assembly_name=args.revision+'-assembly' if surface else 'assembly-interconnect-study'
    p.SaveBoard(str(out/(assembly_name+'.kicad_pcb')),assembly)
    for name in list(boards)+['assembly-interconnect-study']:
        input_name=assembly_name if name=='assembly-interconnect-study' else name
        subprocess.run([CLI,'pcb','export','svg','--layers','F.Cu,B.Cu,F.Fab,Edge.Cuts','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--output',str(out/f'{name}.svg'),str(out/f'{input_name}.kicad_pcb')],check=True)
    for label,layer in [('ground','In1.Cu'),('power','In2.Cu')]:
        subprocess.run([CLI,'pcb','export','svg','--layers',layer+',Edge.Cuts','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--output',str(out/f'controller-{label}.svg'),str(out/'controller.kicad_pcb')],check=True)
    report={'revision':args.revision,'status':'Checked routing draft; incomplete camera; not for fabrication',
            'parent_native_files_unchanged':True,'prior_placements_pads_and_tracks_retained':True,
            'rigid_board_pad_net_checks':checked,'assembled_pin_alignment_checks':24,'flex_contact_paths_verified':24,
            'schematic_erc_errors':0,'schematic_erc_warnings':0,'boards':summary,
            'sha256':{n:sha(out/n) for n in ['controller.kicad_pcb','head.kicad_pcb','flex-study.kicad_pcb','camera.kicad_sch',assembly_name+'.kicad_pcb']}}
    if surface:report['new_surface_paths_verified']=sum(len(d['routes']) for d in surface['boards'].values())
    if r08:
        report['new_paths_verified']=report.pop('new_surface_paths_verified')
        report['assembly_variant_verified']=r08['assembly_variant']
    report['design_rule_snapshot']={n:json.loads((out/(n+'.kicad_pro')).read_text())['board']['design_settings']['rules'] for n in boards}
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:{k:v for k,v in d.items() if k!='net_connectivity'} for n,d in summary.items()},indent=2))

if __name__=='__main__':main()
