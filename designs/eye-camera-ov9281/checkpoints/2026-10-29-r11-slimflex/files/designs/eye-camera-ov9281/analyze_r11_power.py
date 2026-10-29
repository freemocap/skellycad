"""Conservative sensor-rail conductor/inductor DC screens, not transient proof."""
import json,math
from validate_r11_board import OUT,SPEC,path
from routing_r11 import *
def main():
    b=p.LoadBoard(str(OUT/'camera.kicad_pcb'));tracks={uid(t):t for t in b.GetTracks()};results={}
    def resistance(m):
        total=0
        for row in m['path']:
            t=tracks[row['uuid']]
            if row['kind']=='trace':total+=1.72e-5*math.dist(row['from'][1:],row['to'][1:])/(p.ToMM(t.GetWidth())*(.025 if t.GetLayer() in [p.F_Cu,p.B_Cu] else .018))
            else:
                a,z=sorted([LAYERS.index(t.TopLayer()),LAYERS.index(t.BottomLayer())]);total+=1.72e-5*([.02,.02,.05,.02,.02][a]+.018)/(math.pi*.035**2)
        return total
    for name,u,coil,voltage,minimum,typ in [('DVDD','U6','L1',1.2,1.14,.052),('DOVDD','U5','L2',1.8,1.7,.0025),('AVDD','U7','L3',2.8,2.6,.024)]:
        supply={1.2:'+1V2',1.8:'+1V8',2.8:'+2V8'}[voltage];net='/M1_'+name
        first=path(b,supply,[(u,'1'),(coil,'1')]);r1=resistance(first);paths=[]
        for pad in b.GetPads():
            if pad.GetParentFootprint().GetReference()=='U1' and pad.GetNetname()==net:
                m=path(b,net,[(coil,'2'),('U1',pad.GetNumber())]);paths.append({'pin':pad.GetNumber(),'trace_R_ohm':resistance(m),'centerline_mm':m['path_length_mm']})
        # Entire rail current through its worst pad path is conservative for
        # the distributed load. Add an explicit return-path allowance.
        total=r1+max(q['trace_R_ohm'] for q in paths)+.19*1.3+.01;low=voltage*(1-.014)
        results[name]={'nominal_V':voltage,'LDO_low_V':low,'sensor_minimum_V':minimum,'typical_current_A':typ,'upstream_trace_R_ohm':r1,'filter_max_DCR_ohm':.247,'return_allowance_ohm':.01,'worst_total_series_R_ohm':total,'loaded_low_at_typical_V':low-total*typ,'loaded_low_at_twice_typical_V':low-total*2*typ,'twice_typical_passes_DC_screen':low-total*2*typ>=minimum,'DC_current_at_minimum_V_A':(low-minimum)/total,'pad_paths':paths}
        assert results[name]['loaded_low_at_typical_V']>=minimum
    report={'results':results,'scope':'DC screening with full rail current assigned to its worst routed pad path. 1.4% LDO error, 0.247 ohm maximum inductor DCR (0.19 plus 30 percent) and 0.01 ohm return allowance. Published currents are typical at 1280x800/120 fps, not maximum ratings. The DVDD twice-typical stress case fails; loaded rail margin requires qualification or correction before fabrication. Temperature-dependent conductor resistance, regulator dynamics and rail sequencing remain unqualified. The 0.2 W selection envelope is a dissipation screen, not a guaranteed distribution of rail currents.','sources':['leopardOv9281Electrical2026','tiTlv733R11','tdkMlp2012R11']}
    (SPEC/'sensor-power-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:{n:v for n,v in r.items() if n!='pad_paths'} for k,r in results.items()},indent=2))
if __name__=='__main__':main()
