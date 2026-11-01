"""Create R02 connected electrical draft. Never overwrite an existing revision.

Sources: [@antmicroOv9281Board; @esp32P4HardwareGuide; @esp32P4Datasheet;
@espressifKicadLibrary; @tiTlv62569; @stUsblc6]. Not a fabrication release.
"""
from pathlib import Path
import re, json, uuid, shutil, hashlib, math, sys
from extract_head import children

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
KICAD = Path('C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/share/kicad')
OUT = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'electronics/r02'
SHEET = 'e3549937-ce5e-4391-94ab-3d7fcb0b1d31'
LIB = {}
PARTS = []
CONNECTIONS = {}
FOOTPRINTS = {}

def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL, 'skellycad/ov9281/r02/'+s))
def q(s): return json.dumps(str(s))
def tag(b): return re.match(r'\(([^\s)]+)',b)[1]
def prop(b,n):
    m=re.search(r'\(property "'+n+r'" "([^"]*)"',b)
    return m[1] if m else ''
def rename(b,name): return re.sub(r'^\(symbol "[^"]+"', '(symbol '+q(name),b,count=1)

def load(lib,name):
    key=lib+'_'+name
    if key in LIB:return key
    path=(ROOT/'reference/espressif/Espressif.kicad_sym') if lib=='Espressif' else KICAD/'symbols'/f'{lib}.kicad_sym'
    syms={re.match(r'\(symbol "([^"]+)"',b)[1]:b for b in children(path.read_text(encoding='utf-8')) if tag(b)=='symbol'}
    def flat(n):
        b=syms[n]; ext=re.search(r'\(extends "([^"]+)"\)',b)
        if not ext:return b
        base=flat(ext[1])
        own=list(children(b)); names={re.match(r'\(property "([^"]+)"',x)[1] for x in own if tag(x)=='property'}
        inherited=[x for x in children(base) if not(tag(x)=='property' and re.match(r'\(property "([^"]+)"',x)[1] in names)]
        return '(symbol '+q(n)+'\n'+'\n'.join(inherited+[x for x in own if tag(x)!='extends'])+'\n)'
    b=rename(flat(name),key)
    # Nested symbol names must follow the root name.
    b=re.sub(r'\(symbol "[^"\n]+(_[0-9]+_[0-9]+)"',lambda m:'(symbol '+q(key+m[1]),b)
    if lib=='Espressif' and name=='ESP32-P4X':
        for unit in list(children(b)):
            if tag(unit)!='symbol':continue
            replacement=unit
            for pin in children(unit):
                if tag(pin)=='pin' and re.search(r'\(number "(101|102)"',pin):
                    replacement=replacement.replace(pin,pin.replace('(pin bidirectional','(pin power_in',1))
            b=b.replace(unit,replacement)
    fp=prop(b,'Footprint')
    if fp:
        fplib,fpname=fp.split(':',1)
        source=(ROOT/'reference/espressif'/f'{fpname}.kicad_mod') if lib=='Espressif' else KICAD/'footprints'/f'{fplib}.pretty'/f'{fpname}.kicad_mod'
        if source.exists():
            FOOTPRINTS[fpname]=source
            b=b.replace(q(fp),q('Camera:'+fpname))
    LIB[key]=b
    return key

def pins(key):
    result={}
    for unit in children(LIB[key]):
        if tag(unit)!='symbol':continue
        for p in children(unit):
            if tag(p)!='pin':continue
            num=re.search(r'\(number "([^"]+)"',p)[1]
            name=re.search(r'\(name "([^"]*)"',p)[1]
            coords=list(map(float,re.search(r'\(at ([^)]+)\)',p)[1].split()))
            result[num]=(name,*coords)
    return result

def label(net,x,y,angle=0):
    if net in {'+3V3','+1V8','+1V2','+2V8','GND'}:
        PARTS.append(f'(global_label {q(net)} (shape input) (at {x:.4f} {y:.4f} {angle}) (effects (font (size 1.0 1.0)) (justify left)) (uuid {uid(str((net,x,y)))}))')
        return
    PARTS.append(f'(label {q(net)} (at {x:.4f} {y:.4f} {angle}) (effects (font (size 1.0 1.0)) (justify left bottom)) (uuid {uid(str((net,x,y)))}))')

def add(ref,lib,name,value,x,y,nets,fp=None):
    x=round(x/1.27)*1.27; y=round(y/1.27)*1.27
    key=load(lib,name); ps=pins(key)
    if fp:
        fplib,fpname=fp.split(':',1); source=KICAD/'footprints'/f'{fplib}.pretty'/f'{fpname}.kicad_mod'
        if source.exists():FOOTPRINTS[fpname]=source;fp='Camera:'+fpname
    else:fp=prop(LIB[key],'Footprint')
    p=f'(symbol (lib_id "Camera:{key}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {uid(ref)})'
    # References/values above the body; all connectivity is explicit labelled wiring.
    p+=f'(property "Reference" {q(ref)} (at {x} {y-8} 0) (effects (font (size 1.27 1.27))))'
    p+=f'(property "Value" {q(value)} (at {x} {y-6} 0) (effects (font (size 1 1))))'
    p+=f'(property "Footprint" {q(fp)} (at {x} {y} 0) (effects (font (size 1 1)) (hide yes)))'
    for num in ps:p+=f'(pin {q(num)} (uuid {uid(ref+num)}))'
    p+=f'(instances (project "camera" (path "/{SHEET}" (reference {q(ref)}) (unit 1)))))'
    PARTS.append(p)
    for num,(pn,px,py,angle) in ps.items():
        xx,yy=x+px,y-py
        net=nets.get(num)
        if net is None:
            PARTS.append(f'(no_connect (at {xx} {yy}) (uuid {uid(ref+num+"nc")}))')
            continue
        CONNECTIONS[ref+'.'+num]=net
        # Pin angle points inward; extend away from body.
        dx=-math.cos(math.radians(angle));dy=math.sin(math.radians(angle))
        ex,ey=round(xx+dx*5.08,4),round(yy+dy*5.08,4)
        PARTS.append(f'(wire (pts (xy {xx} {yy}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid {uid(ref+num+"w")}))')
        label(net,ex,ey,90 if abs(dy)>0.5 else 0)

counter={'R':100,'C':100,'L':100}
slot=0
def passive(kind,val,a,b):
    global slot
    counter[kind]+=1;ref=kind+str(counter[kind]);x=30+(slot%16)*49;y=335+(slot//16)*32;slot+=1
    fp={'R':'Resistor_SMD:R_0402_1005Metric','C':'Capacitor_SMD:C_0402_1005Metric','L':'Inductor_SMD:L_0805_2012Metric'}[kind]
    add(ref,'Device',kind,val,x,y,{'1':a,'2':b},fp)
    return ref

def text(s,x,y):PARTS.append(f'(text {q(s)} (at {x} {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid(s)}))')

def main():
    if OUT.exists():raise SystemExit('R02 exists; choose a new revision rather than overwrite.')
    OUT.mkdir(parents=True); (OUT/'Camera.pretty').mkdir()
    src=ROOT/'reference/antmicro/ov9281-dual-camera-board.kicad_sch'
    source=list(children(src.read_text(encoding='utf-8')))
    libblock=next(b for b in source if tag(b)=='lib_symbols')
    source_lib={re.match(r'\(symbol "([^"]+)"',b)[1]:b for b in children(libblock)}
    # Adds all sensor-1 auxiliary analog networks omitted from R01.
    regions=[(0,0,123,130),(0,140,145,202),(0,220,210,245),(230,30,303,65),(150,140,216,160),(150,175,216,200)]
    def zone(x,y):return next((i for i,(a,b,c,d) in enumerate(regions) if a<=x<=c and b<=y<=d),None)
    for b in source:
        k=tag(b)
        if k not in {'symbol','wire','junction','no_connect','label','global_label'}:continue
        coords=re.findall(r'\(xy\s+([-\d.]+)\s+([-\d.]+)',b) if k=='wire' else re.findall(r'\(at\s+([-\d.]+)\s+([-\d.]+)',b)[:1]
        zones=[zone(float(x),float(y)) for x,y in coords]
        if not zones or zones[0] is None or any(z!=zones[0] for z in zones):continue
        if k=='symbol':
            old=re.search(r'\(lib_id "([^"]+)"',b)[1];new='A_'+re.sub(r'[^a-zA-Z0-9_]','_',old)
            definition=rename(source_lib[old],new)
            definition=re.sub(r'\(symbol "[^"\n]+(_[0-9]+_[0-9]+)"',lambda m:'(symbol '+q(new+m[1]),definition)
            for part in [prop(definition,'Footprint')]:
                if part:definition=definition.replace(q(part),q('Camera:'+part.split(':')[-1]))
            LIB[new]=definition
            b=b.replace(q(old),q('Camera:'+new),1).replace('(project "ov9281-dual-camera-board"','(project "camera"')
            fp=prop(b,'Footprint')
            if fp:b=b.replace(q(fp),q('Camera:'+fp.split(':')[-1]))
        PARTS.append(b)
    label('M1_DVDD',156.21,148.59)
    # Match official v3.x P4X pinout. GPIO5 LED PWM; GPIO6 reset assert;
    # GPIO7/8 I2C use external level translation to the sensor's 1.8 V domain.
    nets={'9':'+3V3','21':'+3V3','26':'P4_VDD_HP','54':'P4_VDD_HP','76':'P4_VDD_HP','91':'P4_VDD_HP',
          '62':'+3V3','85':'+3V3','96':'+3V3','101':'+3V3','102':'+3V3','75':'+3V3','77':'+3V3','105':'GND',
          '71':'P4_FLASH_VDD','30':'P4_FLASH_VDD','72':'P4_PSRAM_VDD','59':'P4_PSRAM_VDD','67':'P4_PSRAM_VDD',
          '73':'P4_MIPI_2V5','41':'P4_MIPI_2V5','74':'P4_LDO4_UNUSED','51':'+3V3',
          '78':'P4_FB','79':'P4_EN_DCDC','103':'P4_EN','99':'P4_XTAL_N','100':'P4_XTAL_P',
          '27':'FLASH_CS','28':'FLASH_Q','29':'FLASH_WP','31':'FLASH_HOLD','32':'FLASH_CLK','33':'FLASH_D',
          '42':'CAM_L_D0_N','43':'CAM_L_D0_P','44':'CAM_L_CLK_P','45':'CAM_L_CLK_N','46':'CAM_L_D1_N','47':'CAM_L_D1_P',
          '48':'P4_CSI_REXT','49':'USB_DM_CHIP','50':'USB_DP_CHIP',
          '5':'LED_PWM','6':'CAM_RESET_ASSERT','7':'CAM_SCL_3V3','8':'CAM_SDA_3V3',
          '69':'P4_UART_TX','70':'P4_UART_RX','66':'P4_BOOT','68':'P4_DOWNLOAD_ENABLE'}
    add('U101','Espressif','ESP32-P4X','ESP32-P4NRW16X / v3.x',450,90,nets)
    text('R02 / OV9281 + ESP32-P4X connected draft - NOT FOR FABRICATION',25,15)
    text('Sensor circuit / bias networks restored; original Antmicro references retained',25,25)
    text('USB, flash, core supply and 1.8 V control translation',350,185)
    text('Supporting passives: labelled nets; values/footprints remain subject to BOM review',25,310)
    for i,net in enumerate(['USB_VBUS','GND','+3V3','P4_VDD_HP']):
        add('#FLG'+str(101+i),'power','PWR_FLAG','PWR_FLAG',350+i*25,165,{'1':net})
    # QSPI flash and processor clocks.
    add('U102','Memory_Flash','W25Q32JVSS','W25Q32JVSS (4 MB candidate)',585,55,{'1':'FLASH_CS','2':'FLASH_Q','3':'FLASH_WP','4':'GND','5':'FLASH_D','6':'FLASH_CLK','7':'FLASH_HOLD','8':'P4_FLASH_VDD'})
    add('Y101','Device','Crystal_GND24','40 MHz / CL TBD',585,100,{'1':'P4_XTAL_P','2':'GND','3':'P4_XTAL_N','4':'GND'},'Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm')
    passive('C','CL_TBD','P4_XTAL_P','GND');passive('C','CL_TBD','P4_XTAL_N','GND')
    passive('R','10k','P4_FLASH_VDD','FLASH_CS');passive('C','100n','P4_FLASH_VDD','GND')
    passive('R','10k','+3V3','P4_EN');passive('C','1u','P4_EN','GND')
    passive('R','10k','+3V3','P4_BOOT');passive('R','10k','+3V3','P4_DOWNLOAD_ENABLE')
    add('J103','Connector_Generic','Conn_01x05','PROGRAM / RESET pads',690,55,{'1':'GND','2':'P4_UART_TX','3':'P4_UART_RX','4':'P4_BOOT','5':'P4_EN'})
    # Core supply matches the manufacturer v3.x circuit, including feedback divider.
    add('U103','Regulator_Switching','TLV62569DBV','TLV62569DBV / core',390,225,{'1':'P4_EN_DCDC','2':'GND','3':'P4_SW','4':'+3V3','5':'P4_FB'})
    passive('L','2.2u / Isat TBD','P4_SW','P4_VDD_HP');passive('C','4.7u','+3V3','GND');passive('C','22u','P4_VDD_HP','GND')
    passive('R','499k','P4_VDD_HP','P4_FB');passive('R','499k','P4_FB','GND');passive('C','22p','P4_VDD_HP','P4_FB')
    # 5 V to nominal 3.3 V system supply; 453k/100k yields 3.318 V nominal.
    add('U104','Regulator_Switching','TLV62569DBV','TLV62569DBV / system',455,225,{'1':'USB_VBUS','2':'GND','3':'SYS_SW','4':'USB_VBUS','5':'SYS_FB'})
    passive('L','2.2u / Isat TBD','SYS_SW','+3V3');passive('C','4.7u','USB_VBUS','GND');passive('C','22u','+3V3','GND')
    passive('R','453k','+3V3','SYS_FB');passive('R','100k','SYS_FB','GND')
    # USB2 high-speed pins, not the separate full-speed GPIO peripheral.
    add('J101','Connector_Generic','Conn_01x04','USB / JST 4-contact candidate',690,115,{'1':'USB_VBUS','2':'USB_DM','3':'USB_DP','4':'GND'},'Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal')
    add('U105','Power_Protection','USBLC6-2P6','USBLC6-2P6',585,150,{'1':'USB_DM','6':'USB_DM','3':'USB_DP','4':'USB_DP','2':'GND','5':'USB_VBUS'})
    passive('R','0','USB_DM','USB_DM_CHIP');passive('R','0','USB_DP','USB_DP_CHIP');passive('R','4.02k 1%','P4_CSI_REXT','GND')
    # Separate decoupling per power pin, plus bulk and PHY rails.
    for pin in ['9','21','26','54','62','75','76','77','85','91','96','101','102']:
        passive('C','100n / U101.'+pin,nets[pin],'GND')
    for rail in ['+3V3','P4_VDD_HP']:passive('C','10u',rail,'GND')
    for rail in ['P4_FLASH_VDD','P4_PSRAM_VDD','P4_LDO4_UNUSED']:
        passive('C','1u',rail,'GND')
    for pin in ['30','59','67']:passive('C','100n / U101.'+pin,nets[pin],'GND')
    for val in ['10n','100n','1u']:passive('C',val,'P4_MIPI_2V5','GND')
    for val in ['10n','100n','4.7u']:passive('C',val,'+3V3','GND')
    # Bidirectional open-drain I2C level translation. BSS138: G=1,S=2,D=3.
    for ref,lo,hi,x in [('Q101','M1_CAM_SCL_1V8','CAM_SCL_3V3',530),('Q102','M1_CAM_SDA_1V8','CAM_SDA_3V3',590)]:
        add(ref,'Transistor_FET','BSS138','BSS138',x,225,{'1':'+1V8','2':lo,'3':hi})
        passive('R','4.7k','+1V8',lo);passive('R','4.7k','+3V3',hi)
    add('Q103','Transistor_FET','BSS138','BSS138 / reset asserted HIGH',650,225,{'1':'CAM_RESET_ASSERT','2':'GND','3':'CAM_NRST_1V8'})
    passive('R','100k','+3V3','CAM_RESET_ASSERT');passive('R','10k','+1V8','CAM_NRST_1V8')
    passive('R','10k','M1_VSYNC_1V8_M','GND')
    # LED circuitry remains intentionally unpopulated, pending actual emitter and exposure budget.
    add('J104','Connector_Generic','Conn_01x03','LED DRIVER RESERVED',735,225,{'1':'LED_PWM','2':'+3V3','3':'GND'})
    text('LED current driver/emitter pending. USB enumeration power/inrush budget pending.',350,275)
    text('P4 firmware: enable 2.5 V MIPI LDO; RAW8 mono path and sustained rate untested.',350,285)
    # Logical harness pin assignment. Not yet a selected physical flex connector.
    harness=['GND','CAM_L_D0_N','CAM_L_D0_P','GND','CAM_L_CLK_N','CAM_L_CLK_P','GND','CAM_L_D1_N','CAM_L_D1_P','GND',
             '+1V8','M1_CAM_SCL_1V8','M1_CAM_SDA_1V8','GND','CAM_NRST_1V8','M1_VSYNC_1V8_M','+1V2','GND','+2V8','GND','+3V3','LED_PWM','GND','GND']
    add('J102','Connector_Generic','Conn_01x24','HEAD HARNESS / logical only',325,80,{str(i+1):n for i,n in enumerate(harness)})
    (OUT/'interface.json').write_text(json.dumps({'status':'Logical harness allocation; connector and board partition not frozen','pins':{str(i+1):n for i,n in enumerate(harness)},'usb_pins':{'1':'VBUS','2':'D-','3':'D+','4':'GND'},'warning':'USB numbering is our proposed harness, not verified Pupil cable compatibility'},indent=2)+'\n')
    # Keep actual source symbols locally, with attribution in source-record.json.
    (OUT/'Camera.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+'\n'.join(LIB.values())+'\n)',encoding='utf-8')
    embed=[rename(b,'Camera:'+name) for name,b in LIB.items()]
    sch=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{SHEET}") (paper "A1")\n'
    sch+='(lib_symbols '+'\n'.join(embed)+')\n'+'\n'.join(PARTS)+'\n(sheet_instances (path "/" (page "1")))\n)'
    (OUT/'camera.kicad_sch').write_text(sch,encoding='utf-8')
    (OUT/'camera.kicad_pro').write_text(json.dumps({'meta':{'filename':'camera.kicad_pro','version':1}},indent=2)+'\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "Camera") (type "KiCad") (uri "${KIPRJMOD}/Camera.kicad_sym") (options "") (descr "Project-local licensed symbols")))\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Camera") (type "KiCad") (uri "${KIPRJMOD}/Camera.pretty") (options "") (descr "Project-local footprints")))\n')
    for name,path in FOOTPRINTS.items():shutil.copy2(path,OUT/'Camera.pretty'/f'{name}.kicad_mod')
    (OUT/'expected-connections.json').write_text(json.dumps(CONNECTIONS,indent=2)+'\n')
    shutil.copy2(ROOT/'reference/espressif/LICENSE.md',OUT/'LICENSE-Espressif-library.md')
    shutil.copy2(ROOT/'reference/antmicro/LICENSE',OUT/'LICENSE-Antmicro')
    (OUT/'source-record.json').write_text(json.dumps({'revision':'OV9281-P4-R02','antmicro_commit':'ea69666fa06f66a0691e50eebff9356cc2a08e32','espressif_library_commit':'dd76561812ab300351234ba6e0ec1295641796f0','local_symbol_changes':'ESP32-P4X VDD_ANA pin101 and VDD_BAT pin102 changed from bidirectional to power_in, per datasheet; library names localized','kicad_libraries':'Installed KiCad 10.0.7; CC-BY-SA-4.0 with design exception','espressif_library':'CC-BY-SA-4.0 with design exception; see included license','antmicro':'Apache-2.0; copyright Antmicro 2019-2025','status':'Connected draft; schematic and BOM validation incomplete; no routing or hardware test','schematic_sha256':hashlib.sha256((OUT/'camera.kicad_sch').read_bytes()).hexdigest()},indent=2)+'\n')
    print(OUT)

if __name__=='__main__':main()
