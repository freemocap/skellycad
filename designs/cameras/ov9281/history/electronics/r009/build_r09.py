"""Derive a new R09 trial: corrected 1.8 V oscillator and default-off IR driver.

Sources: [@epsonSG210STF; @kingbrightAP1608F3C; @nexperiaMMBT3904].
Run with KiCad Python. Preserve R08; reroute head copper after footprint changes.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess
import pcbnew as p
from extract_head import children
import build_r02 as g

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'electronics/r08'
CLI='C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'
OSC='Epson_SG210STF_2.5x2.0mm_R09'
LED='Kingbright_AP1608F3C_R09'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def prop(block,key,value):
    pattern=r'(\(property\s+"'+re.escape(key)+r'"\s+)"[^"\n]*"'
    if re.search(pattern,block):return re.sub(pattern,lambda m:m[1]+json.dumps(value),block,count=1)
    return block[:-1]+f' (property "{key}" {json.dumps(value)} (at 0 0 0) (effects (font (size 1 1)) (hide yes))))'

def footprint(name,body,pads):
    text=f'(footprint "{name}" (version 20260206) (generator "pcbnew") (layer "F.Cu") (attr smd)'
    text+='(property "Reference" "REF**" (at 0 -2.5 0) (layer "F.SilkS") (effects (font (size .6 .6) (thickness .1))))'
    text+=f'(property "Value" "{name}" (at 0 2.5 0) (layer "F.Fab") (effects (font (size .6 .6) (thickness .1))))'
    for layer,extra,width in [('F.Fab',0,.1),('F.CrtYd',.3,.05)]:
        x,y=body[0]/2+extra,body[1]/2+extra
        if layer=='F.CrtYd':
            x=max(x,max(abs(a)+w/2+.25 for _,a,_,w,_ in pads))
            y=max(y,max(abs(a)+h/2+.25 for _,_,a,_,h in pads))
        text+=f'(fp_rect (start {-x} {-y}) (end {x} {y}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))'
    for number,x,y,w,h in pads:
        text+=f'(pad "{number}" smd rect (at {x} {y}) (size {w} {h}) (layers "F.Cu" "F.Mask" "F.Paste"))'
    return text+')\n'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve()
    assert not out.exists()
    baseline=json.loads((SRC/'validation.json').read_text())
    for name,digest in baseline['sha256'].items():assert sha(SRC/name)==digest,name
    shutil.copytree(SRC,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','checks','*.svg','overview.html','README.md','validation.json','inventory.json','*-assembly.kicad_pcb'))
    # Epson page 23, recommended land pattern; top-view pin 1 is lower left.
    (out/'Camera.pretty'/f'{OSC}.kicad_mod').write_text(footprint(OSC,(2.5,2),[(1,-.85,.65,1.1,.9),(2,.85,.65,1.1,.9),(3,.85,-.65,1.1,.9),(4,-.85,-.65,1.1,.9)]))
    # Kingbright page 1: 0.8 mm squares, 0.85 mm pad-edge gap. Pin 1 cathode.
    (out/'Camera.pretty'/f'{LED}.kicad_mod').write_text(footprint(LED,(1.6,.8),[(1,-.825,0,.8,.8),(2,.825,0,.8,.8)]))
    sch=(out/'camera.kicad_sch').read_text(encoding='utf-8')
    y=next(b for b in children(sch) if re.match(r'\(symbol\s',b) and re.search(r'\(property\s+"Reference"\s+"Y1"',b))
    updates={'Value':'SG-210STF 24.0000ML','Footprint':'Camera:'+OSC,'MPN':'X1G004171003100',
             'Manufacturer':'Epson','Datasheet':'https://download.epsondevice.com/td/pdf/app/SG-210STF_en.pdf',
             'Description':'24 MHz CMOS oscillator, 1.6-3.63 V, 2.5 x 2.0 x 0.8 mm, 50 ppm -40 to +85 C'}
    revised=y
    for k,val in updates.items():revised=prop(revised,k,val)
    sch=sch.replace(y,revised)
    # Add labelled circuitry using the established native symbol generator.
    g.LIB.clear();g.PARTS.clear();g.CONNECTIONS.clear();g.FOOTPRINTS.clear()
    parts=[('D201','Device','LED','AP1608F3C',{'1':'IR_K','2':'IR_A1'},'Camera:'+LED),
           ('D202','Device','LED','AP1608F3C',{'1':'IR_K','2':'IR_A2'},'Camera:'+LED),
           ('R201','Device','R','1k 1%',{'1':'+3V3','2':'IR_A1'},'Resistor_SMD:R_0402_1005Metric'),
           ('R202','Device','R','1k 1%',{'1':'+3V3','2':'IR_A2'},'Resistor_SMD:R_0402_1005Metric'),
           ('R203','Device','R','2.2k 1%',{'1':'LED_PWM','2':'IR_BASE'},'Resistor_SMD:R_0402_1005Metric'),
           ('R204','Device','R','100k 1%',{'1':'IR_BASE','2':'GND'},'Resistor_SMD:R_0402_1005Metric'),
           ('Q201','Transistor_BJT','MMBT3904','MMBT3904,215',{'1':'IR_BASE','2':'GND','3':'IR_K'},'Package_TO_SOT_SMD:SOT-23')]
    for i,(ref,lib,sym,val,nets,fp) in enumerate(parts):g.add(ref,lib,sym,val,35+i*75,550,nets,fp)
    for i,block in enumerate(g.PARTS):
        if not block.startswith('(symbol '):continue
        ref=g.prop(block,'Reference')
        mpn={'D201':'AP1608F3C','D202':'AP1608F3C','Q201':'MMBT3904,215',
             'R201':'RC0402FR-071KL','R202':'RC0402FR-071KL','R203':'RC0402FR-072K2L','R204':'RC0402FR-07100KL'}[ref]
        block=prop(block,'MPN',mpn)
        block=prop(block,'Manufacturer','Kingbright' if ref.startswith('D') else 'Nexperia' if ref.startswith('Q') else 'Yageo')
        g.PARTS[i]=block
    existing=next(b for b in children(sch) if b.startswith('(lib_symbols'))
    names=set(re.findall(r'^\(symbol "([^"]+)"',existing,re.M))
    extra=[g.rename(b,'Camera:'+n) for n,b in g.LIB.items() if 'Camera:'+n not in existing]
    sch=sch.replace(existing,existing[:-1]+'\n'+'\n'.join(extra)+'\n)')
    sch=sch.rstrip()[:-1]+'\n'+'\n'.join(g.PARTS)+'\n)\n'
    (out/'camera.kicad_sch').write_text(sch,encoding='utf-8')
    library=(out/'Camera.kicad_sym').read_text(encoding='utf-8').rstrip()
    library=library[:-1]+'\n'+'\n'.join(b for n,b in g.LIB.items() if f'(symbol "{n}"' not in library)+'\n)\n'
    (out/'Camera.kicad_sym').write_text(library,encoding='utf-8')
    for name,path in g.FOOTPRINTS.items():
        target=out/'Camera.pretty'/f'{name}.kicad_mod'
        if not target.exists():shutil.copy2(path,target)
    subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','--output',str(out/'source-netlist.xml'),str(out/'camera.kicad_sch')],check=True)
    # Strip head routing explicitly in the new revision. Retain all R08 files.
    path=out/'head.kicad_pcb';text=path.read_text();oldhead=text
    for b in list(children(text)):
        if re.match(r'\((segment|via)\s',b):text=text.replace(b,'',1)
    path.write_text(text)
    b=p.LoadBoard(str(path))
    old=next(f for f in b.GetFootprints() if f.GetReference()=='Y1')
    oldnets={q.GetNumber():q.GetNetname() for q in old.Pads()};position=old.GetPosition();oldpath=old.GetPath()
    # Remove footprint text before a fresh load to avoid SWIG ownership hazards.
    fpblock=next(x for x in children(text) if x.startswith('(footprint') and re.search(r'\(property\s+"Reference"\s+"Y1"',x))
    text=text.replace(fpblock,'',1);path.write_text(text);b=p.LoadBoard(str(path))
    def put(ref,fp,val,pos,angle,back,assign,path_id):
        f=p.FootprintLoad(str(out/'Camera.pretty'),fp);assert f
        f.SetReference(ref);f.SetValue(val);f.SetFPID(p.LIB_ID('Camera',fp));f.SetPath(path_id)
        b.Add(f)
        if back:f.Flip(v(0,0),False)
        f.SetOrientationDegrees(angle);f.SetPosition(v(*pos))
        f.Reference().SetVisible(False);f.Value().SetVisible(False)
        for q in f.Pads():
            net=assign[q.GetNumber()]
            if not b.FindNet(net):b.Add(p.NETINFO_ITEM(b,net))
            q.SetNet(b.FindNet(net))
        return f
    put('Y1',OSC,updates['Value'],(7.085,3.525),180,True,oldnets,oldpath)
    next(f for f in b.GetFootprints() if f.GetReference()=='C33').SetPosition(v(7.085,1.3))
    placements={'D201':((1.8,1.8),0,False),'D202':((12.2,1.8),180,False),
        'R201':((1.8,3.7),90,False),'R202':((12.2,3.7),90,False),
        'R203':((1.8,6.5),90,False),'R204':((1.8,8.75),90,False),
        'Q201':((12,8.5),90,False)}
    for ref,lib,sym,val,nets,fp in parts:
        pos,angle,back=placements[ref]
        assign={q:(n if n in ['+3V3','GND'] else '/'+n) for q,n in nets.items()}
        put(ref,fp.split(':')[1],val,pos,angle,back,assign,p.KIID_PATH('/'+g.SHEET+'/'+g.uid(ref)))
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    for name in ['head','controller']:
        pro=out/(name+'.kicad_pro');config=json.loads(pro.read_text())
        # Router width follows the existing native minimum; impedance unqualified.
        config['net_settings']['classes'][0]['track_width']=.1 if name=='head' else .15
        pro.write_text(json.dumps(config,indent=2)+'\n')
        board=p.LoadBoard(str(out/(name+'.kicad_pcb')))
        assert p.ExportSpecctraDSN(board,str(out/(name+'.dsn')))
    record={'revision':'OV9281-P4-R09','parent_sha256':baseline['sha256'],
        'units':'mm','oscillator':updates,'added_components':[x[0] for x in parts],
        'head_rerouted_from_scratch':True,'controller_existing_copper_retained_at_input':True,
        'led_branch_resistance_ohm':1000,'led_current_short_bound_mA_each':3.3*1.05/990*1000,
        'status':'Unrouted circuit revision; not a fabrication release'}
    (out/'revision.json').write_text(json.dumps(record,indent=2)+'\n')
    print(out)

if __name__=='__main__':main()
