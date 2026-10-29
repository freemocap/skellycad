"""Independent native connectivity, regional construction and path audit."""
from pathlib import Path
import collections,hashlib,json,math,subprocess,sys
import pcbnew as p
from routing_r11 import LAYERS,HX,xy,v,launch,legal_layer,groups,uid
from interconnect_graph import measure
from extract_head import children

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'generated/ov9281-r11-electronics';SPEC=ROOT/'designs/eye-camera-ov9281/electronics/r11';CLI=Path(sys.executable).with_name('kicad-cli.exe')

def native_stackup():
    # KiCad does not assign a separate thickness to ENIG. Preserve the real
    # copper/dielectric dimensions; describe the finish/rounding separately.
    s='(stackup\n(layer "F.Mask" (type "Top Solder Mask") (thickness 0.02))\n'
    for i,name in enumerate(['F.Cu','In1.Cu','In2.Cu','In3.Cu','In4.Cu','B.Cu']):
        s+=f'(layer "{name}" (type "copper") (thickness {0.025 if i in [0,5] else 0.018}))\n'
        if i<5:s+=f'(layer "dielectric {i+1}" (type "{ "core" if i==2 else "prepreg"}") (thickness {0.05 if i==2 else 0.02}) (material "C SLIM.flex; permittivity assumed") (epsilon_r {3.4 if i==2 else 3.8}) (loss_tangent 0.02))\n'
    return s+'(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.02)) (copper_finish "ENIG") (dielectric_constraints yes))'

def path(b,net,port_refs):
    pads={(q.GetParentFootprint().GetReference(),q.GetNumber()):q for q in b.GetPads()};segments=[];vias=[]
    for t in b.GetTracks():
        if t.GetNetname()!=net:continue
        if isinstance(t,p.PCB_VIA):vias.append({'uuid':uid(t),'xy':xy(t.GetPosition()),'layers':[b.GetLayerName(l) for l in LAYERS if t.IsOnLayer(l)]})
        else:segments.append({'uuid':uid(t),'a':xy(t.GetStart()),'b':xy(t.GetEnd()),'layer':b.GetLayerName(t.GetLayer())})
    ports=[{'xy':xy(pads[key].GetPosition()),'layer':'F.Cu' if pads[key].IsOnLayer(p.F_Cu) else 'B.Cu'} for key in port_refs]
    return measure(segments,vias,ports)

def main():
    pathfile=OUT/'camera.kicad_pcb';content=pathfile.read_text();setup=next(x for x in children(content) if x.startswith('(setup'))
    old=next((x for x in children(setup) if x.startswith('(stackup')),None)
    content=content.replace(old,native_stackup(),1) if old else content.replace(setup,setup[:-1]+native_stackup()+')',1)
    pathfile.write_text(content,encoding='utf-8')
    b=p.LoadBoard(str(pathfile));parts=json.loads((SPEC/'components.json').read_text())['parts'];errors=[]
    # Native pad assignments are checked independently of routing metadata.
    fp={f.GetReference():f for f in b.GetFootprints()};assert set(fp)==set(parts)
    count=0
    for ref,f in fp.items():
        if not f.GetPath().AsString():errors.append(['no schematic link',ref])
        for pad in f.Pads():
            n=pad.GetNumber();expected=parts[ref]['pin_nets'].get(n) or '';count+=1
            if pad.GetNetname()!=expected:errors.append(['pad net',ref,n,expected,pad.GetNetname()])
        x,y=xy(f.GetPosition())
        if 28<x<HX:errors.append(['component in neck',ref])
    nets={q.GetNetname() for q in b.GetPads() if q.GetNetname()}
    islands={n:len(groups(b,n)) for n in nets};errors += [['disconnected',n,k] for n,k in islands.items() if k!=1]
    stacks=collections.defaultdict(list);via_map={};segments=0
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):
            x,y=xy(t.GetPosition());a,z=sorted([LAYERS.index(t.TopLayer()),LAYERS.index(t.BottomLayer())]);via_map[uid(t)]=t
            if z-a!=1 or abs(p.ToMM(t.GetDrill())-.07)>1e-6 or abs(p.ToMM(t.GetWidth(t.TopLayer()))-.25)>1e-6:errors.append(['via construction',uid(t)])
            if 27<x<HX+1:errors.append(['via transition setback',uid(t),x,y])
            stacks[round(x,6),round(y,6),t.GetNetname()].append((a,z,uid(t)))
        else:
            segments+=1;a,z=xy(t.GetStart()),xy(t.GetEnd());steps=max(1,math.ceil(math.dist(a,z)/.1))
            for i in range(steps+1):
                x=a[0]+(z[0]-a[0])*i/steps
                if not legal_layer(x,t.GetLayer()):errors.append(['absent flex layer',uid(t)]);break
            if p.ToMM(t.GetWidth())<.075-1e-6:errors.append(['undersize trace',uid(t)])
    for key,rows in stacks.items():
        spans=[(a,z) for a,z,_ in rows]
        if len(set(spans))!=len(spans):errors.append(['duplicate via span',key])
    for zone in b.Zones():
        if zone.GetLayer() in [p.In2_Cu,p.In3_Cu]:continue
        poly=zone.GetFilledPolysList(zone.GetLayer())
        for index in range(poly.OutlineCount()):
            outline=poly.Outline(index)
            for i in range(outline.PointCount()):
                a=xy(outline.CPoint(i));z=xy(outline.CPoint((i+1)%outline.PointCount()))
                if min(a[0],z[0])<HX and max(a[0],z[0])>28:errors.append(['zone on absent flex layer',uid(zone)]);break
    # Pair lengths are measured from the saved native copper, not route plans.
    signal={};pair_names=['D0','CLK','D1'];lengths={}
    for name in pair_names:
        lengths[name]={}
        for polarity in ['P','N']:
            net=f'/CAM_L_{name}_{polarity}';ends=[(r,q.GetNumber()) for r in ['U101','U1'] for q in fp[r].Pads() if q.GetNetname()==net]
            m=path(b,net,ends);signal[net]=m;lengths[name][polarity]=m['path_length_mm']
        if abs(lengths[name]['P']-lengths[name]['N'])>.254:errors.append(['CSI pair mismatch',name])
    means=[sum(x.values())/2 for x in lengths.values()]
    if max(means)-min(means)>.762:errors.append(['CSI lane mismatch'])
    usb={}
    for pol,pin,res,jpin in [('P','50','R110','3'),('N','49','R109','2')]:
        a=path(b,'/USB_D'+('P' if pol=='P' else 'M')+'_CHIP',[('U101',pin),(res,'2')])
        z=path(b,'/USB_D'+('P' if pol=='P' else 'M'),[(res,'1'),('J101',jpin)])
        pads={q.GetNumber():q for q in fp[res].Pads()};span=math.dist(xy(pads['1'].GetPosition()),xy(pads['2'].GetPosition()))
        usb[pol]={'chip':a,'connector':z,'resistor_center_span_mm':span,'total_mm':a['path_length_mm']+z['path_length_mm']+span}
    if abs(usb['P']['total_mm']-usb['N']['total_mm'])>.254:errors.append(['USB pair mismatch'])
    # Sample the actual filled reference plane beneath each long trace.
    ground=[z.GetFilledPolysList(p.In3_Cu) for z in b.Zones() if z.GetNetname()=='GND' and z.IsOnLayer(p.In3_Cu)]
    reference={'uniform_samples':0,'launch_samples':0,'missing':[]}
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA) or not(t.GetNetname().startswith('/CAM_L_') or t.GetNetname() in ['/USB_DP_CHIP','/USB_DM_CHIP']):continue
        a,z=xy(t.GetStart()),xy(t.GetEnd());steps=max(1,math.ceil(math.dist(a,z)/.1))
        for i in range(steps+1):
            q=(a[0]+(z[0]-a[0])*i/steps,a[1]+(z[1]-a[1])*i/steps)
            if launch(*q):reference['launch_samples']+=1;continue
            length=math.dist(a,z);nx,ny=(-(z[1]-a[1])/length,(z[0]-a[0])/length) if length else (0,0)
            for offset in [-p.ToMM(t.GetWidth())/2,0,p.ToMM(t.GetWidth())/2]:
                point=(q[0]+nx*offset,q[1]+ny*offset);reference['uniform_samples']+=1
                if not any(poly.Contains(v(*point)) for poly in ground):reference['missing'].append([t.GetNetname(),point])
    if reference['missing']:errors.append(['reference gaps',len(reference['missing'])])
    subprocess.run([str(CLI),'pcb','drc','--format','json','--output',str(OUT/'audit-drc.json'),str(pathfile)],capture_output=True,check=True)
    drc=json.loads((OUT/'audit-drc.json').read_text());dispositions=[]
    for issue in drc['violations']:
        ids=[q['uuid'] for q in issue['items']]
        if issue['type']=='holes_co_located' and all(k in via_map for k in ids):
            rows=[via_map[k] for k in ids];positions={xy(q.GetPosition()) for q in rows};ns={q.GetNetname() for q in rows}
            if len(positions)==1 and len(ns)==1:dispositions.append({'type':issue['type'],'uuids':ids,'reason':'Coincident same-net adjacent laser-via spans. Filled/capped sequential construction; fabricator qualification required.'});continue
        errors.append(['undisposed native DRC',issue])
    if drc['unconnected_items']:errors.append(['native unconnected',drc['unconnected_items']])
    report={'status':'pass' if not errors else 'fail','board_sha256':hashlib.sha256(pathfile.read_bytes()).hexdigest(),'pad_instances_checked':count,'net_count':len(nets),'native_unconnected':len(drc['unconnected_items']),'native_errors':sum(x['severity']=='error' for x in drc['violations']),'native_warnings':len(drc['violations']),'reviewed_stack_warnings':dispositions,'trace_segments':segments,'laser_via_segments':len(via_map),'CSI_lengths_mm':lengths,'CSI_mean_spread_mm':max(means)-min(means),'USB':usb,'reference':reference,'errors':errors,'limitations':['No board-level 3D electromagnetic or transient power-integrity qualification.','Pad launches, USB input/ESD section and isolated tuning lobes are nonuniform structures; 2D impedance results do not qualify them.','Regional layer removal, laser processing, via fill/cap, coverlay, drying openings and stiffener bonding require fabrication review.','Native global stackup lists 0.292 mm copper/dielectric/mask; finished source target is 0.303 mm including surface finish and rounding. Regional flex thickness is 0.166 mm.','No hardware operation, IR eye safety, close focus, USB compliance, thermal or mechanical durability has been demonstrated.']}
    (SPEC/'board-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (SPEC/'native-signal-paths.json').write_text(json.dumps(signal,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['reviewed_stack_warnings','USB']},indent=2));assert not errors

if __name__=='__main__':main()
