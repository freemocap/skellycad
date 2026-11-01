"""Reserve the sensor's laser-via escapes before ordinary local routing."""
import shutil,json
from route_r11_remaining import *

def main():
    path=OUT/'camera.kicad_pcb';trial=OUT/'trials/before-sensor-escapes-02.kicad_pcb';assert not trial.exists();shutil.copy2(path,trial)
    b=p.LoadBoard(str(path));sensor=next(f for f in b.GetFootprints() if f.GetReference()=='U1')
    nets={q.GetNetname() for q in sensor.Pads() if q.GetNetname() and q.GetNetname()!='GND' and not q.GetNetname().startswith('/CAM_L_')}
    for t in list(b.GetTracks()):
        if t.GetNetname() in nets and not t.IsLocked():b.Delete(t)
    failures=[];escapes=[]
    for pad in sensor.Pads():
        net=pad.GetNetname()
        if net not in nets:continue
        x,y=xy(pad.GetPosition());circle=p.SHAPE_CIRCLE(v(x,y),125000)
        # Ordinary ground escape segments can be rerouted after the CSP vias
        # are reserved. Preserve every locked signal and all existing vias.
        for t in list(b.GetTracks()):
            if not isinstance(t,p.PCB_VIA) and not t.IsLocked() and t.GetNetname()=='GND' and t.GetLayer() in [p.F_Cu,p.In1_Cu] and t.GetEffectiveShape(t.GetLayer()).Collide(circle,76000):b.Delete(t)
        clear=Clearance(b,net,.075)
        if not clear.via(x,y,p.F_Cu,p.In1_Cu):failures.append(pad.GetNumber());continue
        via_stack(b,(x,y),p.F_Cu,p.In1_Cu,net);escapes.append(pad.GetNumber())
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    (OUT/'sensor-escapes.json').write_text(json.dumps({'reserved_pads':escapes,'failures':failures,'construction':'Filled/capped adjacent F-In1 laser vias; supplier qualification required'},indent=2)+'\n')
    print('Reserved',len(escapes),'sensor pad escapes; failures',failures)

if __name__=='__main__':main()
