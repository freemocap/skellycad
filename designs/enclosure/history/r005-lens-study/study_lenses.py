"""Constrained zoom comparison and illustrative thin-lens defocus screen."""
from pathlib import Path
import sys,json,itertools,copy
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'capture-study-r04'))
from optimize import layout,metrics
from geometry import grid,project,visibility
OUT=HERE.parents[2]/'generated/enclosure/lens-study-r05'

def blur_mm(f,number,focus,z):
    """Paraxial defocus-circle diameter at the sensor, axial object distance in mm."""
    v0=f*focus/(focus-f);v=f*z/(z-f)
    return (f/number)*np.abs(v0-v)/v

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    settings=json.loads((HERE.parent/'capture-study-r04/study.json').read_text())
    floor=grid(25,floor=True);lower=grid(25,height=200)
    cases={};selected=None
    for name,side in [('R04-synthetic-sensors',None),('AR0234-square-ROI',3.6)]:
        trials=[]
        # 5 mm is widest throughout 5-50 mm: every larger focal length gives a
        # subset of the same pose's frustum. Coverage-only optimum is at 5 mm.
        for h,a,r in itertools.product((250,275,300),(-100,-50,0,50,100,150,200),(0,15,30,45)):
            cams=layout(settings,h,a,100,r)
            for c in cams:
                c['focal_mm']=5.
                if side:c['sensor_mm']=[side,side];c['pixels']=[1200,1200]
            fm=metrics(cams,floor);lm=metrics(cams,lower)
            trials.append(dict(cameras=cams,score=.6*fm['5']+.4*lm['5'],parameters=dict(height_mm=h,aim_mm=a,roll_deg=r,focal_mm=5)))
        ranked=sorted(trials,key=lambda t:t['score'],reverse=True)[:12]
        finefloor=grid(12.5,floor=True);finelower=grid(12.5,height=200)
        for t in ranked:
            t['floor']=metrics(t['cameras'],finefloor);t['lower']=metrics(t['cameras'],finelower)
            t['score']=.6*t['floor']['5']+.4*t['lower']['5']
        best=max(ranked,key=lambda t:t['score']);cases[name]=best
        if selected is None:selected=best
    # Keep lens changes separate from pose changes in the zoom curve.
    curve=[]
    for f in (5,6,8,12,25,50):
        cams=copy.deepcopy(selected['cameras'])
        for c in cams:c['focal_mm']=f
        curve.append({'focal_mm':f,'floor':metrics(cams,floor),'lower':metrics(cams,lower)})
    # Per-camera optimal focus plane: maximize weighted, geometrically visible
    # floor/lower samples satisfying a TWO-PIXEL geometric defocus diameter.
    points=np.concatenate([floor,lower]);weights=np.concatenate([np.full(len(floor),.6/len(floor)),np.full(len(lower),.4/len(lower))])
    screens=[]
    for number in (1.6,2.8,4,5.6,8):
        masks=[];focus_settings=[]
        for c in selected['cameras']:
            visible=visibility(c,points)[0];_,xyz,_=project(c,points);z=xyz[:,2]
            limit=2*min(np.array(c['sensor_mm'])/c['pixels'])
            options=[]
            for focus in np.arange(150,801,10):
                mask=visible&(z>c['focal_mm'])&(blur_mm(c['focal_mm'],number,focus,np.maximum(z,6))<=limit)
                options.append((float(np.sum(weights*mask)),float(focus),mask))
            _,focus,mask=max(options,key=lambda x:x[0]);focus_settings.append(focus);masks.append(mask)
        allfive=np.all(masks,axis=0)
        screens.append(dict(f_number=number,focus_axial_mm=focus_settings,
            floor_allfive_defocus_pass_pct=float(np.mean(allfive[:len(floor)])*100),
            lower_allfive_defocus_pass_pct=float(np.mean(allfive[len(floor):])*100),
            relative_light_to_f16=(1.6/number)**2))
    report={'cases':cases,'zoom_curve_fixed_pose':curve,'defocus_screen':screens,
        'assumptions':['5-50 mm hard focal range; exact lens identity and minimum focus unverified',
        'Synthetic sensors may exceed image circle of a lens labeled 1/2.7 inch',
        'Thin lens axial distances, 2-pixel defocus threshold; diffraction and aberrations excluded',
        'Focus and aperture availability assumed for screening, not verified ring calibration',
        'Focus-dependent magnification and breathing excluded from pinhole frustums'],
        'r04_focal_mm':[c['focal_mm'] for c in json.loads((OUT.parent/'capture-study-r04/selected-layout.json').read_text())['cameras']]}
    (OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    (OUT/'selected-layout.json').write_text(json.dumps(selected,indent=2)+'\n')
    print(json.dumps({'cases':{k:{p:v[p] for p in ['parameters','floor','lower']} for k,v in cases.items()},'defocus_screen':screens},indent=2),flush=True)

if __name__=='__main__':main()
