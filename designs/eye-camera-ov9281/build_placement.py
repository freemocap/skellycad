"""R03 unrouted physical placement from R02 netlist, with explicit reservations.

Uses pinned footprints [@antmicroOv9281Board; @espressifKicadLibrary;
@kicadFootprintsSource]. Run with KiCad 10.0.7 bundled Python.
"""
from pathlib import Path
import argparse, json, shutil, hashlib, re, subprocess, itertools, csv
import xml.etree.ElementTree as ET
import pcbnew as p

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
KICAD=Path('C:/Users/jonma/AppData/Local/Programs/KiCad/10.0')
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
OUT=parser.parse_args().output.resolve()
if OUT.exists():raise SystemExit('Choose a new output directory; preserve open revisions.')
OUT.mkdir(parents=True)
SRC=ROOT/'electronics/r02'
LIB=OUT/'Camera.pretty';shutil.copytree(SRC/'Camera.pretty',LIB)
mm=p.FromMM
def v(x,y):return p.VECTOR2I(mm(x),mm(y))
subprocess.run([str(KICAD/'bin/kicad-cli.exe'),'sch','export','netlist','--format','kicadxml','--output',str(OUT/'source-netlist.xml'),str(SRC/'camera.kicad_sch')],check=True)
xml=ET.parse(OUT/'source-netlist.xml')
components={c.get('ref'):{'value':c.findtext('value'),'footprint':c.findtext('footprint') or '', 'symbol_uuid':c.findtext('tstamps')} for c in xml.findall('.//components/comp')}
netmap={}
for net in xml.findall('.//nets/net'):
    for n in net.findall('node'):netmap[(n.get('ref'),n.get('pin'))]=net.get('name')
head=set('U1 Y1 L1 L2 L3 C7 C8 C9 C10 C12 C13 C14 C15 C16 C17 C18 C19 C20 C21 C33 R7 R8 R9'.split())
assert len(head)==23
excluded={'J102':'Logical flex interface; exact connector and flex not selected',
          'J104':'LED interface placeholder; current driver and emitter not selected'}
overrides={}
for ref,c in components.items():
    if ref.startswith('C') and int(ref[1:])>=100:
        value=c['value'].split()[0]
        size='0805_2012' if value in {'10u','22u'} else ('0603_1608' if value in {'1u','4.7u'} else None)
        if size:
            name=f'C_{size}Metric';source=KICAD/'share/kicad/footprints/Capacitor_SMD.pretty'/f'{name}.kicad_mod'
            
            if not (LIB/source.name).exists():shutil.copy2(source,LIB/source.name)
            overrides[ref]={'before':c['footprint'],'after':'Camera:'+name,'reason':'Conservative placement allowance; effective capacitance and exact MPN pending'}
            c['footprint']='Camera:'+name
components['J103']['footprint']='Camera:ProgrammingPads_5x1mm_P1.5mm'
overrides['J103']={'before':'','after':components['J103']['footprint'],'reason':'Custom five PCB test pads; not a packaged connector'}
custom='(footprint "ProgrammingPads_5x1mm_P1.5mm" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr smd)\n'
for i in range(5):
    custom+=f'(pad "{i+1}" smd circle (at {i*1.5} 0) (size 1 1) (layers "F.Cu" "F.Mask"))\n'
(LIB/'ProgrammingPads_5x1mm_P1.5mm.kicad_mod').write_text(custom+')\n')

# Actual footprint bounding boxes include pads and graphics, excluding text.
# Reserved rectangles are chosen spatial budgets, not invented component models.
SPECS={
 'controller':{'size':[32,20],'thickness':0.6,'origin':[50,50],
               'reserved':[{'name':'FLEX CONNECTOR TBD','side':'front','rect':[19,0.5,31,4.5]}]},
 'head':{'size':[14,14],'thickness':0.6,'origin':[112,53],
         'reserved':[{'name':'LENS/HOLDER BUDGET - TBD','side':'front','rect':[3,2,11,10]},
                     {'name':'IR LED TBD','side':'front','rect':[0.5,4.5,2.5,6.5]},
                     {'name':'IR LED TBD','side':'front','rect':[11.5,4.5,13.5,6.5]},
                     {'name':'FLEX EXIT TBD','side':'front','rect':[3,12.2,11,13.2]}]}}
boards={};placed={};records=[]
def rect(fp):
    b=fp.GetBoundingBox(False,False)
    return [p.ToMM(b.GetX()),p.ToMM(b.GetY()),p.ToMM(b.GetRight()),p.ToMM(b.GetBottom())]
def collide(a,b,gap=0.15):return not(a[2]+gap<=b[0] or b[2]+gap<=a[0] or a[3]+gap<=b[1] or b[3]+gap<=a[1])
def add_line(board,a,b,layer,width=.05):
    x=p.PCB_SHAPE();x.SetShape(p.SHAPE_T_SEGMENT);x.SetStart(v(*a));x.SetEnd(v(*b));x.SetLayer(layer);x.SetWidth(mm(width));board.Add(x)
def box(board,r,layer):
    x,y,X,Y=r
    for a,b in [((x,y),(X,y)),((X,y),(X,Y)),((X,Y),(x,Y)),((x,Y),(x,y))]:add_line(board,a,b,layer)
def text(board,s,x,y,size=.8):
    t=p.PCB_TEXT(board);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(mm(.12));t.SetLayer(p.Dwgs_User);board.Add(t)
def create(name):
    b=p.BOARD();b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(mm(SPECS[name]['thickness']))
    nets={}
    for s in sorted(set(netmap.values())):
        n=p.NETINFO_ITEM(b,s);b.Add(n);nets[s]=n
    boards[name]=(b,nets);placed[name]={'front':[],'back':[]}
    w,h=SPECS[name]['size'];box(b,[0,0,w,h],p.Edge_Cuts)
    for r in SPECS[name]['reserved']:
        box(b,r['rect'],p.Dwgs_User)
        # Sensor sits below the lens; this is an optical reservation only.
        if 'LENS' not in r['name']:placed[name][r['side']].append((r['name'],r['rect']))
    text(b,name.upper()+' / R03 UNROUTED',w/2,-3)
    text(b,f'{w} x {h} mm / 0.6 mm provisional',w/2,-1.5,.65)

def put(ref,name,side,preferred=None,angle=0):
    b,nets=boards[name];c=components[ref];fpname=c['footprint'].split(':')[-1]
    fp=p.FootprintLoad(str(LIB),fpname)
    if not fp:raise ValueError((ref,fpname))
    fp.SetReference(ref);fp.SetValue(c['value']);fp.SetPath(p.KIID_PATH('/e3549937-ce5e-4391-94ab-3d7fcb0b1d31/'+c['symbol_uuid']));fp.SetFPID(p.LIB_ID('Camera',fpname))
    fp.SetPosition(v(0,0));fp.SetOrientationDegrees(angle)
    b.Add(fp)
    if side=='back':fp.Flip(v(0,0),False)
    fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
    # Missing external 3D paths must not imply a complete 3D assembly.
    bounds=rect(fp);width=bounds[2]-bounds[0];height=bounds[3]-bounds[1]
    w,h=SPECS[name]['size']; target=preferred or (w/2,h/2)
    candidates=[]
    for ix in range(3,int((w-width-.75)/.25)+1):
        for iy in range(3,int((h-height-.75)/.25)+1):
            x,y=ix*.25,iy*.25;r=[x,y,x+width,y+height]
            if not any(collide(r,other) for _,other in placed[name][side]):
                candidates.append(((x+width/2-target[0])**2+(y+height/2-target[1])**2,x,y,r))
    if not candidates:
        b.Remove(fp)
        raise RuntimeError(f'No placement space for {ref} on {name} {side}')
    _,x,y,r=min(candidates)
    fp.SetPosition(v(x-bounds[0],y-bounds[1]))
    for pad in fp.Pads():
        net=netmap.get((ref,pad.GetNumber()))
        if net:pad.SetNet(nets[net])
    placed[name][side].append((ref,r))
    records.append({'reference':ref,'board':name,'side':side,'value':c['value'],'footprint':c['footprint'],
                    'anchor_mm':[p.ToMM(fp.GetPosition().x),p.ToMM(fp.GetPosition().y)],
                    'angle_deg':fp.GetOrientationDegrees(),'bounds_mm':rect(fp)})
    return fp

for name in SPECS:create(name)
sensor=put('U1','head','front',(7,6))
# Keep front clear for optics and emitters. Backside holds head support parts.
put('Y1','head','back',(7,3))
for ref in sorted(head-{'U1','Y1'},key=lambda r:(0 if r.startswith('L') else 1,r)):put(ref,'head','back')
put('U101','controller','front',(16,11))
put('J101','controller','front',(4,12),90)
put('U103','controller','front',(26,8))
put('L101','controller','front',(26,12))
put('Y101','controller','front',(8,5))
put('U102','controller','back',(15,7))
put('U104','controller','back',(4,4))
put('L102','controller','back',(4,8))
put('U105','controller','front',(5,7))
put('J103','controller','back',(26,17))
done={r['reference'] for r in records}
remaining=set(components)-head-set(excluded)-done
# Large parts first; subsequent passives are provisional packing, not routing placement.
def area(ref):
    fp=p.FootprintLoad(str(LIB),components[ref]['footprint'].split(':')[-1]);r=rect(fp)
    return (r[2]-r[0])*(r[3]-r[1])
for ref in sorted(remaining,key=lambda r:(-area(r),r)):
    try:put(ref,'controller','back')
    except RuntimeError:put(ref,'controller','front')

for name,(board,nets) in boards.items():
    board.BuildConnectivity();p.SaveBoard(str(OUT/f'{name}.kicad_pcb'),board)
    (OUT/f'{name}.kicad_pro').write_text(json.dumps({'meta':{'filename':name+'.kicad_pro','version':1}},indent=2)+'\n')

# Same-scale assembly review file. Gap is illustrative; no fabricated flex is present.
combined=p.BOARD();combined.GetDesignSettings().SetBoardThickness(mm(.6));combined.SetCopperLayerCount(4)
cn={}
for n in sorted(set(netmap.values())):
    item=p.NETINFO_ITEM(combined,n);combined.Add(item);cn[n]=item
for name,(board,_) in boards.items():
    ox,oy=SPECS[name]['origin'];w,h=SPECS[name]['size'];box(combined,[ox,oy,ox+w,oy+h],p.Edge_Cuts)
    for original in board.GetFootprints():
        fp=p.FOOTPRINT(original);fp.SetPosition(fp.GetPosition()+v(ox,oy));combined.Add(fp)
        for pad in fp.Pads():
            net=netmap.get((fp.GetReference(),pad.GetNumber()))
            if net:pad.SetNet(cn[net])
    for res in SPECS[name]['reserved']:
        x,y,X,Y=res['rect'];box(combined,[ox+x,oy+y,ox+X,oy+Y],p.Dwgs_User)
    text(combined,f'{name.upper()} {w} x {h} mm',ox+w/2,oy-2)
box(combined,[82,58,112,66],p.Dwgs_User)
text(combined,'30 mm gap / flex TBD',97,56,.7)
text(combined,'R03 PLACEMENT ONLY - NO ROUTES - NOT FOR FABRICATION',88,75,.8)
combined.BuildConnectivity();p.SaveBoard(str(OUT/'assembly-placement.kicad_pcb'),combined)
(OUT/'assembly-placement.kicad_pro').write_text('{}\n')
shutil.copy2(SRC/'fp-lib-table',OUT/'fp-lib-table')
shutil.copy2(SRC/'sym-lib-table',OUT/'sym-lib-table')
shutil.copy2(SRC/'Camera.kicad_sym',OUT/'Camera.kicad_sym')
# Preserve a coherent schematic revision with placement-specific footprint overrides.
sys_path=str(ROOT)
import sys
sys.path.insert(0,sys_path)
from extract_head import children
sch=(SRC/'camera.kicad_sch').read_text(encoding='utf-8')
for block in list(children(sch)):
    if not block.startswith('(symbol '):continue
    m=re.search(r'\(property "Reference" "([^"]+)"',block)
    if m and m[1] in overrides:
        changed=re.sub(r'\(property "Footprint" "[^"]*"','(property "Footprint" "'+overrides[m[1]]['after']+'"',block,count=1)
        sch=sch.replace(block,changed)
(OUT/'camera.kicad_sch').write_text(sch,encoding='utf-8');shutil.copy2(SRC/'camera.kicad_pro',OUT/'camera.kicad_pro')
for name in ['LICENSE-Antmicro','LICENSE-Espressif-library.md']:shutil.copy2(SRC/name,OUT/name)
record={'revision':'OV9281-P4-PLACEMENT-R03','units':'mm','source_schematic_sha256':hashlib.sha256((SRC/'camera.kicad_sch').read_bytes()).hexdigest(),
        'board_specs':SPECS,'placements':records,'excluded_logical_symbols':excluded,'footprint_overrides':overrides,
        'status':'Unrouted placement study. Neither production dimensions nor fit-qualified assembly.',
        'limitations':['Optics, LEDs and flex represented only by reservations','Provisional passive footprints and BOM',
                       'No impedance stackup or routing','No solder assembly, power or thermal test','3D component models incomplete']}
(OUT/'placement.json').write_text(json.dumps(record,indent=2)+'\n')
with (OUT/'placement.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['reference','board','side','x_mm','y_mm','angle_deg','footprint','value'])
    for r in records:writer.writerow([r['reference'],r['board'],r['side'],*r['anchor_mm'],r['angle_deg'],r['footprint'],r['value']])
print(json.dumps({'boards':{n:s['size'] for n,s in SPECS.items()},'placed':len(records),'excluded':excluded},indent=2))
