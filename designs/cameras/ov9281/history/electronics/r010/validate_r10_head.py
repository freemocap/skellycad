"""Validate the repaired sensor head from saved native copper, not route plans."""
from pathlib import Path
import argparse,hashlib,json,math,subprocess,sys
import pcbnew as p
import audit_interconnect as audit
from build_r10_planes import connectivity

ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('--inspect',action='store_true');a=ap.parse_args();folder=a.directory.resolve();path=folder/'head.kicad_pcb'
source,src=audit.checked_inputs();b=p.LoadBoard(str(path));old=p.LoadBoard(str(src/'head.kicad_pcb'))
def padmap(board):return {(q.GetParentFootprint().GetReference(),q.GetNumber()):q.GetNetname() for q in board.GetPads()}
assert padmap(b)==padmap(old);assert b.GetCopperLayerCount()==6
audit.COPPER=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];g=audit.geometry(b)
report={'sha256':audit.sha(path),'pad_net_checks':len(padmap(b)),'source_hashes_verified':True,'scope':'Native geometry and connectivity only; no physical camera or channel qualification','pairs':[],'routes':[]}
for pair in ['D0','CLK','D1']:
    records=[]
    for polarity in ['P','N']:
        net='/CAM_L_'+pair+'_'+polarity;r=audit.route_record(b,g,'head',net,['U1','J201'])
        coverage=[]
        for edge in r['path']:
            if edge['kind']!='trace':continue
            layer={'F.Cu':p.In1_Cu,'B.Cu':p.In4_Cu}[edge['layer']];aa=edge['from'][1:];zz=edge['to'][1:];length=math.dist(aa,zz);count=max(1,math.ceil(length/.025));holes=[]
            for i in range(count):
                point=[aa[k]+(i+.5)/count*(zz[k]-aa[k]) for k in range(2)]
                if not any(z.GetNetname()=='GND' and z.IsOnLayer(layer) and z.HitTestFilledArea(layer,audit.vec(point)) for z in b.Zones()):
                    holes.append({'xy':point,'near_own_transition':any(math.dist(point,v['xy'])<=.45 for v in r['vias'])})
            coverage.append({'uuid':edge['uuid'],'reference_layer':b.GetLayerName(layer),'length_mm':length,'uncovered_mm':length*len(holes)/count,'uncovered_samples':holes})
        r['reference_screen']=coverage;r['reference_gap_mm']=sum(x['uncovered_mm'] for x in coverage);r['reference_supported_mm']=r['path_length_mm']-r['reference_gap_mm']
        r['transition_neighborhood_radius_mm']=.45
        r['unexplained_reference_samples']=sum(not s['near_own_transition'] for x in coverage for s in x['uncovered_samples'])
        assert r['unexplained_reference_samples']==0,(net,'reference void outside transition neighborhood')
        assert all(abs(t['width_mm']-.1)<1e-7 for t in r['segments'])
        records.append(r);report['routes'].append(r)
    pp,nn=records;row={'pair':pair,'p_mm':pp['path_length_mm'],'n_mm':nn['path_length_mm'],'difference_mm':abs(pp['path_length_mm']-nn['path_length_mm']),'layers_match':set(pp['length_by_layer_mm'])==set(nn['length_by_layer_mm']),'via_counts':[len(r['vias']) for r in records],'nearest_mate':audit.pair_screen(pp,nn)}
    assert row['difference_mm']<=.254 and row['layers_match'] and row['via_counts'][0]==row['via_counts'][1]
    assert all(len(v['ground_vias_within_1mm'])>=2 for r in records for v in r['via_return_screen']);report['pairs'].append(row)
planes=[]
for layer in [p.In1_Cu,p.In4_Cu]:
    assert not any(not isinstance(t,p.PCB_VIA) and t.GetNetname()!='GND' and t.GetLayer()==layer for t in b.GetTracks())
    z=next(z for z in b.Zones() if z.GetNetname()=='GND' and z.GetLayer()==layer);poly=z.GetFilledPolysList(layer)
    planes.append({'layer':b.GetLayerName(layer),'connected_polygons':poly.OutlineCount(),'area_mm2':poly.Area()/1e12});assert poly.OutlineCount()==1
report['reference_planes']=planes
cli=Path(sys.executable).with_name('kicad-cli.exe');drc=folder/'checks/head-drc.json';subprocess.run([str(cli),'pcb','drc','--format','json','--output',str(drc),str(path)],capture_output=True,check=True)
d=json.loads(drc.read_text());report['drc']={'violations':len(d['violations']),'unconnected':len(d['unconnected_items'])};report['all_pad_groups_connected']=all(len(groups)==1 for groups in connectivity(b).values())
(folder/'head-routing-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='routes'},indent=2))
if not a.inspect:assert not d['violations'] and not d['unconnected_items'] and report['all_pad_groups_connected']
audit.checked_inputs()
