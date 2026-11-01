"""Actual-footprint, one-sided packing study; deliberately unrouted.

No fabrication clearance or impedance sign-off is implied by rectangle packing.
"""
from pathlib import Path
import json,math,copy,hashlib,subprocess
import pcbnew as p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'generated/three-board-e01'
parts={}
for folder in ['head-interface','base']:
    for ref,v in json.loads((HERE/(folder+'-components.json')).read_text()).items():
        assert ref not in parts,('duplicate cross-board reference',ref)
        v['folder']=folder;parts[ref]=v
def mm(v):return p.ToMM(v)
def vec(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def fpof(v,angle=0):
    fp=p.FootprintLoad(str(OUT/v['folder']/'Camera.pretty'),v['footprint'].split(':')[1]);fp.SetOrientationDegrees(angle);return fp
def bounds(fp):
    b=fp.GetBoundingBox(False,False);return [mm(b.GetX()),mm(b.GetY()),mm(b.GetRight()),mm(b.GetBottom())]
def overlaps(a,b,gap=.10):return a[0]<b[2]+gap and a[2]>b[0]-gap and a[1]<b[3]+gap and a[3]>b[1]-gap
def shifted(b,x,y):return [b[0]+x,b[1]+y,b[2]+x,b[3]+y]
def footprint_body(v):
    fp=fpof(v);bs=[]
    for s in fp.GraphicalItems():
        if type(s).__name__=='PCB_SHAPE' and s.GetLayer()==p.F_Fab:
            b=s.GetBoundingBox();d=mm(s.GetWidth())/2
            bs.append([mm(b.GetX())+d,mm(b.GetY())+d,mm(b.GetRight())-d,mm(b.GetBottom())-d])
    if not bs:bs=[bounds(fp)]
    b=[min(x[0] for x in bs),min(x[1] for x in bs),max(x[2] for x in bs),max(x[3] for x in bs)]
    return [(b[0]+b[2])/2,(b[1]+b[3])/2,b[2]-b[0],b[3]-b[1],v['height_max_mm']]

def pack(region,w,h,mode='net'):
    items={k:v for k,v in parts.items() if v['region']==region};placed={};occupied=[]
    def insert(ref,x,y,angle=0):
        b=shifted(bounds(fpof(items[ref],angle)),x,y)
        if b[0]<.10 or b[1]<.10 or b[2]>w-.10 or b[3]>h-.10:return False
        if any(overlaps(b,z) for z in occupied):return False
        placed[ref]=dict(center=[x,y],angle=angle,bounds=b);occupied.append(b);return True
    if region=='head':
        # Optical datum at package-body center is provisional, not a lens prescription.
        body=footprint_body(items['U1']);assert insert('U1',w/2-body[0],h/2-body[1])
        occupied.append([w/2-4,h/2-4,w/2+4,h/2+4])
        if not insert('D201',1.3,h/2,90) or not insert('D202',w-1.3,h/2,90):return None
        if not insert('Y1',w/2,1.5):return None
    elif region=='interface':
        if not insert('U201',5.5,h/2) or not insert('J201',w-3.55,h/2,90):return None
        occupied.append([0,h/2-2.75,2.3,h/2+2.75])
    else:
        for ref,x,y,angle in [('U101',6.0,6.0,90),('U301',17.0,4.5,0),('J101',w-3.55,h-5.0,90),('J301',w-3.55,5.0,90)]:
            if not insert(ref,x,y,angle):return None
        occupied.append([11.75,4,12.9,8])
    ordered=sorted((r for r in items if r not in placed),key=lambda r:-(bounds(fpof(items[r]))[2]-bounds(fpof(items[r]))[0])*(bounds(fpof(items[r]))[3]-bounds(fpof(items[r]))[1]))
    for ref in ordered:
        v=items[ref];nets=set(v['pin_nets'].values())-{'GND',None,'+3V3','H1V8','H5V','B5V'}
        anchors=[a['center'] for k,a in placed.items() if nets&set(items[k]['pin_nets'].values())]
        target=[sum(a[i] for a in anchors)/len(anchors) for i in (0,1)] if anchors else [w/2,h/2]
        best=None
        for angle in (0,90):
            b=bounds(fpof(v,angle))
            xs={.15-b[0],w-.15-b[2]};ys={.15-b[1],h-.15-b[3]}
            for z in occupied:
                xs.update([z[2]+.101-b[0],z[0]-.101-b[2]])
                ys.update([z[3]+.101-b[1],z[1]-.101-b[3]])
            for x in sorted(xs):
                if x+b[0]<.149 or x+b[2]>w-.149:continue
                for y in sorted(ys):
                    if y+b[1]<.149 or y+b[3]>h-.149:continue
                    score=y*100+x if mode=='bottom' else x*100+y if mode=='left' else (x-target[0])**2+(y-target[1])**2
                    if best and score>=best[0]:continue
                    box=shifted(b,x,y)
                    if not any(overlaps(box,z) for z in occupied):best=(score,x,y,angle)
        if not best:
            print('envelope exhausted',region,w,h,'at',ref,'after',len(placed),'parts',flush=True)
            return None
        assert insert(ref,best[1],best[2],best[3])
    return placed

choices={'head':[(14,12),(14,14),(16,14),(18,14)],'interface':[(18,12),(20,12),(22,12),(22,14),(24,14)],'base':[(30,25),(32,25),(34,26)]}
selected={};boards={};attempts=[]
for region,opts in choices.items():
    for w,h in opts:
        result=None
        for mode in ['net','bottom','left']:
            result=pack(region,w,h,mode);attempts.append([region,w,h,mode,result is not None])
            if result is not None:break
        if result is not None:selected.update(result);boards[region]={'size':[w,h],'thickness':.4 if region=='base' else .303};print('packed',region,w,h,flush=True);break
    else:raise RuntimeError('No tested envelope fits '+region)
boards['head']['origin']=[0,0];boards['interface']['origin']=[boards['head']['size'][0]+25,(boards['head']['size'][1]-boards['interface']['size'][1])/2]
span=boards['interface']['origin'][0]+boards['interface']['size'][0];boards['base']['origin']=[span+18,0]
rows=[]
for ref,v in parts.items():
    rows.append(dict(ref=ref,board=v['region'],mpn=v['mpn'],value=v['value'],populated=v['populated'],**selected[ref],body=footprint_body(v),mass_g=v['mass_g'],folder=v['folder']))
layout={'revision':'THREE-BOARD-E01','units':'mm','boards':boards,'parts':rows,'attempts':attempts,'local_flex_mm':[25,5.5,.166],'flat_head_span_mm':span,'kind':'Actual footprints, pin-net connected, one-sided placement study; no routes',
 'routing_reserves':'Lens keepout; 5.5 mm flex; receiver-to-P4 corridor; no demonstrated routing closure','body_evidence':'XY from footprint F.Fab outlines; Z from component envelope; not manufacturer solid models'}
(HERE/'placement.json').write_text(json.dumps(layout,indent=2)+'\n')

def build_pcb(name,regions):
    board=p.BOARD();board.SetCopperLayerCount(4);board.GetDesignSettings().SetBoardThickness(p.FromMM(.4 if name=='base' else .303))
    nets={}
    for v in parts.values():
        if v['region'] in regions:
            for net in v['pin_nets'].values():
                if net and net not in nets:nets[net]=p.NETINFO_ITEM(board,net);board.Add(nets[net])
    for row in rows:
        if row['board'] not in regions:continue
        v=parts[row['ref']];fp=fpof(v,row['angle']);fp.SetReference(row['ref']);fp.SetValue(v['value']);fp.SetFPID(p.LIB_ID('Camera',v['footprint'].split(':')[1]))
        origin=boards[row['board']]['origin'] if name=='head-interface' else [0,0]
        fp.SetPosition(vec(100+origin[0]+row['center'][0],100+origin[1]+row['center'][1]));fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
        for pad in fp.Pads():
            net=v['pin_nets'].get(pad.GetNumber())
            if net:pad.SetNet(nets[net])
        if not v['populated']:fp.SetDNP(True)
        board.Add(fp)
    if name=='base':w,h=boards['base']['size'];outline=[(0,0),(w,0),(w,h),(0,h)]
    else:
        hw,hh=boards['head']['size'];ix,iy=boards['interface']['origin'];iw,ih=boards['interface']['size'];lo=(hh-5.5)/2;hi=lo+5.5
        outline=[(0,0),(hw,0),(hw,lo),(ix,lo),(ix,iy),(ix+iw,iy),(ix+iw,iy+ih),(ix,iy+ih),(ix,hi),(hw,hi),(hw,hh),(0,hh)]
    for a,b in zip(outline,outline[1:]+outline[:1]):
        if a==b:continue
        s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(vec(100+a[0],100+a[1]));s.SetEnd(vec(100+b[0],100+b[1]));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));board.Add(s)
    text=p.PCB_TEXT(board);text.SetText('E01 / UNROUTED PLACEMENT STUDY / mm');text.SetPosition(vec(100,96));text.SetTextSize(vec(.8,.8));text.SetLayer(p.Dwgs_User);board.Add(text)
    dest=OUT/name/'camera.kicad_pcb';p.SaveBoard(str(dest),board)
    reread=p.LoadBoard(str(dest))
    expected=json.loads((HERE/(name+'-components.json')).read_text())
    assert {fp.GetReference() for fp in reread.GetFootprints()}==set(expected)
    padrows=[]
    for fp in reread.GetFootprints():
        for pad in fp.Pads():
            net=expected[fp.GetReference()]['pin_nets'].get(pad.GetNumber())
            assert (pad.GetNetname() or None)==net,(fp.GetReference(),pad.GetNumber(),net,pad.GetNetname())
            padrows.append({'ref':fp.GetReference(),'pin':pad.GetNumber(),'net':pad.GetNetname(),'xy':[mm(pad.GetPosition().x)-100,mm(pad.GetPosition().y)-100],'size':[mm(pad.GetSize().x),mm(pad.GetSize().y)],'angle':pad.GetOrientationDegrees()})
    (OUT/name/'cad-pads.json').write_text(json.dumps(padrows,indent=2)+'\n')
    assert len(list(reread.GetTracks()))==0
    return {'file':str(dest.relative_to(ROOT)),'footprints':len(list(reread.GetFootprints())),'tracks':0,'copper_layers':4,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
report={'boards':[build_pcb('head-interface',['head','interface']),build_pcb('base',['base'])],'placement_clearance_mm':.10,'placement_collisions':[], 'routing_complete':False}
for reg,b in boards.items():
    these=[x for x in rows if x['board']==reg]
    for i,a in enumerate(these):
        for other in these[i+1:]:assert not overlaps(a['bounds'],other['bounds']),[reg,a['ref'],other['ref']]
(OUT/'pcb-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Saved actual-footprint boards; no routes',flush=True)
