"""Check saved R04 geometry, nets and partial routes; export review views.

Run with KiCad Python. Expected six open CSI ends are reported, never waived.
"""
from pathlib import Path
import collections, hashlib, itertools, json, math, re, statistics, subprocess
import xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'electronics/r04';SRC=ROOT/'electronics/r03'
GEN=ROOT.parents[1]/'generated/ov9281-r04-validation';GEN.mkdir(exist_ok=True)
CLI='C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'
record=json.loads((OUT/'routing-study.json').read_text());assert not record['unrouted_requests']
mm=p.FromMM
def v(x,y):return p.VECTOR2I(mm(x),mm(y))
def key(pt):return (pt.x,pt.y)
expected={}
for net in ET.parse(OUT/'source-netlist.xml').findall('.//nets/net'):
    for node in net.findall('node'):expected[(node.get('ref'),node.get('pin'))]=net.get('name')
for name,digest in record['parent_sha256'].items():
    assert hashlib.sha256((SRC/name).read_bytes()).hexdigest()==digest,('Parent changed',name)
for name in ['head.kicad_pcb','camera.kicad_sch']:
    assert (OUT/name).read_bytes()==(SRC/name).read_bytes(),('Unchanged source differs',name)
boards={};refs=[];padcount=0;summary={}
for name,size in [('controller',[32,20]),('head',[14,14])]:
    b=p.LoadBoard(str(OUT/f'{name}.kicad_pcb'));boards[name]=b;by_side=collections.defaultdict(list)
    for f in b.GetFootprints():
        r=f.GetReference();refs.append(r);bb=f.GetBoundingBox(False,False)
        bounds=[p.ToMM(x) for x in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]]
        assert bounds[0]>=.749 and bounds[1]>=.749 and bounds[2]<=size[0]-.749 and bounds[3]<=size[1]-.749,(r,bounds)
        by_side['back' if f.IsFlipped() else 'front'].append((r,bounds))
        for q in f.Pads():
            k=(r,q.GetNumber())
            if k in expected:assert q.GetNetname()==expected[k],k;padcount+=1
    for side,items in by_side.items():
        for (ra,a),(rz,z) in itertools.combinations(items,2):
            assert a[2]+.149<=z[0] or z[2]+.149<=a[0] or a[3]+.149<=z[1] or z[3]+.149<=a[1],(side,ra,rz)
    subprocess.run([CLI,'pcb','drc','--format','json','--output',str(GEN/f'{name}-drc.json'),str(OUT/f'{name}.kicad_pcb')],check=True)
    drc=json.loads((GEN/f'{name}-drc.json').read_text())
    errors=[d for d in drc['violations'] if d['type']!='track_dangling']
    assert not errors,errors
    if name=='controller':
        assert len(drc['violations'])==6
        assert all('/CAM_L_' in str(d['items']) for d in drc['violations'])
    else:assert not drc['violations']
    summary[name]={'dimensions_mm':size,'footprints_by_side':{s:len(x) for s,x in by_side.items()},
                   'violations_by_type':dict(collections.Counter(d['type'] for d in drc['violations'])),
                   'unconnected_items':len(drc['unconnected_items'])}
assert len(refs)==99 and len(set(refs))==99
assert set(refs)=={c.get('ref') for c in ET.parse(OUT/'source-netlist.xml').findall('.//components/comp')}-{'J102','J104'}

# Check each requested connection through actual saved copper endpoints.
b=boards['controller'];fps={f.GetReference():f for f in b.GetFootprints()}
graph=collections.defaultdict(lambda:collections.defaultdict(set))
for t in b.GetTracks():
    a,z=key(t.GetStart()),key(t.GetEnd());g=graph[t.GetNetname()];g[a].add(z);g[z].add(a)
def pad(r,n):return next(q for q in fps[r].Pads() if q.GetNumber()==n)
connections=0
for route in record['routes']:
    m=re.fullmatch(r'(\w+)\.(\w+) to (\w+)\.(\w+)',route['label'])
    if not m:continue
    a,z=pad(m[1],m[2]),pad(m[3],m[4]);assert a.GetNetname()==z.GetNetname()==route['net']
    start,end=key(a.GetPosition()),key(z.GetPosition());seen={start};queue=[start]
    while queue:
        q=queue.pop()
        for n in graph[route['net']][q]-seen:seen.add(n);queue.append(n)
    assert end in seen,('Copper path missing',route['label']);connections+=1

# Same-scale combined view, retaining separate native boards as working files.
assembly=p.BOARD();assembly.SetCopperLayerCount(4);assembly.GetDesignSettings().SetBoardThickness(mm(.6));nets={}
for board in boards.values():
    for f in board.GetFootprints():
        for q in f.Pads():
            n=q.GetNetname()
            if n and n not in nets:item=p.NETINFO_ITEM(assembly,n);assembly.Add(item);nets[n]=item
for name,origin in [('controller',(50,50)),('head',(112,53))]:
    board=boards[name];offset=v(*origin)
    for original in board.GetFootprints():
        f=p.FOOTPRINT(original);assembly.Add(f);f.Move(offset)
        for q in f.Pads():
            if q.GetNetname():q.SetNet(nets[q.GetNetname()])
    for original in board.GetTracks():
        t=p.PCB_TRACK(original);assembly.Add(t);t.Move(offset);t.SetNet(nets[original.GetNetname()])
    for original in board.GetDrawings():
        if isinstance(original,p.PCB_SHAPE):
            d=p.PCB_SHAPE(original);assembly.Add(d);d.Move(offset)
for a,z in [((82,57),(112,57)),((112,57),(112,65)),((112,65),(82,65)),((82,65),(82,57))]:
    d=p.PCB_SHAPE();d.SetShape(p.SHAPE_T_SEGMENT);d.SetStart(v(*a));d.SetEnd(v(*z));d.SetLayer(p.Dwgs_User);d.SetWidth(mm(.06));assembly.Add(d)
assembly.BuildConnectivity();p.SaveBoard(str(OUT/'assembly-routing-study.kicad_pcb'),assembly)
(OUT/'assembly-routing-study.kicad_pro').write_bytes((OUT/'controller.kicad_pro').read_bytes())
for name,file in [('controller',OUT/'controller.kicad_pcb'),('before',SRC/'controller.kicad_pcb'),('assembly',OUT/'assembly-routing-study.kicad_pcb')]:
    for side,layers in [('front','F.Cu,F.Fab,F.CrtYd,Edge.Cuts,Dwgs.User'),('back','B.Cu,B.Fab,B.CrtYd,Edge.Cuts,Dwgs.User')]:
        subprocess.run([CLI,'pcb','export','svg','--layers',layers,'--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--output',str(OUT/f'{name}-{side}.svg'),str(file)],check=True)
subprocess.run([CLI,'sch','erc','--exit-code-violations','--output',str(GEN/'erc.rpt'),str(OUT/'camera.kicad_sch')],check=True)
usb={}
for suffix in ['DM','DP']:
    usb[suffix]=round(sum(r['length_mm'] for r in record['routes'] if r['net'] in ['/USB_'+suffix,'/USB_'+suffix+'_CHIP']),4)
report={'status':'Partial-routing geometry passes; not a fabrication release','footprints':99,'pad_net_checks':padcount,
        'native_copper_paths_verified':connections,'csi_unterminated_escapes':6,'schematic_erc_errors':0,'schematic_erc_warnings':0,
        'same_side_footprint_bounds_do_not_overlap':True,'boards':summary,
        'decoupler_pad_xy_median_mm':{'before':statistics.median(d['before_xy_mm'] for d in record['decoupler_distances']),
                                    'after':statistics.median(d['after_xy_mm'] for d in record['decoupler_distances'])},
        'usb_copper_length_mm':usb,'usb_copper_length_difference_mm':round(abs(usb['DP']-usb['DM']),4),
        'usb_length_note':'Summed trial copper only; not impedance-qualified or tuned; excludes resistor/package electrical delay',
        'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ['controller.kicad_pcb','head.kicad_pcb','camera.kicad_sch','assembly-routing-study.kicad_pcb']}}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
