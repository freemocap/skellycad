"""Floor-first five-view overlap with square sensors and a floor-fitted top view."""
from pathlib import Path
import json,itertools,copy
import numpy as np
from geometry import grid,visibility,evaluate,summary,project
HERE=Path(__file__).resolve().parent
OUT=HERE.parents[2]/'generated/enclosure/capture-study-r04'

def layout(s,height,aim,hfov,roll):
    cams=[]
    for i,(x,y) in enumerate(((45,45),(455,45),(455,455),(45,455))):
        cams.append(dict(id=f'C{i+1}',position_mm=[x,y,height],target_mm=[250,250,aim],up=[0,0,1],roll_deg=roll,
            sensor_mm=[5.544,5.544],pixels=[1386,1386],focal_mm=5.544/(2*np.tan(np.deg2rad(hfov/2)))))
    h=s['top_optical_height_mm'];side=s['top_sensor_mm'][0]
    cams.append(dict(id='Top',position_mm=[250,250,h],target_mm=[250,250,0],up=[0,1,0],roll_deg=0,
        sensor_mm=[side,side],pixels=s['top_pixels'],focal_mm=side*(1-2*s['edge_margin'])*h/500))
    for c in cams:c.update(near_mm=s['near_mm'],far_mm=s['far_mm'],edge_margin=s['edge_margin'])
    return cams

def metrics(cams,points):
    count=np.sum([visibility(c,points)[0] for c in cams],axis=0)
    return {str(n):float(np.mean(count>=n)*100) for n in (2,3,4,5)}

def main():
    OUT.mkdir(parents=True,exist_ok=True);s=json.loads((HERE/'study.json').read_text())
    floor=grid(25,floor=True);lower=grid(25,height=200)
    trials=[]
    for height,aim,fov,roll in itertools.product((250,275,300),(-100,-50,0,50,100,150),(70,80,90,100,110,120),(0,15,30,45)):
        cams=layout(s,height,aim,fov,roll);fm=metrics(cams,floor);lm=metrics(cams,lower)
        trials.append(dict(parameters=dict(height_mm=height,aim_height_mm=aim,hfov_deg=fov,roll_deg=roll),cameras=cams,
            floor=fm,lower=lm,score=.6*fm['5']+.4*lm['5']))
    # Prefer narrower lenses among equal-coverage candidates, then a smaller tilt.
    trials.sort(key=lambda t:(t['score'],-t['parameters']['hfov_deg'],t['parameters']['aim_height_mm']),reverse=True)
    best=trials[0]
    # Denser verification of the leading candidates rejects coarse-grid tie artifacts.
    finefloor=grid(12.5,floor=True);finelower=grid(12.5,height=200)
    candidates=trials[:24]
    for t in candidates:
        t['floor']=metrics(t['cameras'],finefloor);t['lower']=metrics(t['cameras'],finelower)
        t['score']=.6*t['floor']['5']+.4*t['lower']['5']
    best=max(candidates,key=lambda t:(t['score'],-t['parameters']['hfov_deg'],t['parameters']['aim_height_mm']))
    cams=best['cameras']
    corners=np.array([[0,0,0],[500,0,0],[500,500,0],[0,500,0]])
    uv,_,_=project(cams[-1],corners)
    assert np.allclose(np.abs(uv),np.array(cams[-1]['pixels'])*(.5-s['edge_margin']))
    assert all(c['sensor_mm'][0]==c['sensor_mm'][1] and c['pixels'][0]==c['pixels'][1] for c in cams)
    old=json.loads((OUT.parent/'capture-study-r03/selected-layout.json').read_text())['cameras']
    results={}
    for name,cs in [('R03',old),('R04',cams)]:
        results[name]={}
        for region,p in [('floor',finefloor),('lower',finelower),('cube',grid(25))]:
            results[name][region]={'geometric':metrics(cs,p),'with_body_occlusion':summary(evaluate(cs,p,s))}
    slices=[]
    for z in range(0,201,25):
        p=grid(12.5,floor=True);p[:,2]=z
        slices.append({'height_mm':z,'top_max_square_width_mm':500*(1-z/450),'coverage':metrics(cams,p)})
    # Top-only bound obtained by integrating the square footprint from z=0 to 200.
    bound=100*(1-200/450+200**2/(3*450**2))
    report=dict(candidate_count=len(trials),selected_parameters=best['parameters'],comparisons=results,
        top_floor_corner_pixels=uv.tolist(),top_only_lower_volume_upper_bound_pct=bound,height_slices=slices,
        objective='0.6 * five-view floor percentage + 0.4 * five-view lower-volume percentage; narrower lens breaks ties',
        scope='Ideal geometric overlap, not guaranteed tracking; numerical body-occlusion metrics reported separately')
    for name,data in [('selected-layout.json',best),('results.json',report),('shortlist.json',candidates)]:
        (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
