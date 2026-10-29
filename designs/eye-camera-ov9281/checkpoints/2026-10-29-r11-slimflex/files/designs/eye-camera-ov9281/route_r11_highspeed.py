"""Route and length-balance native CSI/USB paths before ordinary circuitry."""
import json,math,shutil
import pcbnew as p
from build_r11_schematic import OUT,SPEC
from place_r11 import HX,xy
from routing_r11 import track,via_stack,Clearance


def length(points):return sum(math.dist(a,z) for a,z in zip(points,points[1:]))
def offset(points,d):
    directions=[];normals=[]
    for a,z in zip(points,points[1:]):
        dx,dy=z[0]-a[0],z[1]-a[1];r=math.hypot(dx,dy);directions.append((dx/r,dy/r));normals.append((-dy/r,dx/r))
    result=[]
    for i,(x,y) in enumerate(points):
        if i==0:n=normals[0]
        elif i==len(points)-1:n=normals[-1]
        else:
            a,z=normals[i-1],normals[i];den=1+a[0]*z[0]+a[1]*z[1]
            n=((a[0]+z[0])/den,(a[1]+z[1])/den)
        result.append((x+d*n[0],y+d*n[1]))
    return result


def teeth(start,y,count,pitch,amplitude,direction):
    rows=[(start,y)]
    for i in range(count):rows.extend([(start+(i+.5)*pitch,y+direction*amplitude),(start+(i+1)*pitch,y)])
    return rows


def tune(points,extra,side,start=29.0,max_span=6.8,pitch=.4,amax=.14):
    if extra<1e-7:return points
    n=math.ceil(extra/(2*math.hypot(pitch/2,amax)-pitch))
    assert n*pitch<=max_span+1e-8,(extra,n,max_span)
    amp=math.sqrt(((extra/n+pitch)/2)**2-(pitch/2)**2)
    end=start+n*pitch
    for i,(a,z) in enumerate(zip(points,points[1:])):
        if abs(a[1]-z[1])<1e-8 and min(a[0],z[0])<start and max(a[0],z[0])>end:
            wave=teeth(start,a[1],n,pitch,amp,side)
            if a[0]>z[0]:wave.reverse()
            return points[:i+1]+wave+points[i+1:]
    raise ValueError(('No tuning section',extra,start,end))


def main():
    path=OUT/'camera.kicad_pcb';b=p.LoadBoard(str(path));assert not list(b.GetTracks()),'Do not overwrite existing copper'
    shutil.copyfile(path,OUT/'camera-placement.kicad_pcb')
    fps={f.GetReference():f for f in b.GetFootprints()}
    def pad(ref,num):return next(q for q in fps[ref].Pads() if q.GetNumber()==str(num))
    def pt(ref,num):return xy(pad(ref,num).GetPosition())
    pairs={'D0':{'center':6.15,'loop_x':3.6,'loop_y':10.8,'wide_x':5.0,'head_x':5.792,'pins':{'P':('43','G3'),'N':('42','H3')},'p_sign':-1,'wave_n':50,'pitch':.48,'amp_max':.23,'wave_sign':1,'wave_start':36.0},
           'CLK':{'center':5.25,'loop_x':2.7,'loop_y':11.6,'wide_x':6.1,'head_x':6.432,'pins':{'P':('44','G4'),'N':('45','H4')},'p_sign':1,'wave_n':64,'pitch':.45,'amp_max':.15,'wave_sign':-1,'wave_start':20.8},
           'D1':{'center':4.35,'loop_x':1.8,'loop_y':12.4,'wide_x':7.2,'head_x':7.072,'pins':{'P':('47','G5'),'N':('46','F5')},'p_sign':-1,'wave_n':0,'pitch':.5,'amp_max':0,'wave_sign':1,'wave_start':37.0}}
    def paths(name,amp):
        q=pairs[name];y=q['center'];center=[(20.3,y)]
        if amp>1e-9:center+=teeth(q['wave_start'],y,q['wave_n'],q['pitch'],amp,q['wave_sign'])
        if name=='D0':
            center += [(HX+1.8,y),(HX+1.8,10.8),(HX+q['head_x'],10.8),(HX+q['head_x'],9.4)]
        elif name=='CLK':
            center += [(HX+2.7,y),(HX+2.7,6.8),(HX+4.2,6.8),(HX+4.2,5.1),(HX+5.3,5.1),(HX+5.3,6.8),(HX+q['head_x'],6.8),(HX+q['head_x'],7.1)]
        else:
            center += [(HX+10.5,y),(HX+10.5,7.964),(HX+8,7.964)]
        result={}
        for polarity,(cp,hp) in q['pins'].items():
            sign=q['p_sign']*(1 if polarity=='P' else -1)
            points=offset(center,sign*.1625);sensor=pt('U1',hp);cx=HX+q['head_x']
            other=pt('U1',q['pins']['N' if polarity=='P' else 'P'][1])
            if name=='D0' and sensor[1]<other[1]:
                side=-1 if points[-1][0]<cx else 1
                points.extend([(cx+side*.32,9.1),(cx+side*.32,sensor[1]),sensor])
            elif name=='CLK' and sensor[1]>other[1]:
                side=-1 if points[-1][0]<cx else 1
                points.extend([(cx+side*.32,7.4),(cx+side*.32,sensor[1]),sensor])
            else:points.append(sensor)
            result[polarity]=[pt('U101',cp)]+points
        return result
    raw={name:paths(name,0) for name in pairs};target=max(length(points) for rows in raw.values() for points in rows.values())
    report={'units':'mm','reference_layer':'In3.Cu','CSI_signal_layer':'In2.Cu','USB_signal_layer':'F.Cu','pairs':{},'scope':'Geometric routing and uniform cross-section estimate; no hardware signal-integrity qualification'}
    for name,q in pairs.items():
        lo=0.;hi=q['amp_max']
        if hi:
            assert max(map(length,paths(name,hi).values()))>=target,(name,target,max(map(length,paths(name,hi).values())))
            for _ in range(45):
                mid=(lo+hi)/2
                if max(map(length,paths(name,mid).values()))<target:lo=mid
                else:hi=mid
        rows=paths(name,(lo+hi)/2)
        longest=max(map(length,rows.values()))
        for polarity,points in rows.items():
            sign=q['p_sign']*(1 if polarity=='P' else -1)
            rows[polarity]=tune(points,longest-length(points),sign,start=50 if name=='CLK' else 29,max_span=10 if name=='CLK' else 6.8 if name=='D0' else 7.5,amax=.13 if name=='CLK' else .14)
        for polarity,points in rows.items():
            net=f'/CAM_L_{name}_{polarity}';cp,hp=q['pins'][polarity]
            via_stack(b,pt('U101',cp),p.F_Cu,p.In2_Cu,net,True)
            via_stack(b,pt('U1',hp),p.F_Cu,p.In2_Cu,net,True)
            track(b,points,p.In2_Cu,net,.075,True)
        report['pairs'][name]={'width_mm':.075,'uniform_gap_mm':.25,'p_mm':length(rows['P']),'n_mm':length(rows['N']),'difference_mm':abs(length(rows['P'])-length(rows['N'])),'common_wave_amplitude_mm':(lo+hi)/2,'routes':rows}
    # Input-side USB path, including the two flow-through ESD lands.
    inputs={}
    for polarity,j,esd1,esd2,res,sign in [('N','2','1','6','R109',1),('P','3','3','4','R110',-1)]:
        net='/USB_D'+('M' if polarity=='N' else 'P')
        points=[pt('J101',j),pt('U105',esd1),pt('U105',esd2)]
        if polarity=='N':points += [(6.5,pt('U105',esd2)[1]),(7.0,pt(res,1)[1])]
        points.append(pt(res,1));inputs[polarity]=points
        track(b,points[:2],p.In2_Cu,net,.075,True)
        via_stack(b,points[0],p.F_Cu,p.In2_Cu,net,True);via_stack(b,points[1],p.F_Cu,p.In2_Cu,net,True)
        track(b,points[1:],p.F_Cu,net,.15,True)
    center=[(19.65,3.5),(21.4,3.5),(21.4,.85),(8.1,.85)]
    usb={}
    for polarity,pin,res,sign in [('N','49','R109',1),('P','50','R110',-1)]:
        tail=[(7.2,.725),(7.2,1.1),pt(res,2)] if polarity=='N' else [(8.15,1.2),(8.15,pt(res,2)[1]),pt(res,2)]
        usb[polarity]=[pt('U101',pin)]+offset(center,sign*.125)+tail
    total={k:length(usb[k])+length(inputs[k])+math.dist(pt('R109' if k=='N' else 'R110',1),pt('R109' if k=='N' else 'R110',2)) for k in usb}
    usb_target=max(total.values())
    for polarity in usb:
        # Above the processor, travel is leftward; outward is toward that trace's Y side.
        outward=-1 if polarity=='N' else 1
        usb[polarity]=tune(usb[polarity],usb_target-total[polarity],outward,start=9.5,max_span=10.2,pitch=.6,amax=.25)
        track(b,usb[polarity],p.F_Cu,'/USB_D'+('M' if polarity=='N' else 'P')+'_CHIP',.15,True)
    report['USB']={'width_mm':.15,'uniform_gap_mm':.1,'p_mm_including_resistor_span':usb_target,'n_mm_including_resistor_span':usb_target,'input_routes':inputs,'chip_routes':usb,'resistor_span_included':True,'ESD_flowthrough_copper_included':True}
    # Continuous neck rails and controls. All layer changes stay in six-layer regions.
    signals=[('/M1_CAM_SCL_1V8',3.4,.1),('/M1_CAM_SDA_1V8',3.65,.1),('/CAM_NRST_1V8',7.15,.1),('/M1_VSYNC_1V8_M',7.4,.1),('/LED_PWM',7.65,.1),('+1V2',8.3,.5),('+2V8',8.95,.35),('+1V8',9.55,.3),('+3V3',10.15,.3)]
    landing_y={'/M1_CAM_SCL_1V8':3.2,'/M1_CAM_SDA_1V8':3.6,'/CAM_NRST_1V8':6.95,'/M1_VSYNC_1V8_M':7.35,'/LED_PWM':7.8}
    for net,y,width in signals:
        end_y=landing_y.get(net,y)
        track(b,[(26.5,y),(HX+.3,y),(HX+1,end_y)],p.In2_Cu,net,width)
        via_stack(b,(HX+1,end_y),p.In2_Cu,p.In4_Cu,net)
    p.SaveBoard(str(path),b)
    (SPEC/'highspeed-routing.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({name:{k:v for k,v in row.items() if k!='routes'} for name,row in report['pairs'].items()},indent=2))


if __name__=='__main__':main()
