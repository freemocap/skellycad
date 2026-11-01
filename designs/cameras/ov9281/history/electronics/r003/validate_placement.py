"""Validate R03 footprint coverage, bounding-box placement and pad-net preservation.

Run with KiCad's bundled Python. Reports routing DRC separately; no waivers.
"""
from pathlib import Path
import json, subprocess, collections, itertools, hashlib
import xml.etree.ElementTree as ET
import pcbnew as p

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'electronics/r03'
GEN=ROOT.parents[1]/'generated/ov9281-r03-validation';GEN.mkdir(exist_ok=True)
CLI='C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'
record=json.loads((OUT/'placement.json').read_text())
xml=ET.parse(OUT/'source-netlist.xml')
expected={}
for net in xml.findall('.//nets/net'):
    for n in net.findall('node'):expected[(n.get('ref'),n.get('pin'))]=net.get('name')
source_refs={c.get('ref') for c in xml.findall('.//components/comp')}
allrefs=[];netboards=collections.defaultdict(set);padchecks=0;summary={}
for name,spec in record['board_specs'].items():
    b=p.LoadBoard(str(OUT/f'{name}.kicad_pcb'));w,h=spec['size'];by_side=collections.defaultdict(list)
    for fp in b.GetFootprints():
        ref=fp.GetReference();allrefs.append(ref)
        bb=fp.GetBoundingBox(False,False);r=[p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())]
        assert r[0]>=.749 and r[1]>=.749 and r[2]<=w-.749 and r[3]<=h-.749,(name,ref,r)
        side='back' if fp.IsFlipped() else 'front';by_side[side].append((ref,r))
        for pad in fp.Pads():
            key=(ref,pad.GetNumber())
            if key in expected:
                assert pad.GetNetname()==expected[key],(key,pad.GetNetname(),expected[key])
                padchecks+=1;netboards[expected[key]].add(name)
    for side,items in by_side.items():
        for (ra,a),(rb,bounds) in itertools.combinations(items,2):
            assert a[2]+.149<=bounds[0] or bounds[2]+.149<=a[0] or a[3]+.149<=bounds[1] or bounds[3]+.149<=a[1],(name,side,ra,rb)
    subprocess.run([CLI,'pcb','drc','--format','json','--output',str(GEN/f'{name}-drc.json'),str(OUT/f'{name}.kicad_pcb')],check=True)
    drc=json.loads((GEN/f'{name}-drc.json').read_text())
    summary[name]={'dimensions_mm':spec['size'],'footprints_by_side':{s:len(i) for s,i in by_side.items()},
                   'drc_violations_by_type':dict(collections.Counter(i['type'] for i in drc['violations'])),
                   'unconnected_items':len(drc['unconnected_items'])}
assert len(allrefs)==len(set(allrefs))
assert set(allrefs)==source_refs-set(record['excluded_logical_symbols'])
combined=p.LoadBoard(str(OUT/'assembly-placement.kicad_pcb'))
assert {f.GetReference() for f in combined.GetFootprints()}==set(allrefs)
assert not list(combined.GetTracks()),'Unexpected routing in placement-only board'
subprocess.run([CLI,'sch','erc','--exit-code-violations','--output',str(GEN/'erc.rpt'),str(OUT/'camera.kicad_sch')],check=True)
for side,layers in [('front','F.Cu,F.Fab,F.CrtYd,Edge.Cuts,Dwgs.User'),('back','B.Cu,B.Fab,B.CrtYd,Edge.Cuts,Dwgs.User')]:
    subprocess.run([CLI,'pcb','export','svg','--layers',layers,'--mode-single','--fit-page-to-board','--exclude-drawing-sheet',
                    '--output',str(OUT/f'{side}.svg'),str(OUT/'assembly-placement.kicad_pcb')],check=True)
report={'status':'Placement-envelope checks pass; routing and fabrication qualification incomplete','footprints':len(allrefs),
        'pad_net_checks':padchecks,'all_placed_pads_preserve_source_nets':True,'same_side_bounding_boxes_do_not_overlap':True,
        'footprint_geometry_inside_outline':True,'schematic_erc_errors':0,'schematic_erc_warnings':0,'boards':summary,
        'interboard_nets':sorted(n for n,bs in netboards.items() if len(bs)>1),
        'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ['head.kicad_pcb','controller.kicad_pcb','assembly-placement.kicad_pcb','camera.kicad_sch']},
        'not_validated':['physical assembly fit','lens or emitter compatibility','flex geometry or contact mapping','trace escape and impedance','thermal performance','final board size']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
