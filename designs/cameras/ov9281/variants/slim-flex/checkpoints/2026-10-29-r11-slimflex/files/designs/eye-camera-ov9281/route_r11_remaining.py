"""Resume-safe ordinary routing; preserve the checked locked data paths."""
from pathlib import Path
import argparse,json,math,time
import pcbnew as p
from routing_r11 import *

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'generated/ov9281-r11-electronics'
RECORD=ROOT/'designs/eye-camera-ov9281/electronics/r11/ordinary-routing.json'

def save(b,record):
    p.SaveBoard(str(OUT/'camera.kicad_pcb'),b)
    RECORD.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')

def ground(b,record):
    if not list(b.Zones()):
        z=p.ZONE(b);z.SetLayer(p.In3_Cu);z.SetNetCode(b.FindNet('GND').GetNetCode())
        z.SetLocalClearance(p.FromMM(.075));z.SetMinThickness(p.FromMM(.075));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
        poly=z.Outline();poly.NewOutline()
        for x,y in POLYGON:poly.Append(p.FromMM(x),p.FromMM(y))
        # Keep the reference beneath all signal lanes solid. Two vent rows are
        # provisional manufacturing features, subject to the flex vendor review.
        for x in range(29,61):
            for y in [3.5,10.5]:
                hole=poly.NewHole(0)
                for i in range(20):
                    a=2*math.pi*i/20;poly.Append(p.FromMM(x+.15*math.cos(a)),p.FromMM(y+.15*math.sin(a)),0,hole)
        b.Add(z)
    missing=[];clear=Clearance(b,'GND',.15)
    pads=sorted([q for q in b.GetPads() if q.GetNetname()=='GND'],key=lambda q:(q.GetParentFootprint().GetReference(),q.GetNumber()))
    for pad in pads:
        q=xy(pad.GetPosition());layer=next(l for l in [p.F_Cu,p.B_Cu] if pad.IsOnLayer(l))
        candidates=[q]+[(q[0]+dx,q[1]+dy) for radius in [.2,.35,.5,.7,1] for dx,dy in [(radius,0),(-radius,0),(0,radius),(0,-radius),(radius,radius),(-radius,radius),(radius,-radius),(-radius,-radius)]]
        point=next((t for t in candidates if clear.via(*t,layer,p.In3_Cu) and clear.segment(pad.GetPosition(),v(*t),layer)),None)
        if point is None:missing.append(pad.GetParentFootprint().GetReference()+'.'+pad.GetNumber());continue
        via_stack(b,point,layer,p.In3_Cu,'GND');track(b,[q,point],layer,'GND',.15)
    # Distributed thermal/return connections beneath the QFN exposed pad.
    for x in [11.5,13,14.5,16]:
        for y in [4.5,6,7.5,9]:
            if clear.via(x,y,p.F_Cu,p.In3_Cu):via_stack(b,(x,y),p.F_Cu,p.In3_Cu,'GND')
    for x,y in [(18.25,4.55),(18.25,5.25),(18.25,5.95)]:
        if clear.via(x,y,p.F_Cu,p.In3_Cu) and clear.segment(v(17.7,y),v(x,y),p.F_Cu):
            via_stack(b,(x,y),p.F_Cu,p.In3_Cu,'GND');track(b,[(17.7,y),(x,y)],p.F_Cu,'GND',.15)
    p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
    record['ground']={'pad_stitch_unresolved':missing,'plane':'In3.Cu','vent_rows_mm':[3.5,10.5],'vent_diameter_mm':.3,'vent_pitch_mm':1,'vendor_approval_required':True}
    save(b,record);print('Ground plane; unstitched pads:',missing,flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--net');ap.add_argument('--width',type=float);ap.add_argument('--nodes',type=int,default=35000);ap.add_argument('--ground-only',action='store_true');args=ap.parse_args()
    b=p.LoadBoard(str(OUT/'camera.kicad_pcb'))
    record=json.loads(RECORD.read_text()) if RECORD.exists() else {'routes':[],'failures':[]}
    if 'ground' not in record:ground(b,record)
    if args.ground_only:return
    nets={q.GetNetname() for q in b.GetPads() if q.GetNetname()}
    def priority(n):
        if n in ['/P4_SW','/SYS_SW']:return 0
        if 'XTAL' in n or 'CLK24' in n or 'MCLK' in n:return 1
        if n in ['/P4_VDD_HP','+3V3','/USB_VBUS','+1V2','+1V8','+2V8']:return 2
        if 'FLASH' in n:return 3
        return 4
    record['failures']=[]
    for net in ([args.net] if args.net else sorted(nets,key=lambda n:(priority(n),n))):
        attempts=0
        while len(groups(b,net))>1 and attempts<150:
            widths=[args.width] if args.width else ([.3,.15] if net in ['/P4_VDD_HP','+3V3','/USB_VBUS','+1V2','+1V8','+2V8'] or net.endswith('_SW') else [.075])
            result=None;before=len(groups(b,net));started=time.time()
            for width in widths:
                result=join(b,net,width,args.nodes)
                if result is None or result['result']=='routed':break
            if not result:break
            result.update(net=net,elapsed_s=round(time.time()-started,3));attempts+=1
            if result['result']!='routed':
                record['failures'].append(result);save(b,record);print(net,result,flush=True);break
            record['routes'].append(result)
            if net=='GND':p.ZONE_FILLER(b).Fill(b.Zones())
            after=len(groups(b,net));save(b,record);print(net,before,'->',after,'islands',result['width_mm'],'mm',result['elapsed_s'],'s',flush=True)
            if after>=before:raise RuntimeError((net,'route did not reduce islands',before,after))
    p.ZONE_FILLER(b).Fill(b.Zones());save(b,record)
    summary={n:len(groups(b,n)) for n in sorted(nets) if len(groups(b,n))>1}
    record['remaining_islands']=summary;save(b,record);print('Remaining',summary,flush=True)

if __name__=='__main__':main()
