"""Single source for architecture drawings and placement envelopes (millimetres).

These are body-only placements, not land patterns, a BOM or a routed design.
Sources: [@ti953A01; @ti954A01; @esp32P4Datasheet; @omnivisionOv9281Brief].
"""
from pathlib import Path
import json, uuid, subprocess, html, hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'generated/three-board-a01'
CLI=Path('C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe')
def uid(x): return str(uuid.uuid5(uuid.NAMESPACE_URL,'skellycad/three-board-a01/'+x))
def q(x):return json.dumps(str(x))

def layout():
    boards={'head':{'origin':[0,0],'size':[14,10],'thickness':.303},
            'interface':{'origin':[39,0],'size':[18,10],'thickness':.303},
            'base':{'origin':[77,0],'size':[40,30],'thickness':.8}}
    parts=[]
    def part(board,ref,kind,x,y,w,h,z,mpn='',evidence='Engineering reserve; exact part/land pattern unresolved'):
        parts.append(dict(board=board,ref=ref,kind=kind,center=[x,y],body=[w,h,z],mpn=mpn,evidence=evidence,side='F'))
    part('head','SENSOR','sensor',7,5,5.24,4.46,.8,'OV09281-H64A','Package XY from R11; Z envelope; optical image plane provisional')
    part('head','IR1','LED',1,5,1.6,.8,1.1,'AP1608F3C','R11 candidate; illumination unqualified')
    part('head','IR2','LED',13,5,1.6,.8,1.1,'AP1608F3C','R11 candidate; illumination unqualified')
    part('head','CLK24','clock',1.5,1.9,2.5,2,.8,'SG-210STF candidate','R11 24 MHz oscillator envelope')
    # Keep passive bodies out of the 8 x 8 optical-holder envelope.
    for row,y in enumerate([.40,9.60]):
        for i in range(10):part('head',f'HC{row*10+i+1}','capacitor',1.15+i*1.30,y,1,.5,.55)
    for i in range(4):part('head',f'HR{i+1}','resistor',12.6,1.4+i*.7,.6,.3,.3)
    part('interface','SER','serializer',6,5,5,5,1,'DS90UB953TRHBRQ1','TI 5 x 5 mm package; height envelope')
    part('interface','J_TETHER','connector',15,5,5.6,4.5,3,'TBD','Connector body reserve only; no selected pinout or rated channel')
    part('interface','BUCK18','regulator',2,2,1.6,1.2,.6,'TLV62569DRLR','R11 package retained as power candidate')
    part('interface','L_BUCK','inductor',10.5,2,2.5,2,1.2,'DFE252012F-2R2M=P2','R11 package candidate')
    part('interface','LDO12','regulator',10.4,7.1,1,1,.6,'TLV73312PDQNR')
    part('interface','LDO28','regulator',10.4,8.5,1,1,.6,'TLV73328PDQNR')
    for i in range(3):part('interface',f'FILTER{i+1}','inductor',1.5,4+i*1.7,2,1.25,.7,'MLP2012S3R3MT0S1')
    for row,y in enumerate([.5,9.5]):
        for i in range(13):part('interface',f'IC{row*13+i+1}','capacitor',2.8+i*1.1,y,.6,.3,.35)
    for i in range(4):part('interface',f'IR{i+1}','resistor',11.2,3.5+i*.7,.6,.3,.3)
    part('interface','LED_DRIVER','transistor',10.2,5,1,.6,.5,'PMZB200UNEYL','Drive and stock need qualification')
    for ref,kind,x,y,w,h,z,mpn in [('RX','receiver',8,15,7,7,1,'DS90UB954TRGZRQ1'),('P4','processor',23,15,10,10,1,'ESP32-P4NRW16X'),('FLASH','memory',23,6,4,3,.8,'W25Q32JV'),('USB','connector',36,15,7,9,3.3,'USB connector TBD'),('LINK_IN','connector',3.2,5,5.6,4.5,3,'Tether connector TBD'),('POWER','connector',35,26,6,5,3,'Bench power input TBD'),('BASE_POWER','power-reserve',9,25,12,6,1.6,'Regulators/inductors reserve'),('CLK25','clock',9,6,3.2,2.5,1,'25 MHz reference TBD'),('CLK40','clock',22,24,2,1.6,.5,'40 MHz crystal')]:
        part('base',ref,kind,x,y,w,h,z,mpn)
    for i in range(12):part('base',f'BC{i+1}','capacitor',16+i*.95,3,.6,.3,.35)
    for i in range(10):part('base',f'BD{i+1}','capacitor',16+i*.95,28,.6,.3,.35)
    data={'revision':'THREE-BOARD-A01','units':'mm','kind':'Architecture placement only; not pin-complete or routed',
        'boards':boards,'parts':parts,'flex':{'origin':[14,2.25],'size':[25,5.5],'thickness':.166},
        'optics':{'holder_outer':[8,8],'holder_inner':[6,6],'holder_height':1.4,'barrel_diameter':6,'barrel_height':2.5,'barrel_bottom_above_board':1.4,'status':'Provisional space reservation, not a selected lens'},
        'supports':{'FR4':{'thickness':.1,'adhesive':.05},'steel':{'thickness':.05,'adhesive':.025}},
        'limits':['Passive counts and packages reserve layout area; no pin mapping or complete procurement BOM.',
        'All head/interface components on front; no pad, courtyard or routing clearance proof.',
        'Base offset in scene is for viewing, not tether length. Tether shown schematically only.',
        'Optics and species mount fit are unverified. Body collision checks do not establish manufacturability.']}
    # Verify body rectangles fit and do not intersect, before constructing solids.
    checks=[]
    for board,b in boards.items():
        ps=[p for p in parts if p['board']==board]
        for p in ps:
            x,y=p['center'];w,h,_=p['body']
            assert x-w/2>=0 and y-h/2>=0 and x+w/2<=b['size'][0] and y+h/2<=b['size'][1],p
        for i,a in enumerate(ps):
            for b2 in ps[i+1:]:
                overlap=all(abs(a['center'][j]-b2['center'][j])<(a['body'][j]+b2['body'][j])/2-1e-7 for j in [0,1])
                assert not overlap,(a['ref'],b2['ref'])
        checks.append({'board':board,'body_count':len(ps),'body_rectangles_fit':True,'body_overlaps':0})
    data['checks']=checks
    return data

def schematic(name,blocks,connections,notes):
    content=[]
    def text(s,x,y,size=2):content.append(f'(text {q(s)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid {uid(name+str((s,x,y)))}))')
    def poly(points,key):content.append('(polyline (pts '+' '.join(f'(xy {x} {y})' for x,y in points)+f') (stroke (width 0.25) (type default)) (fill (type none)) (uuid {uid(name+key)}))')
    text('THREE-BOARD A01 | '+name.upper().replace('-',' '),20,20,4)
    text('ARCHITECTURE ONLY - functional links, NOT pin-level wiring or a fabrication schematic',20,30,2)
    for ident,title,sub,x,y,w,h in blocks:
        poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)],ident)
        text(title,x+4,y+8,2.5)
        for i,s in enumerate(sub):text(s,x+4,y+15+i*5,1.6)
    for ident,points,caption,x,y in connections:
        poly(points,ident);text(caption,x,y,1.6)
    for i,n in enumerate(notes):text(n,20,195+i*7,1.7)
    s=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid(name)}) (paper "A3") (lib_symbols)\n'+'\n'.join(content)+'\n)'
    file=OUT/(name+'.kicad_sch');file.write_text(s,encoding='utf-8')
    subprocess.run([str(CLI),'sch','export','pdf','-o',str(OUT/(name+'.pdf')),str(file)],check=True,capture_output=True,text=True)
    return file

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data=layout();(HERE/'placement.json').write_text(json.dumps(data,indent=2)+'\n')
    schematics=[]
    schematics.append(schematic('system',[
        ('h','CAMERA HEAD',['OV9281 + IR optics','Two axial IR LEDs','Local bypass capacitors'],20,65,90,55),
        ('i','CAMERA INTERFACE',['DS90UB953 serializer','Local 1.8 / 1.2 / 2.8 V','Protection + tether exit'],145,65,105,55),
        ('b','BASE STATION',['DS90UB954 -> ESP32-P4','Frame buffering + USB','Enclosure or backpack'],285,65,110,55)],
        [('m',[(110,90),(145,90)],'Short flex',112,85),('t',[(250,90),(285,90)],'STP tether',252,85),('usb',[(340,120),(340,150)],'USB to computer',342,145)],
        ['Head assembly target <1.0 g includes both small boards, flex, optics, supports and connector.',
         'Primary: 640 x 400 RAW8 at 100 fps; continuous transport not implemented or measured.',
         'Tether: 0.30 / 0.60 m, two data conductors + supply + return + shield; connector unqualified.',
         'External tether and base mass reported separately; R11 preserved. Sources: COMPONENT-CHAIN.md.']))
    schematics.append(schematic('camera-head',[
        ('s','OV9281',['RAW8 VC0 / two CSI lanes','24 MHz local oscillator','1.2 V core / 2.8 V analog','1.8 V IO + local decoupling'],35,60,110,65),
        ('o','OPTICS / ILLUMINATION',['Adjustable close-focus optics','Visible-blocking IR-pass filter','Two axial 940 nm candidates','IR driver off by default'],220,60,140,65)],
        [('c',[(145,100),(185,100),(185,150)],'CSI + SCCB + reset / timing to interface',100,157)],
        ['Head envelope 14 x 10 mm; all parts on one side. Lens assembly remains provisional.',
         'Optical coverage, focus at 10 / 15 / 20 mm, heat and illumination require physical qualification.',
         'No crop silently substituted; no functional circuit or pin-complete symbol claimed.']))
    schematics.append(schematic('camera-interface',[
        ('s','DS90UB953',['CSI input from head','RAW8 remains RAW8','I2C / GPIO control tunnel','Receiver-derived link clock'],35,60,105,65),
        ('p','LOCAL POWER',['5 V tether input -> 1.8 V buck','1.8 V -> 1.2 V core LDO','5 V -> 2.8 V analog LDO','Filters / decoupling / LED driver'],215,60,160,65)],
        [('l',[(85,125),(85,160)],'Differential STP + separate power / return to base',35,170)],
        ['Interface envelope 18 x 10 mm; serializer is not a CPU or JPEG encoder.',
         '100 ohm STP candidate; TI AC coupling / termination circuit must be designed explicitly.',
         'Do not wire this link as USB. No connector pin assignment made in this architecture sheet.']))
    schematics.append(schematic('base-station',[
        ('r','DS90UB954',['One input enabled','25 MHz reference','RAW8 / VC0 forwarding','CSI output 2 x 800 candidate'],20,60,110,65),
        ('p','ESP32-P4',['CSI DMA + frame buffers','Control I2C to receiver','16 MB package PSRAM','4 MB flash / USB HS device'],165,60,110,65),
        ('u','HOST / POWER',['USB recording','Separate bench power','Current-limited tether supply','No USB backfeed'],305,60,95,65)],
        [('c',[(130,90),(165,90)],'CSI',137,85),('usb',[(275,90),(305,90)],'USB HS',277,85)],
        ['Base envelope 40 x 30 mm; no head mass constraint. Clock and reset sequencing need detailed audit.',
         'Firmware sequence: synthetic stream -> receiver pattern -> sensor snapshots -> continuous recording.',
         'Full-resolution 120 fps RAW8 exceeds USB2; CSI nominal rates do not prove sustainable recording.']))
    # Scaled plan view derived from exactly the same bodies as the native CAD.
    colors={'sensor':'#207c83','LED':'#df495e','serializer':'#354d65','processor':'#354d65','connector':'#e2dfcd'}
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-3 -12 125 53" role="img" aria-label="Three-board native placement envelopes, millimetres">','<rect x="-3" y="-12" width="125" height="53" fill="#f5f7fa"/>']
    for name,b in data['boards'].items():
        x,y=b['origin'];w,h=b['size'];svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx=".4" fill="#c3d7ce" stroke="#35755e" stroke-width=".2"/><text x="{x}" y="{y-4}" font-size="2" font-family="sans-serif">{name.upper()} {w} x {h} mm</text>')
    f=data['flex'];svg.append('<rect x="14" y="2.25" width="25" height="5.5" fill="#d9b963"/><text x="16" y="12" font-size="1.7" font-family="sans-serif">25 x 5.5 mm local flex</text>')
    for p in data['parts']:
        ox,oy=data['boards'][p['board']]['origin'];x,y=p['center'];w,h,z=p['body']
        svg.append(f'<rect x="{ox+x-w/2}" y="{oy+y-h/2}" width="{w}" height="{h}" fill="{colors.get(p["kind"],"#67717c")}" stroke="white" stroke-width=".08"><title>{html.escape(p["ref"]+" "+p["mpn"]+" "+str(p["body"])+" mm")}</title></rect>')
    svg.append('<rect x="3" y="1" width="8" height="8" fill="none" stroke="#633c7d" stroke-width=".3"/><circle cx="7" cy="5" r="3" fill="#69839c" fill-opacity=".55" stroke="#633c7d" stroke-width=".2"/>')
    svg.append('<path d="M57 5 C65 5 68 5 77 5" fill="none" stroke="#788699" stroke-width=".7" stroke-dasharray="1 1"/><text x="58" y="0" font-size="1.5" font-family="sans-serif">tether schematic</text>')
    svg.append('<path d="M0 18H57 M0 17V19 M57 17V19" stroke="#273d50" stroke-width=".15"/><text x="15" y="22" font-size="2" font-family="sans-serif">Head assembly: 57 x 10 mm flat span</text><text x="0" y="34" font-size="1.8" font-family="sans-serif">BODY PLACEMENT STUDY - no routing, selected cable, or qualified optics</text></svg>')
    (OUT/'placement.svg').write_text(''.join(svg),encoding='utf-8')
    (OUT/'kicad-validation.json').write_text(json.dumps({'native_sheets_exported':len(schematics),'status':'KiCad CLI parsed and exported all architecture sheets','electrical_connectivity_validated':False,'sheets':[{'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in schematics]},indent=2))
    print('PLACEMENT_AND_KICAD_OK',data['checks'])

if __name__=='__main__':main()
