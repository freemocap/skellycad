"""Build the compact revision's native schematic and package library.

Run with KiCad Python. R10 inputs remain unchanged. [@kicadSchematicFormat;
@winbondW25Q32JvK2026; @tiTlv733R11; @tiTlv62569; @ecs1637b2R11]
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import pcbnew as p
from extract_head import children
import build_r02 as g
from build_r09 import footprint, prop

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BASE = REPO/'generated/ov9281-r10-review-02'
OUT = REPO/'generated/ov9281-r11-electronics'
SPEC = ROOT/'electronics/r11'
CLI = 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'
SHARE = Path('C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/share/kicad')


def tag(block):
    return re.match(r'\(([^\s)]+)',block)[1]


def getprop(block, name):
    m=re.search(r'\(property\s+"'+name+r'"\s+"([^"]*)"',block)
    return m[1] if m else ''


def cloned_symbol(block,key,ref):
    block=re.sub(r'^\(symbol\s+"[^"]+"','(symbol "'+key+'"',block, count=1)
    block=re.sub(r'\(symbol\s+"[^"\n]+(_[0-9]+_[0-9]+)"',lambda m:'(symbol "'+key+m[1]+'"',block)
    remap = ({'1':'5','2':'2','3':'4','4':'3','5':'1'} if ref in ('U103','U104') else
             {'1':'4','2':'2','3':'3','5':'1'} if ref in ('U5','U6','U7') else None)
    for unit in list(children(block)):
        if tag(unit) != 'symbol':continue
        revised=unit
        for pin in children(unit):
            if tag(pin)!='pin':continue
            number=re.search(r'\(number\s+"([^"]+)"',pin)[1]
            if remap:
                if number not in remap:
                    revised=revised.replace(pin,'')
                else:
                    revised=revised.replace(pin,re.sub(r'\(number\s+"[^"]+"','(number "'+remap[number]+'"',pin))
        if re.search(r'_1_1"',unit[:100]):
            extra=None
            if ref in ('U103','U104'):
                extra=('6','NC',7.62,-2.54,180,'no_connect')
            if ref in ('U5','U6','U7'):
                extra=('5','EP',10.16,-7.62,90,'power_in')
            if ref=='U102':
                extra=('9','EP',5.08,-12.7,90,'passive')
            if extra:
                n,name,x,y,a,kind=extra
                revised=revised.rstrip()[:-1]+f'\n(pin {kind} line (at {x} {y} {a}) (length 2.54) (name "{name}" (effects (font (size 1.0 1.0)))) (number "{n}" (effects (font (size 1.0 1.0)))))\n)'
        block=block.replace(unit,revised)
    return block


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'camera.kicad_pcb').exists(), 'Do not rebuild schematic assets beneath routed review'
    (OUT/'Camera.pretty').mkdir(exist_ok=True)
    for existing in (OUT/'Camera.pretty').glob('*.kicad_mod'):
        existing.chmod(0o666)
    for fp in (BASE/'Camera.pretty').glob('*.kicad_mod'):
        shutil.copyfile(fp,OUT/'Camera.pretty'/fp.name)
    spec=json.loads((SPEC/'components.json').read_text(encoding='utf-8'))
    parts=spec['parts']
    # Explicit manufacturer land patterns; millimetres, top view.
    customs={
      'TI_DRL0006A_R11':((1.2,1.6),[(i+1,-.74,y,.67,.3) for i,y in enumerate((-.5,0,.5))]+[(i+4,.74,y,.67,.3) for i,y in enumerate((.5,0,-.5))]),
      'Murata_DFE252012F_R11':((2.5,2),[(1,-1,0,.8,2),(2,1,0,.8,2)]),
      'ECS_ECX1637B2_R11':((2,1.6),[(1,-.675,.575,.85,.75),(2,.675,.575,.85,.75),(3,.675,-.575,.85,.75),(4,-.675,-.575,.85,.75)])}
    for name,(body,pads) in customs.items():
        fptext=footprint(name,body,pads)
        if name=='TI_DRL0006A_R11':
            fptext=fptext.replace('smd rect','smd roundrect').replace('(layers "F.Cu" "F.Mask" "F.Paste"))','(layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.1666667))')
        (OUT/'Camera.pretty'/f'{name}.kicad_mod').write_text(fptext,encoding='utf-8')
    source=(BASE/'camera.kicad_sch').read_text(encoding='utf-8')
    lib=next(b for b in children(source) if tag(b)=='lib_symbols')
    symbols={re.match(r'\(symbol\s+"([^"]+)"',b)[1]:b for b in children(lib)}
    instances={getprop(b,'Reference'):b for b in children(source) if tag(b)=='symbol'}
    g.LIB.clear();g.PARTS.clear();g.FOOTPRINTS.clear();g.CONNECTIONS.clear()
    g.SHEET=g.uid('R11-root')
    # Stable functional locations in a single A1 sheet. All wires are labelled.
    active={
      'U101':(100,105),'U102':(245,80),'Y101':(240,135),'J103':(240,180),
      'U1':(330,65),'Y1':(350,160),
      'U103':(455,70),'U104':(535,70),'U105':(620,70),'J101':(710,70),
      'U5':(440,135),'U6':(530,135),'U7':(620,135),
      'Q101':(455,195),'Q102':(535,195),'Q103':(615,195),
      'Q201':(710,150),'D201':(690,200),'D202':(760,200)}
    passive_index=0
    for ref,item in parts.items():
        sourcekey=re.search(r'\(lib_id\s+"([^"]+)"',instances['Q101' if ref=='Q201' else ref])[1]
        key='R11_'+ref
        g.LIB[key]=cloned_symbol(symbols[sourcekey],key,ref)
        fplib,fpname=item['footprint'].split(':',1)
        if fplib != 'Camera':
            shutil.copyfile(SHARE/'footprints'/f'{fplib}.pretty'/f'{fpname}.kicad_mod',OUT/'Camera.pretty'/f'{fpname}.kicad_mod')
        if ref in active:
            x,y=active[ref]
        else:
            x=35+(passive_index%13)*60
            y=270+(passive_index//13)*40
            passive_index+=1
        before=len(g.PARTS)
        g.add(ref,'R11',ref,item['value'],x,y,{n:net.lstrip('/') if net else None for n,net in item['pin_nets'].items()},'Camera:'+fpname)
        block=g.PARTS[before]
        pincoords=g.pins(key)
        top=max(v[2] for v in pincoords.values())
        left=min(v[1] for v in pincoords.values());right=max(v[1] for v in pincoords.values())
        x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
        for name,yy in [('Reference',y-top-7.62),('Value',y-top-5.08)]:
            old=next(b for b in children(block) if tag(b)=='property' and re.search(r'\(property\s+"'+name+'"',b))
            block=block.replace(old,re.sub(r'\(at [^)]+\)',f'(at {x+(left+right)/2} {yy} 0)',old,count=1))
        for name,value in [('MPN',item['mpn']),('Manufacturer',item['manufacturer']),('Region',item['region'])]:
            block=prop(block,name,value)
        if not item['populated']:block=block.replace('(dnp no)','(dnp yes)')
        g.PARTS[before]=block
    for i,net in enumerate(['USB_VBUS','GND','+3V3','P4_VDD_HP']):
        g.add('#FLG'+str(101+i),'power','PWR_FLAG','PWR_FLAG',40+i*70,565,{'1':net})
    for i,net in enumerate(['GND','+3V3','+1V8','+1V2','+2V8']):
        g.add('#PWR'+str(101+i),'power',net,net,40+i*55,545,{'1':net})
    g.text('R11 / OV9281 + ESP32-P4 / C SLIM.flex / ENGINEERING REVIEW',25,15)
    g.text('Processor, flash and programming',25,30)
    g.text('Sensor and 24 MHz clock',320,30)
    g.text('Power, USB and control translation',435,30)
    g.text('Supporting components / net names are electrical connections',25,235)
    g.text('Continuous flex replaces J102/J201. No external cable is included in the module mass target.',350,555)
    g.text('Optics, fabrication process, thermal behavior and physical camera operation remain unqualified.',350,565)
    libraries='\n'.join(g.rename(b,'Camera:'+key) for key,b in g.LIB.items())
    header=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {g.SHEET}) (paper "A1")\n'
    text=header+'(lib_symbols\n'+libraries+'\n)\n'+'\n'.join(g.PARTS)+'\n)\n'
    # The compact placement uses assembly-layer pin markings; these two
    # protruding silk markers would overlap neighbouring solder openings.
    for name,shape in [('ESP32-P4','fp_circle'),('Winbond_USON-8-2EP_3x4mm_P0.8mm_EP0.2x0.8mm','fp_poly')]:
        path=OUT/'Camera.pretty'/f'{name}.kicad_mod'
        if path.exists():
            content=path.read_text(encoding='utf-8')
            for block in list(children(content)):
                if tag(block)==shape and '"F.SilkS"' in block:content=content.replace(block,'')
            path.write_text(content,encoding='utf-8')
    (OUT/'camera.kicad_sch').write_text(text,encoding='utf-8')
    (OUT/'Camera.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+'\n'.join(g.LIB.values())+'\n)\n',encoding='utf-8')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "Camera") (type "KiCad") (uri "${KIPRJMOD}/Camera.kicad_sym") (options "") (descr "R11 local library")))\n',encoding='utf-8')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Camera") (type "KiCad") (uri "${KIPRJMOD}/Camera.pretty") (options "") (descr "R11 local footprints")))\n',encoding='utf-8')
    if not (OUT/'camera.kicad_pro').exists():
        (OUT/'camera.kicad_pro').write_text('{}\n',encoding='utf-8')
    for name in ('LICENSE-Antmicro','LICENSE-Espressif-library.md'):
        if (BASE/name).exists():shutil.copy2(BASE/name,OUT/name)
    (OUT/'expected-connections.json').write_text(json.dumps(g.CONNECTIONS,indent=2)+'\n',encoding='utf-8')
    for args in [
        ['sch','export','netlist','--format','kicadxml','--output',str(OUT/'source-netlist.xml'),str(OUT/'camera.kicad_sch')],
        ['sch','erc','--format','json','--output',str(OUT/'erc.json'),str(OUT/'camera.kicad_sch')],
        ['sch','export','svg','--output',str(OUT/'schematic-svg'),str(OUT/'camera.kicad_sch')]]:
        subprocess.run([CLI]+args,check=True)
    print(OUT)


if __name__=='__main__':main()
