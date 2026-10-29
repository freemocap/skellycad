"""Validate complete native USB routes, ESD through-routing and references."""
import argparse,json,math,subprocess,sys
from pathlib import Path
import pcbnew as p
import audit_interconnect as audit
from build_r10_planes import connectivity

ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('--inspect',action='store_true');a=ap.parse_args();folder=a.directory.resolve();path=folder/'controller.kicad_pcb';b=p.LoadBoard(str(path));_,src=audit.checked_inputs();old=p.LoadBoard(str(src/'controller.kicad_pcb'))
def padmap(board):return {(q.GetParentFootprint().GetReference(),q.GetNumber()):q.GetNetname() for q in board.GetPads()}
assert padmap(b)==padmap(old)
audit.COPPER=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];g=audit.geometry(b)
report={'sha256':audit.sha(path),'pad_net_checks':len(padmap(b)),'routes':[],'lanes':[],'esd_through_path':[],'reference_gaps':[]}
for pol,resistor in [('DP','R110'),('DM','R109')]:
    chip=audit.route_record(b,g,'controller','/USB_'+pol+'_CHIP',['U101',resistor]);conn=audit.route_record(b,g,'controller','/USB_'+pol,[resistor,'J101'])
    for r in [chip,conn]:
        assert not r['vias'] and set(r['length_by_layer_mm'])=={'F.Cu'}
        assert abs(r['inventory_length_mm']-r['path_length_mm'])<1e-5
        assert all(abs(t['width_mm']-.1)<1e-8 for t in r['segments'])
        report['reference_gaps'] += [{'net':r['net'],**s} for s in r['reference_screen'] if s['gaps']]
        corridor=[]
        for e in r['path']:
            aa=e['from'][1:];zz=e['to'][1:];length=math.dist(aa,zz);count=max(1,math.ceil(length/.025));normal=[(zz[1]-aa[1])/length,-(zz[0]-aa[0])/length]
            for i in range(count):
                point=[aa[k]+(i+.5)/count*(zz[k]-aa[k]) for k in range(2)]
                for shift in [-.225,0,.225]:
                    q=[point[k]+shift*normal[k] for k in range(2)]
                    if not any(z.IsOnLayer(p.In1_Cu) and z.GetNetname()=='GND' and z.HitTestFilledArea(p.In1_Cu,audit.vec(q)) for z in b.Zones()):corridor.append(q)
        r['reference_corridor_uncovered_samples']=corridor
        report['routes'].append(r)
    report['lanes'].append({'polarity':pol,'chip_mm':chip['path_length_mm'],'connector_mm':conn['path_length_mm'],'total_planar_mm':chip['path_length_mm']+conn['path_length_mm']})
    for pad in [q for q in g['pads'] if q['ref']=='U105' and q['net']==conn['net']]:
        distance=min(audit.project(pad['xy'],e['from'][1:],e['to'][1:])[2] for e in conn['path']);assert distance<1e-6
        report['esd_through_path'].append({'pin':pad['number'],'net':conn['net'],'pad_center_distance_mm':distance})
report['difference_mm']=abs(report['lanes'][0]['total_planar_mm']-report['lanes'][1]['total_planar_mm']);assert report['difference_mm']<=.05
report['pin_mapping']=[{'pin':n,'net':net} for n,net in [('1','/USB_VBUS'),('2','/USB_DM'),('3','/USB_DP'),('4','GND')]]
for row in report['pin_mapping']:assert padmap(b)['J101',row['pin']]==row['net']
report['chip_proximity']=audit.pair_screen(report['routes'][0],report['routes'][2]);report['connector_proximity']=audit.pair_screen(report['routes'][1],report['routes'][3])
report['all_pad_groups_connected']=all(len(v)==1 for v in connectivity(b).values())
x=json.loads((folder/'usb-route-refinement.json').read_text())['compensation_x_mm']
probes=[(xx,3.8+i*.1) for xx in [7.184,7.836] for i in range(6)]+[(13.026,3.2+i*.1) for i in range(13)]+[(x-.201,4.25)]
report['ground_guard_probes']=[{'xy':q,'ground':any(z.IsOnLayer(p.F_Cu) and z.GetNetname()=='GND' and z.HitTestFilledArea(p.F_Cu,audit.vec(q)) for z in b.Zones())} for q in probes]
cli=Path(sys.executable).with_name('kicad-cli.exe');drc=folder/'checks/controller-drc.json';subprocess.run([str(cli),'pcb','drc','--format','json','--output',str(drc),str(path)],capture_output=True,check=True);d=json.loads(drc.read_text());report['drc']={'violations':len(d['violations']),'unconnected':len(d['unconnected_items'])}
report['exclusions']='Resistor and ESD package delays, contact travel and external cable; no USB compliance or hardware qualification.'
(folder/'usb-routing-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='routes'},indent=2))
if not a.inspect:assert not report['reference_gaps'] and not any(r['reference_corridor_uncovered_samples'] for r in report['routes']) and all(q['ground'] for q in report['ground_guard_probes']) and not d['violations'] and not d['unconnected_items'] and report['all_pad_groups_connected']
