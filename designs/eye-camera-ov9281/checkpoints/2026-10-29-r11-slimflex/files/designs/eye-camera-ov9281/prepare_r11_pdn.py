"""Short local pad stitches and broad controller power distribution."""
import json,shutil
from route_r11_remaining import *

def main():
    target=OUT/'camera.kicad_pcb';trial=OUT/'trials/before-pdn-02.kicad_pcb'
    assert not trial.exists();shutil.copy2(target,trial)
    b=p.LoadBoard(str(target));record=json.loads(RECORD.read_text());record.pop('ground',None)
    for t in list(b.GetTracks()):
        if t.GetNetname() in ['GND','/P4_VDD_HP','/USB_VBUS'] or (t.GetNetname()=='+3V3' and not t.IsLocked()):b.Delete(t)
    for z in list(b.Zones()):b.Delete(z)
    ground(b,record)
    for net,layer,points in [('/P4_VDD_HP',p.In1_Cu,[(8.5,1.7),(18.3,1.7),(18.3,12.3),(8.5,12.3)]),
                             ('+3V3',p.In4_Cu,[(.35,.35),(26.8,.35),(27.6,3.4),(27.6,10.6),(26.8,13.65),(.35,13.65)])]:
        z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(b.FindNet(net).GetNetCode());z.SetLocalClearance(p.FromMM(.075));z.SetMinThickness(p.FromMM(.075));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
        poly=z.Outline();poly.NewOutline()
        for x,y in points:poly.Append(p.FromMM(x),p.FromMM(y))
        b.Add(z);clear=Clearance(b,net,.15);missing=[]
        for pad in [q for q in b.GetPads() if q.GetNetname()==net and xy(q.GetPosition())[0]<28]:
            q=xy(pad.GetPosition());side=next(l for l in [p.F_Cu,p.B_Cu] if pad.IsOnLayer(l))
            candidates=[q]+[(q[0]+dx,q[1]+dy) for r in [.2,.35,.5,.7,1] for dx,dy in [(r,0),(-r,0),(0,r),(0,-r),(r,r),(-r,r),(r,-r),(-r,-r)]]
            point=next((t for t in candidates if clear.via(*t,side,layer) and clear.segment(pad.GetPosition(),v(*t),side)),None)
            if point is None:missing.append(pad.GetParentFootprint().GetReference()+'.'+pad.GetNumber());continue
            via_stack(b,point,side,layer,net);track(b,[q,point],side,net,.15)
        if net=='/P4_VDD_HP':
            # Wide regulator-to-plane feed on the layer carrying the core plane.
            clear=Clearance(b,net,.5)
            if clear.segment(v(22,10),v(18,10),layer):track(b,[(22,10),(18,10)],layer,net,.5)
        else:
            # Join the fixed flex supply spine to the controller power plane.
            if clear.via(26.5,10.15,p.In2_Cu,layer):via_stack(b,(26.5,10.15),p.In2_Cu,layer,net)
        record.setdefault('power_planes',{})[net]={'layer':b.GetLayerName(layer),'outline_mm':points,'unstitched':missing}
    p.ZONE_FILLER(b).Fill(b.Zones());save(b,record)
    print(json.dumps(record['power_planes'],indent=2))

if __name__=='__main__':main()
