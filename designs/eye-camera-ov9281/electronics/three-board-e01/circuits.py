"""E01 connected circuits; reuse licensed R11 symbols without modifying R11.

[@ti953A01; @ti954A01; @tiTps2553E01; @esp32P4HardwareGuide]
"""
from pathlib import Path
import sys,json,copy,re,shutil,subprocess,uuid,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CAM=HERE.parents[1]
sys.path.insert(0,str(CAM))
import build_r02 as g
from extract_head import children
from build_r09 import footprint
CLI=Path('C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe')
SHARE=CLI.parent.parent/'share/kicad';BASE=ROOT/'generated/ov9281-r11-electronics';OUT=ROOT/'generated/three-board-e01'
R11=json.loads((CAM/'electronics/r11/components.json').read_text(encoding='utf-8'))['parts']
src=(BASE/'camera.kicad_sch').read_text(encoding='utf-8')
lib=next(b for b in children(src) if g.tag(b)=='lib_symbols')
LIB={re.match(r'\(symbol\s+"([^"]+)"',b)[1]:b for b in children(lib)}
INST={g.prop(b,'Reference'):b for b in children(src) if g.tag(b)=='symbol'}

def inherited(ref,region=None,newref=None,netmap=None):
    p=copy.deepcopy(R11[ref]);p['source_ref']=ref;p['reference']=newref or ref
    if region:p['region']=region
    p['pin_nets']={n:((netmap or {}).get(v.lstrip('/'),v.lstrip('/')) if v else None) for n,v in p['pin_nets'].items()}
    return p

def symbol(key,pins):
    # Numbered electrical pins, arranged in two columns with 2.54 mm pitch.
    half=(len(pins)+1)//2;top=(half-1)*1.27;bodyy=top+2.54;bodyx=17.78
    b=f'(symbol "{key}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 0 0) (effects (font (size 1.27 1.27)))) (property "Value" "{key}" (at 0 0 0) (effects (font (size 1 1)))) (symbol "{key}_0_1" (rectangle (start {-bodyx} {bodyy}) (end {bodyx} {-bodyy}) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "{key}_1_1" '
    for i,(n,name,kind) in enumerate(pins):
        right=i>=half;j=i-half if right else i;x=20.32 if right else -20.32;y=top-j*2.54;angle=180 if right else 0
        b+=f'(pin {kind} line (at {x} {y} {angle}) (length 2.54) (name "{name}" (effects (font (size 0.9 0.9)))) (number "{n}" (effects (font (size 0.9 0.9)))))'
    return b+'))'

def part(ref,value,mpn,region,nets,pins,fp,body,mass,sources):
    return dict(reference=ref,value=value,mpn=mpn,manufacturer='See manufacturer part number',region=region,
        pin_nets={str(k):v for k,v in nets.items()},pins=[(str(n),name,kind) for n,name,kind in pins],
        footprint=fp,body_mm=body,height_max_mm=body[2],mass_g=[mass*.7,mass,mass*1.5],
        populated=True,sources=sources,mass_evidence='Engineering package estimate; not weighed')

class Circuit:
    def __init__(self,name):self.name=name;self.parts={};self.count={k:(600 if name=='base' else 400) for k in ['C','R','FB','TP']}
    def put(self,p):
        assert p['reference'] not in self.parts,p['reference'];self.parts[p['reference']]=p;return p['reference']
    def clone(self,ref,region=None,newref=None,netmap=None):return self.put(inherited(ref,region,newref,netmap))
    def passive(self,kind,value,a,b,region,mpn=None):
        self.count[kind]+=1;ref=kind+str(self.count[kind]);template={'C':'C9','R':'R102','FB':'L1'}[kind]
        p=inherited(template,region,ref);p['pin_nets']={'1':a,'2':b};p['value']=value
        if kind=='C':
            choices={'100n':('C9',None),'10n':('C131',None),'1u':('C12',None),'4.7u':('C105',None),'10u':('C123','GRM21BR61A106KE19L'),'22u':('C123',None),'22p':('C107',None),'16p':('C101',None)}
            template,alt=choices.get(value,('C9',None));p=inherited(template,region,ref);p.update(value=value,pin_nets={'1':a,'2':b})
            if alt:p['mpn']=alt
            if value=='22n':p['mpn']='GRM155R71H223KA12D'
            if value=='100n/50V':p['mpn']='GRM155R71H104KE14D';p['rated_voltage_V']=50;p['sources']=['ti953A01','murataMlccList2025']
        elif kind=='R':
            code=(value[:-1].replace('.','K') if '.' in value else value[:-1]+'K') if value.endswith('k') else value.replace('.','R')
            p['mpn']='RC0402FR-07'+code+'L'
            # Preserve manufacturer codes for reused values; unfamiliar values remain explicit candidates.
            match=next((v for v in R11.values() if v['reference'].startswith('R') and v['value']==value),None)
            if match:p['mpn']=match['mpn']
            p['sources']=['yageoRc0402R11'];p['tolerance_percent']=1
        else:
            p.update(mpn='BLM18SG121TN1D',value='120R@100MHz',footprint='Inductor_SMD:L_0603_1608Metric',height_max_mm=.95,mass_g=[.002,.003,.005],sources=['murataFerritesE01'])
        if mpn:p['mpn']=mpn
        return self.put(p)
    def cap(self,v,rail,region):return self.passive('C',v,rail,'GND',region)
    def esd(self,ref,net,region):
        return self.put(part(ref,'TPD1E01B04 / 0.20pF typ','TPD1E01B04DPYR',region,{'1':net,'2':'GND'},[('1','IO','passive'),('2','IO_GND','passive')],'Diode_SMD:D_0402_1005Metric',[1,.6,.4],.0007,['tiTpd1E01B04E01']))
    def resistor(self,v,a,b,region):return self.passive('R',v,a,b,region)
    def buck(self,ref,vin,vout,en,region,upper,lower='100k'):
        p=inherited('U104',region,ref);p['pin_nets']={'1':ref+'_FB','2':'GND','3':vin,'4':ref+'_SW','5':en,'6':None};self.put(p)
        p=inherited('L102',region,'L'+ref[1:]);p['pin_nets']={'1':ref+'_SW','2':vout};self.put(p)
        self.resistor(upper,vout,ref+'_FB',region);self.resistor(lower,ref+'_FB','GND',region)
        self.cap('4.7u',vin,region);self.cap('22u',vout,region)

SER_NAMES={1:'CSI_D1P',2:'CSI_D1N',3:'CSI_D0P',4:'CSI_D0N',5:'CSI_CLKP',6:'CSI_CLKN',7:'RES0',8:'PDB',9:'LPF1',10:'VDDPLL_CAP',11:'VDDPLL',12:'LPF2',13:'DOUT_N',14:'DOUT_P',15:'VDDDRV_CAP',16:'VDDDRV',17:'GPIO0',18:'GPIO1',19:'CLK_OUT_IDX',20:'CLKIN',21:'MODE',22:'RES1',23:'I2C_SDA',24:'I2C_SCL',25:'VDDD',26:'VDDD_CAP',27:'GPIO2',28:'GPIO3',29:'CSI_D3P',30:'CSI_D3N',31:'CSI_D2P',32:'CSI_D2N',33:'EP'}
def head():
    c=Circuit('head-interface');maphead={'+1V8':'H1V8','+1V2':'H1V2','+2V8':'H2V8','+3V3':'H5V','LED_PWM':'SER_LED_PWM'}
    for ref,p in R11.items():
        if p['region']=='head':c.clone(ref,netmap=maphead)
    for ref in ('R201','R202'):
        c.parts[ref].update(value='2.2k',mpn=R11['R203']['mpn'])
    # Keep the two emitters at the lens; put their switch/resistors on the interface island.
    for ref in ('R201','R202','R203','R204','Q201'):c.parts[ref]['region']='interface'
    # Reset is now driven in the sensor's 1.8 V domain; low holds sensor reset.
    c.resistor('10k','CAM_NRST_1V8','GND','head')
    c.resistor('10k','M1_VSYNC_1V8_M','GND','head')
    c.resistor('4.7k','H1V8','M1_CAM_SCL_1V8','interface');c.resistor('4.7k','H1V8','M1_CAM_SDA_1V8','interface')
    nets={1:'CAM_L_D1_P',2:'CAM_L_D1_N',3:'CAM_L_D0_P',4:'CAM_L_D0_N',5:'CAM_L_CLK_P',6:'CAM_L_CLK_N',7:'GND',8:'SER_PDB',9:'SER_LPF1',10:'SER_PLL_CAP',11:'SER_VDDPLL',12:'SER_LPF2',13:'SER_DOUT_N',14:'SER_DOUT_P',15:'SER_DRV_CAP',16:'SER_VDDDRV',17:'CAM_NRST_1V8',18:'SER_LED_PWM',19:'SER_IDX',20:None,21:'SER_MODE',22:None,23:'M1_CAM_SDA_1V8',24:'M1_CAM_SCL_1V8',25:'SER_VDDD',26:'SER_D_CAP',27:None,28:None,29:None,30:None,31:None,32:None,33:'GND'}
    pins=[]
    for n,name in SER_NAMES.items():
        kind='power_in' if n in (11,16,25,33) else 'power_out' if n in (10,15,26) else 'bidirectional' if n in (13,14,17,18,19,23,24,27,28) else 'passive' if n in (9,12) else 'input'
        pins.append((n,name,kind))
    c.put(part('U201','DS90UB953-Q1','DS90UB953TRHBRQ1','interface',nets,pins,'Camera:TI_RHB0032P_E01',[5,5,1],.05,['ti953A01']))
    for pinrail in ['SER_VDDD','SER_VDDDRV','SER_VDDPLL']:
        c.passive('FB','120R@100MHz','H1V8',pinrail,'interface');c.cap('1u',pinrail,'interface');c.cap('10n',pinrail,'interface')
    for rail in ['SER_PLL_CAP','SER_DRV_CAP','SER_D_CAP']:
        for value in ['10u','100n','10n']:c.cap(value,rail,'interface')
    c.passive('C','22n','SER_LPF1','SER_VDDPLL','interface');c.cap('100n','SER_LPF2','interface')
    c.resistor('10k','SER_MODE','GND','interface');c.resistor('40.2k','SER_IDX','GND','interface')
    c.resistor('100k','H1V8','SER_PDB','interface');c.cap('100n','SER_PDB','interface')
    c.passive('C','100n/50V','SER_DOUT_P','LINK_P','interface');c.passive('C','100n/50V','SER_DOUT_N','LINK_N','interface')
    c.buck('U202','H5V','H1V8','H5V','interface','200k')
    for ref,vin,out in [('U6','H1V8','H1V2'),('U7','H5V','H2V8')]:
        p=inherited(ref,'interface');p['pin_nets']={'1':out,'2':'GND','3':vin,'4':vin,'5':'GND'};c.put(p);c.cap('1u',out,'interface');c.cap('1u',vin,'interface')
    p=inherited('J101','interface','J201');p.update(value='TETHER: 1=5V 2=N 3=P 4=GND; NOT USB',pin_nets={'1':'H5V','2':'LINK_N','3':'LINK_P','4':'GND'});c.put(p)
    c.put(part('TP201','Shield termination','PCB solder land','interface',{'1':'GND'},[('1','SHIELD','passive')],'TestPoint:TestPoint_Pad_1.0x1.0mm',[1,1,.02],0,[]))
    c.esd('D203','LINK_P','interface');c.esd('D204','LINK_N','interface')
    return c

def qfn(name,count,body,ep,padside,padlength,padwidth):
    per=count//4;pads=[]
    for i in range(per):
        t=-(per-1)*.25+i*.5
        pads.extend([(i+1,-padside,t,padlength,padwidth),(per+i+1,t,padside,padwidth,padlength),(2*per+i+1,padside,-t,padlength,padwidth),(3*per+i+1,-t,-padside,padwidth,padlength)])
    pads.append((count+1,0,0,ep,ep))
    content=footprint(name,(body,body),pads)
    # Exposed copper land needs a segmented paste stencil, not 100% aperture.
    blocks=list(children(content))
    for b in blocks:
        if g.tag(b)=='pad' and re.match(r'\(pad "?'+str(count+1)+r'"?\s',b):content=content.replace(b,b.replace(' "F.Paste"',''))
    opening=ep*.35
    for x in (-ep*.24,ep*.24):
        for y in (-ep*.24,ep*.24):content=content.rstrip()[:-1]+f'\n(fp_rect (start {x-opening/2} {y-opening/2}) (end {x+opening/2} {y+opening/2}) (stroke (width 0) (type solid)) (fill solid) (layer "F.Paste"))\n)'
    return content

RX_NAMES={1:'SDA',2:'SCL',3:'VDD11_D',4:'XOUT',5:'XIN_REFCLK',6:'BISTEN',7:'VDDIO',8:'GPIO6',9:'GPIO5',10:'GPIO4',11:'CSI_CLK0N',12:'CSI_CLK0P',13:'CSI_D0N',14:'CSI_D0P',15:'CSI_D1N',16:'CSI_D1P',17:'VDD18_CSI',18:'CSI_CLK1N',19:'CSI_CLK1P',20:'VDD11_CSI',21:'CSI_D2N',22:'CSI_D2P',23:'CSI_D3N',24:'CSI_D3P',25:'GPIO3_INTB',26:'GPIO2',27:'GPIO1',28:'GPIO0',29:'VDDIO',30:'PDB',31:'VDD18_FPD1',32:'RIN1P',33:'RIN1N',34:'VDD11_FPD1',35:'IDX',36:'VDD18_P1',37:'MODE',38:'CMLOUTP',39:'CMLOUTN',40:'VDD18_FPD0',41:'RIN0P',42:'RIN0N',43:'VDD11_FPD0',44:'RES',45:'VDD18_P0',46:'VDD_SEL',47:'PASS',48:'LOCK',49:'EP'}
def base():
    c=Circuit('base');omit={'C1','C2','C3','C4','C5','C6','U5','U6','U7','Q101','Q102','Q103','R112','R114','R116','R117','R118'}
    remap={'CAM_SCL_3V3':'BASE_SCL','CAM_SDA_3V3':'BASE_SDA','CAM_RESET_ASSERT':'RX_PDB','LED_PWM':'TETHER_EN'}
    for ref,p in R11.items():
        if p['region']=='controller' and ref not in omit:c.clone(ref,'base',netmap=remap)
    c.parts['U104']['pin_nets'].update({'3':'B5V','5':'B5V'})
    c.parts['U101']['pin_nets'].update({'10':'RX_CLK_DISABLE','11':'RX_LOCK','12':'RX_PASS','13':'TETHER_FAULT_N','14':'RX_INT_N','17':'USB_PRESENT_N'})
    c.resistor('100k','RX_PDB','GND','base');c.resistor('100k','TETHER_EN','GND','base');c.cap('4.7u','B5V','base')
    nets={n:None for n in RX_NAMES};nets.update({1:'BASE_SDA',2:'BASE_SCL',3:'RX_D_CAP',5:'RX_REFCLK',6:'GND',7:'+3V3',11:'CAM_L_CLK_N',12:'CAM_L_CLK_P',13:'CAM_L_D0_N',14:'CAM_L_D0_P',15:'CAM_L_D1_N',16:'CAM_L_D1_P',17:'RX_VDD18_CSI',20:'RX_CSI_CAP',25:'RX_INT_N',29:'+3V3',30:'RX_PDB',31:'RX_VDD18_FPD',34:'RX_FPD1_CAP',35:'RX_IDX',36:'RX_VDD18_P',37:'RX_MODE',40:'RX_VDD18_FPD',41:'RX_IN_P',42:'RX_IN_N',43:'RX_FPD0_CAP',44:'GND',45:'RX_VDD18_P',46:'GND',47:'RX_PASS',48:'RX_LOCK',49:'GND'})
    pins=[]
    for n,name in RX_NAMES.items():
        kind='power_in' if n in (7,17,29,31,36,40,45,49) else 'power_out' if n in (3,20,34,43) else 'bidirectional' if n in (1,2,8,9,10,25,26,27,28,41,42) else 'output' if n in (4,11,12,13,14,15,16,18,19,21,22,23,24,38,39,47,48) else 'input'
        pins.append((n,name,kind))
    c.put(part('U301','DS90UB954-Q1 / internal LDOs','DS90UB954TRGZRQ1','base',nets,pins,'Camera:TI_RGZ0048B_E01',[7,7,1],.10,['ti954A01']))
    c.buck('U302','B5V','RX1V8','B5V','base','200k')
    for rail in ['RX_VDD18_CSI','RX_VDD18_FPD','RX_VDD18_P']:c.passive('FB','120R@100MHz','RX1V8',rail,'base')
    for _ in range(2):
        c.cap('1u','+3V3','base');c.cap('10n','+3V3','base')
        c.cap('10u','RX_VDD18_FPD','base');c.cap('100n','RX_VDD18_FPD','base');c.cap('10n','RX_VDD18_P','base')
    c.cap('10u','RX_VDD18_P','base');c.cap('1u','RX_VDD18_CSI','base');c.cap('10n','RX_VDD18_CSI','base')
    for rail in ['RX_D_CAP','RX_CSI_CAP','RX_FPD0_CAP','RX_FPD1_CAP']:c.cap('4.7u',rail,'base');c.cap('100n',rail,'base')
    c.resistor('10k','RX_IDX','GND','base');c.resistor('78.7k','RX1V8','RX_MODE','base');c.resistor('97.6k','RX_MODE','GND','base')
    c.resistor('4.7k','+3V3','RX_INT_N','base')
    c.passive('C','100n/50V','LINK_P','RX_IN_P','base');c.passive('C','100n/50V','LINK_N','RX_IN_N','base')
    p=inherited('Y1','base','Y301');p.update(value='SG-210STF 25.0000ML / 1.8V',mpn='SG-210STF 25.0000ML',pin_nets={'1':'RX_CLK_OE','2':'GND','3':'RX_REFCLK','4':'RX1V8'},sources=['epsonSG210STF','epson25E01']);c.put(p)
    c.cap('100n','RX1V8','base');p=inherited('Q103','base','Q301');p['pin_nets']={'1':'RX_CLK_DISABLE','2':'GND','3':'RX_CLK_OE'};c.put(p)
    c.resistor('10k','+3V3','RX_CLK_DISABLE','base');c.resistor('10k','RX1V8','RX_CLK_OE','base')
    # WSON pin numbers differ from SOT-23; explicit datasheet table 5-1 mapping.
    pins=[(1,'OUT','power_out'),(2,'ILIM','passive'),(3,'FAULT_N','open_collector'),(4,'EN','input'),(5,'GND','power_in'),(6,'IN','power_in'),(7,'EP','power_in')]
    c.put(part('U303','TPS2553 / current-limited head power','TPS2553DRVR','base',{1:'TETHER_5V',2:'TETHER_ILIM',3:'TETHER_FAULT_N',4:'TETHER_EN',5:'GND',6:'B5V',7:'GND'},pins,'Camera:TI_DRV0006A_E01',[2,2,.8],.006,['tiTps2553E01']))
    c.resistor('80.6k','TETHER_ILIM','GND','base');c.resistor('10k','+3V3','TETHER_FAULT_N','base');c.cap('1u','B5V','base');c.cap('1u','TETHER_5V','base')
    p=inherited('J101','base','J301');p.update(value='TETHER: 1=5V 2=N 3=P 4=GND; NOT USB',pin_nets={'1':'TETHER_5V','2':'LINK_N','3':'LINK_P','4':'GND'});c.put(p)
    for ref,net,label in [('TP301','GND','Tether shield'),('TP302','B5V','REGULATED 5V INPUT'),('TP303','GND','POWER RETURN')]:
        c.put(part(ref,label,'PCB solder land','base',{'1':net},[('1',label,'passive')],'TestPoint:TestPoint_Pad_1.0x1.0mm',[1,1,.02],0,[]))
    # Detect USB VBUS through a FET, avoiding a divider feeding an unpowered MCU input.
    p=inherited('Q103','base','Q302');p['pin_nets']={'1':'USB_VBUS_GATE','2':'GND','3':'USB_PRESENT_N'};c.put(p)
    c.resistor('100k','USB_VBUS','USB_VBUS_GATE','base');c.resistor('100k','USB_VBUS_GATE','GND','base');c.resistor('10k','+3V3','USB_PRESENT_N','base')
    c.esd('D301','LINK_P','base');c.esd('D302','LINK_N','base')
    return c

def export(c):
    folder=OUT/c.name;folder.mkdir(parents=True,exist_ok=True);pretty=folder/'Camera.pretty';pretty.mkdir(exist_ok=True)
    g.LIB.clear();g.PARTS.clear();g.CONNECTIONS.clear();g.FOOTPRINTS.clear()
    g.uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'skellycad/E01/'+c.name+'/'+str(s)))
    g.SHEET=g.uid('root')
    active=0;passives=0
    for ref,p in c.parts.items():
        key='E01_'+ref
        if 'source_ref' in p:
            srcid=re.search(r'\(lib_id\s+"([^"]+)"',INST[p['source_ref']])[1];block=g.rename(LIB[srcid],key)
            block=re.sub(r'\(symbol\s+"[^"\n]+(_[0-9]+_[0-9]+)"',lambda m:'(symbol "'+key+m[1]+'"',block)
        else:block=symbol(key,p['pins'])
        g.LIB[key]=block
        fplib,fpname=p['footprint'].split(':',1)
        if fpname=='TI_RHB0032P_E01':fptext=qfn(fpname,32,5,3.7,2.4,.6,.25);(pretty/(fpname+'.kicad_mod')).write_text(fptext)
        elif fpname=='TI_RGZ0048B_E01':fptext=qfn(fpname,48,7,4.1,3.4,.6,.24);(pretty/(fpname+'.kicad_mod')).write_text(fptext)
        elif fpname=='TI_DRV0006A_E01':
            pads=[(1,-.975,-.65,.45,.3),(2,-.975,0,.45,.3),(3,-.975,.65,.45,.3),(4,.975,.65,.45,.3),(5,.975,0,.45,.3),(6,.975,-.65,.45,.3),(7,0,0,1,1.6)]
            fptext=footprint(fpname,(2,2),pads)
            for b in children(fptext):
                if g.tag(b)=='pad' and re.match(r'\(pad "?7"?\s',b):fptext=fptext.replace(b,b.replace(' "F.Paste"',''))
            for y in [-.4,.4]:fptext=fptext.rstrip()[:-1]+f'\n(fp_rect (start -.4 {y-.275}) (end .4 {y+.275}) (stroke (width 0) (type solid)) (fill solid) (layer "F.Paste"))\n)'
            (pretty/(fpname+'.kicad_mod')).write_text(fptext)
        else:
            source=(BASE/'Camera.pretty'/f'{fpname}.kicad_mod') if fplib=='Camera' else SHARE/'footprints'/f'{fplib}.pretty'/f'{fpname}.kicad_mod'
            assert source.is_file(),source;shutil.copyfile(source,pretty/source.name)
        # Large active devices occupy an upper grid; each supporting part is labelled below.
        isactive=ref[0] in 'UYJQ' or len(p['pin_nets'])>4
        if isactive:x=85+(active%6)*130;y=140+(active//6)*145;active+=1
        else:x=40+(passives%12)*65;y=560+(passives//12)*31;passives+=1
        before=len(g.PARTS);g.add(ref,'E01',ref,p['value'],x,y,p['pin_nets'],'Camera:'+fpname)
        block=g.PARTS[before];ps=g.pins(key);maxy=max(v[2] for v in ps.values())
        for prop,dy in [('Reference',7.62),('Value',5.08)]:
            old=next(b for b in children(block) if g.tag(b)=='property' and g.prop('('+b+')',prop)) if False else None
            for b in list(children(block)):
                if g.tag(b)=='property' and b.startswith('(property "'+prop+'"'):
                    block=block.replace(b,re.sub(r'\(at [^)]+\)',f'(at {round(x/1.27)*1.27} {round(y/1.27)*1.27-maxy-dy} 0)',b,count=1))
        for prop,value in [('MPN',p['mpn']),('Region',p['region'])]:block=block.rstrip()[:-1]+f'\n(property "{prop}" {json.dumps(value)} (at {x} {y} 0) (effects (font (size 1 1)) (hide yes))))'
        if not p['populated']:block=block.replace('(dnp no)','(dnp yes)')
        g.PARTS[before]=block
    # Explicit rail sources: off-board source / switching output after inductor.
    flags=['GND','H5V','H1V8','M1_DVDD','M1_AVDD','M1_DOVDD','M1_PVDD','SER_VDDD','SER_VDDDRV','SER_VDDPLL'] if c.name=='head-interface' else ['GND','B5V','+3V3','P4_VDD_HP','RX1V8','RX_VDD18_FPD','RX_VDD18_CSI','RX_VDD18_P','USB_VBUS']
    for i,net in enumerate(flags):g.add('#FLG'+str(i+1),'power','PWR_FLAG','PWR_FLAG',35+i*70,970,{'1':net})
    g.text('THREE-BOARD E01 / '+c.name.upper()+' / CONNECTED ELECTRICAL DRAFT',25,15)
    g.text('Pins and matching net labels define connectivity. Unrouted; procurement, optics, cable and hardware qualification remain open.',25,28)
    g.text('Active circuitry',25,43);g.text('Supporting parts / references match BOM and PCB / no implicit connections',25,530)
    (folder/'Camera.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+'\n'.join(g.LIB.values())+'\n)',encoding='utf-8')
    cached='\n'.join(g.rename(b,'Camera:'+key) for key,b in g.LIB.items())
    (folder/'camera.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {g.SHEET}) (paper "User" 1189 1050)\n(lib_symbols\n'+cached+'\n)\n'+'\n'.join(g.PARTS)+'\n)',encoding='utf-8')
    (folder/'camera.kicad_pro').write_text('{}\n')
    (folder/'sym-lib-table').write_text('(sym_lib_table (lib (name "Camera") (type "KiCad") (uri "${KIPRJMOD}/Camera.kicad_sym") (options "") (descr "E01 local symbols")))')
    (folder/'fp-lib-table').write_text('(fp_lib_table (lib (name "Camera") (type "KiCad") (uri "${KIPRJMOD}/Camera.pretty") (options "") (descr "E01 local footprints")))')
    (folder/'expected-connections.json').write_text(json.dumps(g.CONNECTIONS,indent=2)+'\n')
    (HERE/(c.name+'-components.json')).write_text(json.dumps(c.parts,indent=2)+'\n')
    for name in ['LICENSE-Antmicro','LICENSE-Espressif-library.md']:
        if (BASE/name).exists():shutil.copyfile(BASE/name,folder/name)
    for args in [['sch','export','netlist','--format','kicadxml','--output',str(folder/'netlist.xml')],['sch','erc','--format','json','--output',str(folder/'erc.json')],['sch','export','pdf','--output',str(folder/'camera.pdf')]]:
        subprocess.run([str(CLI)]+args+[str(folder/'camera.kicad_sch')],check=True,capture_output=True)
    print(c.name,len(c.parts),'parts exported')

if __name__=='__main__':export(base() if len(sys.argv)>1 and sys.argv[1]=='base' else head())
