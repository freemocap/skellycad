"""Read-only native PCB interconnect audit; run with KiCad's Python.

Measurements are geometric screening, not impedance or propagation simulation.
"""
from pathlib import Path
import argparse, hashlib, json, math, statistics
import pcbnew as p
from interconnect_graph import measure, project

ROOT=Path(__file__).resolve().parents[2]
DESIGN=Path(__file__).resolve().parent
OUT=DESIGN/'audits/2026-10-28-interconnect'
COPPER=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
def xy(q):return [q.x/1e6,q.y/1e6]
def vec(q):return p.VECTOR2I(round(q[0]*1e6),round(q[1]*1e6))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def percentile(values,fraction):
    if not values:return None
    return sorted(values)[round((len(values)-1)*fraction)]

def checked_inputs():
    m=json.loads((DESIGN/'routing-review.json').read_text())
    for f in m['files']:assert sha(ROOT/f['path'])==f['sha256'],f['path']
    directory=(ROOT/next(f['path'] for f in m['files'] if f['path'].endswith('/head.kicad_pcb'))).parent
    return m,directory

def geometry(b):
    segments=[];vias=[];pads=[];edges=[];zones=[]
    for t in b.GetTracks():
        common={'uuid':t.m_Uuid.AsString(),'net':t.GetNetname()}
        if isinstance(t,p.PCB_VIA):
            vias.append({**common,'xy':xy(t.GetPosition()),'diameter_mm':t.GetWidth(p.F_Cu)/1e6,'drill_mm':t.GetDrill()/1e6,'layers':[b.GetLayerName(l) for l in COPPER if t.IsOnLayer(l)]})
        else:
            assert not isinstance(t,p.PCB_ARC),'Arc length needs explicit handling'
            segments.append({**common,'a':xy(t.GetStart()),'b':xy(t.GetEnd()),'width_mm':t.GetWidth()/1e6,'layer':b.GetLayerName(t.GetLayer())})
    for fp in b.GetFootprints():
        for q in fp.Pads():pads.append({'uuid':q.m_Uuid.AsString(),'ref':fp.GetReference(),'number':q.GetNumber(),'value':fp.GetValue(),'net':q.GetNetname(),'xy':xy(q.GetPosition()),'size_mm':xy(q.GetSize()),'rotation_deg':q.GetOrientationDegrees(),'layer':b.GetLayerName(fp.GetLayer())})
    for d in b.GetDrawings():
        if d.GetLayer()==p.Edge_Cuts:edges.append({'a':xy(d.GetStart()),'b':xy(d.GetEnd())})
    def contour(chain):return [xy(chain.CPoint(i)) for i in range(chain.PointCount())]
    for z in b.Zones():
        l=z.GetLayer();poly=z.GetFilledPolysList(l)
        zones.append({'net':z.GetNetname(),'layer':b.GetLayerName(l),'polygons':[{'outer':contour(poly.COutline(i)),'holes':[contour(poly.CHole(i,j)) for j in range(poly.HoleCount(i))]} for i in range(poly.OutlineCount())]})
    return dict(segments=segments,vias=vias,pads=pads,edges=edges,zones=zones)

def route_record(b,g,board,net,refs):
    segments=[t for t in g['segments'] if t['net']==net];vias=[t for t in g['vias'] if t['net']==net]
    ports=[]
    for ref in refs:
        candidates=[q for q in g['pads'] if q['ref']==ref and q['net']==net]
        assert len(candidates)==1,(board,net,ref,candidates)
        ports.append(candidates[0])
    native={q.m_Uuid.AsString():q for q in b.GetPads()}
    b.BuildConnectivity();component={q.m_Uuid.AsString() for q in b.GetConnectivity().GetConnectedItems(native[ports[0]['uuid']])}
    assert ports[1]['uuid'] in component,(board,net,'Native connectivity missing')
    # Native route generators ordinarily use pad centers. If a port center is
    # offset, attach at the nearest native trace intersecting that pad and state
    # the offset; never silently equate the inventory with an end-to-end path.
    attach=[]
    for port in ports:
        candidates=[]
        for s in segments:
            if s['layer']!=port['layer']:continue
            u,point,distance=project(port['xy'],s['a'],s['b'])
            shape=p.SHAPE_SEGMENT(vec(s['a']),vec(s['b']),round(s['width_mm']*1e6))
            if native[port['uuid']].GetEffectiveShape(b.GetLayerID(s['layer'])).Collide(shape,0):candidates.append((distance,point))
        assert candidates,(board,net,port)
        distance,point=min(candidates);attach.append({'xy':point,'layer':port['layer'],'center_offset_mm':distance})
    result=measure(segments,vias,attach)
    result.update(board=board,net=net,ports=ports,graph_attachment=attach,native_connected=True,segments=segments,vias=vias)
    ground_vias=[v for v in g['vias'] if v['net']=='GND']
    result['via_return_screen']=[{**v,'ground_vias_within_1mm':[q['uuid'] for q in ground_vias if math.dist(q['xy'],v['xy'])<=1.0],'nearest_ground_via_mm':min((math.dist(q['xy'],v['xy']) for q in ground_vias),default=None)} for v in vias]
    layers={b.GetLayerName(l):l for l in COPPER};ground_zones=[z for z in b.Zones() if z.GetNetname()=='GND']
    refmap={'B.Cu':'F.Cu'} if board=='flex-study' else {'F.Cu':'In1.Cu','In2.Cu':'In1.Cu'}
    coverage=[]
    for edge in result['path']:
        if edge['kind']!='trace':continue
        a=edge['from'][1:];z=edge['to'][1:];length=math.dist(a,z);count=max(1,math.ceil(length/.05));reference=refmap.get(edge['layer']);hits=0;gaps=[];run=None
        for i in range(count):
            fraction=(i+.5)/count;point=[a[k]+fraction*(z[k]-a[k]) for k in range(2)]
            covered=reference is not None and any(q.IsOnLayer(layers[reference]) and q.HitTestFilledArea(layers[reference],vec(point)) for q in ground_zones)
            hits+=int(covered)
            if not covered and run is None:run=i
            if run is not None and (covered or i==count-1):
                last=i if covered else i+1
                gaps.append({'start':[a[k]+run/count*(z[k]-a[k]) for k in range(2)],'end':[a[k]+last/count*(z[k]-a[k]) for k in range(2)],'length_mm':length*(last-run)/count});run=None
        coverage.append({'uuid':edge['uuid'],'layer':edge['layer'],'reference_layer':reference,'length_mm':length,'covered_mm':length*hits/count,'gaps':gaps})
    result['reference_screen']=coverage
    result['reference_supported_mm']=sum(e['covered_mm'] for e in coverage)
    result['reference_gap_mm']=sum(e['length_mm']-e['covered_mm'] for e in coverage)
    return result

def pair_screen(left,right):
    distances=[];no_mate=0.;total=0.
    for edge in left['path']:
        if edge['kind']!='trace':continue
        a=edge['from'][1:];z=edge['to'][1:];length=math.dist(a,z);count=max(1,math.ceil(length/.05));total+=length
        mates=[s for s in right['segments'] if s['layer']==edge['layer']]
        if not mates:no_mate+=length;continue
        for i in range(count):
            point=[a[k]+(i+.5)/count*(z[k]-a[k]) for k in range(2)]
            distances.append(min(project(point,s['a'],s['b'])[2] for s in mates))
    return {'nearest_mate_centerline_mm':{'min':min(distances,default=None),'median':statistics.median(distances) if distances else None,'p95':percentile(distances,.95),'max':max(distances,default=None)},'length_without_any_mate_on_same_layer_mm':no_mate,'scope':'Nearest geometry only; not coupling, corresponding path station or impedance.'}

def mipi():
    manifest,directory=checked_inputs();routes=[];pairs=[];maps={}
    for board,refs in [('head',['U1','J201']),('flex-study',['J302','J301']),('controller',['J102','U101'])]:
        print('Inspecting',board,flush=True)
        b=p.LoadBoard(str(directory/(board+'.kicad_pcb')));g=geometry(b);maps[board]=g
        for pair in ['CLK','D0','D1']:
            print('Measuring',board,pair,flush=True)
            records=[route_record(b,g,board,f'/CAM_L_{pair}_{polarity}',refs) for polarity in ['P','N']];routes.extend(records)
            pairs.append({'board':board,'pair':pair,'p_mm':records[0]['path_length_mm'],'n_mm':records[1]['path_length_mm'],'absolute_difference_mm':abs(records[0]['path_length_mm']-records[1]['path_length_mm']),'p_to_n_proximity':pair_screen(*records),'n_to_p_proximity':pair_screen(*records[::-1]),'layer_sets_match':set(records[0]['length_by_layer_mm'])==set(records[1]['length_by_layer_mm'])})
    totals=[]
    for pair in ['CLK','D0','D1']:
        rows=[x for x in pairs if x['pair']==pair];pp=sum(x['p_mm'] for x in rows);nn=sum(x['n_mm'] for x in rows)
        totals.append({'pair':pair,'p_mm':pp,'n_mm':nn,'difference_mm':abs(pp-nn),'mean_mm':(pp+nn)/2,'intra_pair_screen_pass':abs(pp-nn)<=.254})
    mean_spread=max(x['mean_mm'] for x in totals)-min(x['mean_mm'] for x in totals)
    pinmap=json.loads((directory/'interface.json').read_text())['pins']
    pin_checks=[]
    for board,refs in [('controller',['J102']),('head',['J201']),('flex-study',['J301','J302'])]:
        for ref in refs:
            for number,net in pinmap.items():
                if not net.startswith('/CAM_L_'):continue
                pad=next(q for q in maps[board]['pads'] if q['ref']==ref and q['number']==number);assert pad['net']==net
                pin_checks.append({'board':board,'ref':ref,'pin':number,'net':net,'verified':True})
    report={'date':'2026-10-28','input_files':manifest['files'],'scope':'Planar centerline geometry; no impedance or electrical delay computed','routes':routes,'board_pairs':pairs,'whole_link':totals,'inter_pair_mean_spread_mm':mean_spread,'inter_pair_screen_pass':mean_spread<=.762,'interface_pin_checks':pin_checks,'excluded':'Package/pad travel, connector contacts, solder laps and via barrel lengths; no flex bend model.'}
    (OUT/'mipi.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'board-geometry.json').write_text(json.dumps(maps,separators=(',',':'))+'\n')
    checked_inputs();print(json.dumps({'whole_link':totals,'mean_spread_mm':mean_spread,'native_paths_verified':len(routes),'pin_checks':len(pin_checks)},indent=2))

def usb():
    manifest,directory=checked_inputs();b=p.LoadBoard(str(directory/'controller.kicad_pcb'));g=geometry(b);routes=[];lanes=[]
    for polarity,resistor in [('DP','R110'),('DM','R109')]:
        chip=route_record(b,g,'controller',f'/USB_{polarity}_CHIP',['U101',resistor])
        connector=route_record(b,g,'controller',f'/USB_{polarity}',[resistor,'J101'])
        routes.extend([chip,connector]);lanes.append({'polarity':polarity,'resistor':resistor,'resistor_value':chip['ports'][1]['value'],'chip_segment_mm':chip['path_length_mm'],'connector_segment_mm':connector['path_length_mm'],'planar_total_mm':chip['path_length_mm']+connector['path_length_mm'],'inventory_minus_path_mm':sum(x['inventory_length_mm']-x['path_length_mm'] for x in [chip,connector])})
        # Show the distance from each ESD pad center to the actual through-path.
        esd=[]
        for pad in [q for q in g['pads'] if q['ref']=='U105' and q['net']==connector['net']]:
            distance=min(project(pad['xy'],e['from'][1:],e['to'][1:])[2] for e in connector['path'] if e['kind']=='trace' and e['layer']==pad['layer'])
            esd.append({'pad':pad,'center_distance_to_through_path_mm':distance})
        lanes[-1]['esd_geometry']=esd
    pin_checks=[]
    for number,net in [('1','/USB_VBUS'),('2','/USB_DM'),('3','/USB_DP'),('4','GND')]:
        q=next(x for x in g['pads'] if x['ref']=='J101' and x['number']==number);assert q['net']==net;pin_checks.append({'pin':number,'net':net,'xy':q['xy'],'verified':True})
    report={'date':'2026-10-28','input_files':manifest['files'],'routes':routes,'lanes':lanes,'difference_mm':abs(lanes[0]['planar_total_mm']-lanes[1]['planar_total_mm']),'published_numeric_skew_limit_mm':None,'connector_pin_checks':pin_checks,'chip_pair_proximity':pair_screen(routes[0],routes[2]),'connector_pair_proximity':pair_screen(routes[1],routes[3]),'excluded':'Resistor and ESD package delay, connector contacts and external cable; no USB compliance simulation.'}
    (OUT/'usb.json').write_text(json.dumps(report,indent=2)+'\n');checked_inputs()
    print(json.dumps({'lanes':lanes,'difference_mm':report['difference_mm'],'verified_routes':len(routes),'connector_pins':pin_checks},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--kind',choices=['mipi','usb'],default='mipi');args=parser.parse_args()
    {'mipi':mipi,'usb':usb}[args.kind]()
