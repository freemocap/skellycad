"""Compare native schematic and footprint pins with the selected component contract."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
import pcbnew as p

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parents[1]/'generated/ov9281-r11-electronics'
SPEC=ROOT/'electronics/r11'


def main():
    parts=json.loads((SPEC/'components.json').read_text())['parts']
    root=ET.parse(OUT/'source-netlist.xml').getroot()
    actual={(node.get('ref'),node.get('pin')):net.get('name') for net in root.findall('nets/net') for node in net.findall('node')}
    errors=[];pins=0;fp_report={}
    assert {c.get('ref') for c in root.findall('components/comp')}==set(parts)
    for ref,item in parts.items():
        for pin,want in item['pin_nets'].items():
            got=actual.get((ref,pin));pins+=1
            if want and (got or '').lstrip('/')!=want.lstrip('/'):errors.append([ref,pin,want,got])
            if not want and got and not got.startswith('unconnected-'):errors.append([ref,pin,None,got])
        name=item['footprint'].split(':')[1]
        fp=p.FootprintLoad(str(OUT/'Camera.pretty'),name)
        assert fp is not None,(ref,name)
        numbered={pad.GetNumber() for pad in fp.Pads() if pad.GetNumber()}
        mechanical={'MP'} if ref=='J101' else set()
        if numbered-mechanical!=set(item['pin_nets']):errors.append([ref,'footprint pin numbers',sorted(numbered),sorted(item['pin_nets'])])
        fp_report[ref]={'name':name,'sha256':hashlib.sha256((OUT/'Camera.pretty'/f'{name}.kicad_mod').read_bytes()).hexdigest(),
          'pads':[{'number':pad.GetNumber(),'xy_mm':[p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)],'size_mm':[p.ToMM(pad.GetSize().x),p.ToMM(pad.GetSize().y)],'shape':int(pad.GetShape())} for pad in fp.Pads()]}
    # Independent baseline-node comparison, with explicit package pin remaps.
    baseline=ET.parse(ROOT.parents[1]/'generated/ov9281-r10-review-02/source-netlist.xml').getroot()
    preserved=0
    for net in baseline.findall('nets/net'):
        name=net.get('name')
        if name=='/IR_BASE':name='/IR_GATE'
        if name.startswith('unconnected-'):continue
        for node in net.findall('node'):
            ref,pin=node.get('ref'),node.get('pin')
            if ref not in parts:continue
            if ref in ('U103','U104'):pin={'1':'5','2':'2','3':'4','4':'3','5':'1'}[pin]
            if ref in ('U5','U6','U7'):
                if pin=='4':continue
                pin={'1':'4','2':'2','3':'3','5':'1'}[pin]
            if actual.get((ref,pin),'').lstrip('/')!=name.lstrip('/'):errors.append(['baseline',ref,pin,name,actual.get((ref,pin))])
            preserved+=1
    erc=json.loads((OUT/'erc.json').read_text())
    violations=[v for s in erc['sheets'] for v in s['violations']]
    if violations:errors.append(['ERC',violations])
    report={'status':'pass' if not errors else 'fail','physical_references':len(parts),'pin_assignments_checked':pins,'baseline_signal_nodes_preserved':preserved,
      'erc_violations':len(violations),'errors':errors,'footprints':fp_report,'mechanical_pad_exceptions':{'J101:MP':'Two unconnected solder mounting tabs; no signal pin assignment'},
      'review_scope':'Native pins and netlist checked. New land patterns compared with cited package drawings. Manufacturing tolerances and assembly process require prototype qualification.',
      'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ['camera.kicad_sch','Camera.kicad_sym','source-netlist.xml']}}
    (SPEC/'schematic-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('footprints','sha256')},indent=2))
    assert not errors


if __name__=='__main__':main()
