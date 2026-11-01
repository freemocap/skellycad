"""Nominal pinhole lens screen for the selected budget USB camera baseline."""
from pathlib import Path
import sys, json, itertools
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'capture-study-r04'))
from optimize import layout, metrics
from geometry import grid

def main():
    settings=json.loads((HERE.parent/'capture-study-r04/study.json').read_text())
    out=HERE.parents[2]/'generated/enclosure/usb-baseline-r06'
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    floor=grid(25,floor=True);lower=grid(25,height=200)
    for focal in (1.5,1.8,2.1):
        trials=[]
        for height,aim,roll in itertools.product((250,275,300),(-100,-50,0,50,100,150),(0,15,30,45)):
            cams=layout(settings,height,aim,100,roll)
            for i,c in enumerate(cams):
                c.update(sensor_mm=[3.6,3.6],pixels=[1024,1024],focal_mm=focal if i<4 else 2.8)
            fm=metrics(cams,floor);lm=metrics(cams,lower)
            trials.append(dict(cameras=cams,parameters=dict(height_mm=height,aim_height_mm=aim,roll_deg=roll,corner_focal_mm=focal,top_focal_mm=2.8),score=.6*fm['5']+.4*lm['5']))
        bests=sorted(trials,key=lambda t:t['score'],reverse=True)[:12]
        for t in bests:
            t['floor']=metrics(t['cameras'],grid(12.5,floor=True))
            t['lower']=metrics(t['cameras'],grid(12.5,height=200))
            t['score']=.6*t['floor']['5']+.4*t['lower']['5']
        results.append(max(bests,key=lambda t:t['score']))
    selected=results[-1]
    report=dict(selected_hardware='IADIY CM2M60M12QG',candidate_results=results,
        scope='Ideal pinhole sensitivity screen; actual lens distortion and stream-to-sensor mapping unverified. No hardware tested.',
        top_floor_width_mm=.9*3.6*450/2.8,
        focal_for_r04_corner_fov_mm=3.6/(2*np.tan(np.deg2rad(50))),
        top_exact_floor_fit_focal_mm=.9*3.6*450/500)
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'selected-layout.json').write_text(json.dumps(selected,indent=2)+'\n')
    assert all(250<=c['position_mm'][2]<=300 for c in selected['cameras'][:4])
    assert all(c['pixels']==[1024,1024] for c in selected['cameras'])
    print(json.dumps([{k:t[k] for k in ('parameters','floor','lower')} for t in results],indent=2))

if __name__=='__main__':main()
