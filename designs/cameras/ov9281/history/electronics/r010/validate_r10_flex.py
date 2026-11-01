"""Measure the saved flex and the complete three-board MIPI link."""
import argparse,json,math,subprocess,sys
from pathlib import Path
import pcbnew as p
import audit_interconnect as audit
from build_r10_planes import connectivity

ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);a=ap.parse_args();folder=a.directory.resolve()
_,baseline=audit.checked_inputs();path=folder/'flex-study.kicad_pcb';b=p.LoadBoard(str(path));old=p.LoadBoard(str(baseline/'flex-study.kicad_pcb'))
def pads(board):return {(q.GetParentFootprint().GetReference(),q.GetNumber()):(q.GetNetname(),audit.xy(q.GetPosition()),audit.xy(q.GetSize()),q.IsOnLayer(p.B_Cu)) for q in board.GetPads()}
assert pads(b)==pads(old);assert b.GetCopperLayerCount()==2
assert abs(b.GetDesignSettings().GetBoardThickness()/1e6-.168)<1e-8
assert all(len(group)==1 for group in connectivity(b).values())
audit.COPPER=[p.F_Cu,p.B_Cu];g=audit.geometry(b)
assert all(v['net']=='GND' and (v['xy'][0]<=2.5 or v['xy'][0]>=32.8) for v in g['vias'])
plane=next(z for z in b.Zones() if z.GetLayer()==p.F_Cu and z.GetNetname()=='GND');assert plane.GetFilledPolysList(p.F_Cu).OutlineCount()==1
report={'sha256':audit.sha(path),'pad_net_geometry_checks':len(pads(b)),'all_pads_connected':True,'no_vias_in_flexible_span':True,'pairs':[],'routes':[],'whole_link':[]}
for pair in ['D0','CLK','D1']:
    rows=[]
    for polarity in ['P','N']:
        print('Measuring saved flex',pair,polarity,flush=True)
        r=audit.route_record(b,g,'flex-study','/CAM_L_'+pair+'_'+polarity,['J301','J302'])
        assert not r['vias'] and set(r['length_by_layer_mm'])=={'B.Cu'} and abs(r['reference_gap_mm'])<1e-9
        assert abs(r['inventory_length_mm']-r['path_length_mm'])<1e-5
        assert all(abs(s['width_mm']-.1)<1e-8 for s in r['segments'])
        # Check a 0.45 mm-wide reference corridor, not only the centerline.
        failures=0
        for e in r['path']:
            aa=e['from'][1:];zz=e['to'][1:];length=math.dist(aa,zz);count=max(1,math.ceil(length/.05));nx=(zz[1]-aa[1])/length;ny=-(zz[0]-aa[0])/length
            for i in range(count):
                point=[aa[k]+(i+.5)/count*(zz[k]-aa[k]) for k in range(2)]
                for shift in [-.225,0,.225]:failures+=not plane.HitTestFilledArea(p.F_Cu,audit.vec([point[0]+shift*nx,point[1]+shift*ny]))
        assert failures==0;r['reference_corridor_uncovered_samples']=failures;rows.append(r);report['routes'].append(r)
    prox=audit.pair_screen(*rows)
    assert prox['length_without_any_mate_on_same_layer_mm']==0
    assert prox['nearest_mate_centerline_mm']['min']>=.34999
    assert prox['nearest_mate_centerline_mm']['max']<=.50001
    report['pairs'].append({'pair':pair,'p_mm':rows[0]['path_length_mm'],'n_mm':rows[1]['path_length_mm'],'difference_mm':abs(rows[0]['path_length_mm']-rows[1]['path_length_mm']),'nearest_mate':prox})
for name in ['head','controller']:
    data=json.loads((folder/(name+'-routing-validation.json')).read_text());assert audit.sha(folder/(name+'.kicad_pcb'))==data['sha256']
    report[name+'_sha256']=data['sha256']
report['unrelated_pair_spacing']=[]
for first,second in [('D0','CLK'),('CLK','D1'),('D0','D1')]:
    sources=[r for r in report['routes'] if '/CAM_L_'+first+'_' in r['net']]
    targets=[s for r in report['routes'] if '/CAM_L_'+second+'_' in r['net'] for s in r['segments']]
    lower=float('inf')
    for r in sources:
        for s in r['segments']:
            length=math.dist(s['a'],s['b']);count=max(1,math.ceil(length/.1))
            for i in range(count):
                point=[s['a'][k]+(i+.5)/count*(s['b'][k]-s['a'][k]) for k in range(2)]
                nearest=min(audit.project(point,t['a'],t['b'])[2] for t in targets)
                lower=min(lower,nearest-length/(2*count)-.1)
    assert lower>=.3
    report['unrelated_pair_spacing'].append({'pairs':[first,second],'conservative_edge_gap_lower_bound_mm':lower,'required_mm':.3})
constraints=json.loads((Path(__file__).parent/'electronics/r10/constraints.json').read_text())['geometry']
for pair in ['D0','CLK','D1']:
    parts={name:next(x for x in json.loads((folder/(name+'-routing-validation.json')).read_text())['pairs'] if x['pair']==pair) for name in ['head','controller']}
    parts['flex']=next(x for x in report['pairs'] if x['pair']==pair)
    pp=sum(x['p_mm'] for x in parts.values());nn=sum(x['n_mm'] for x in parts.values());vias=sum(x['via_counts'][0] for k,x in parts.items() if k!='flex')
    row={'pair':pair,'p_planar_mm':pp,'n_planar_mm':nn,'difference_mm':abs(pp-nn),'mean_planar_mm':(pp+nn)/2,'through_vias_per_conductor':vias,'estimated_barrel_mm_per_conductor':vias*.506,'intra_pair_pass':abs(pp-nn)<=.254}
    fl=(parts['flex']['p_mm']+parts['flex']['n_mm'])/2;rl=row['mean_planar_mm']-fl
    rd=constraints['mipi_clock_guard' if pair=='CLK' else 'mipi_rigid']['delay_ps_mm'];fd=constraints['mipi_flex_clock_guard' if pair=='CLK' else 'mipi_flex']['delay_ps_mm']
    row['uniform_section_delay_ps']=rl*rd+fl*fd;row['illustrative_via_delay_ps']=row['estimated_barrel_mm_per_conductor']*math.sqrt(4.4)/.299792458;row['illustrative_delay_including_barrels_ps']=row['uniform_section_delay_ps']+row['illustrative_via_delay_ps']
    assert row['intra_pair_pass'];report['whole_link'].append(row)
report['pair_mean_spread_mm']=max(x['mean_planar_mm'] for x in report['whole_link'])-min(x['mean_planar_mm'] for x in report['whole_link']);assert report['pair_mean_spread_mm']<=.762
report['exclusions']='Planar budgets exclude via barrels, package and connector contacts, solder-lap travel and bends; no electrical or physical qualification.'
report['delay_scope']='Uniform-section estimate plus illustrative via transit using Er=4.4. Not a field model of transitions, bends, connectors or packages; no timing qualification.'
report['stiffened_end_regions_x_mm']=[[0,2.5],[32.8,35.3]]
cli=Path(sys.executable).with_name('kicad-cli.exe');drc=folder/'checks/flex-study-drc.json';subprocess.run([str(cli),'pcb','drc','--format','json','--output',str(drc),str(path)],capture_output=True,check=True);d=json.loads(drc.read_text());assert not d['violations'] and not d['unconnected_items'];report['drc']={'violations':0,'unconnected':0}
(folder/'flex-routing-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='routes'},indent=2));audit.checked_inputs()
