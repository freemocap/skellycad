"""Save the approved corrective phase's cross-section evidence; no PCB edits."""
from pathlib import Path
import json
from cross_section import solve

OUT=Path(__file__).resolve().parent/'electronics/r10'
RIGID=dict(height=.0705,copper=.035,er=4.21,coat=.02,coat_er=3.8,conformal=True)
FLEX=dict(height=.065,copper=.024,er=3.4,coat=.0275,coat_er=3.4)

def main():
    OUT.mkdir(exist_ok=True)
    reports={}
    for name,width,gap,target,base in [('mipi_rigid',.1,.35,100,RIGID),('usb_rigid',.1,.15,90,RIGID),('mipi_flex',.1,.25,100,FLEX)]:
        settings=dict(width=width,gap=gap,guard_gap=.35,**base)
        runs=[solve(**settings,step=s,domain=1.) for s in [.005,.0025,.00125]]
        # Sensitivity envelope, not supplier-guaranteed manufacturing tolerances.
        corners=[]
        for sign in [-1,1]:
            corner=dict(settings,width=width+sign*.01,gap=gap-sign*.02,
                        height=base['height']*(1-sign*.1),er=base['er']+sign*.2,
                        copper=base['copper']+sign*.005,coat=base['coat']+sign*.01)
            corners.append(solve(**corner,step=.0025,domain=1.))
        expanded=solve(**settings,step=.0025,domain=1.5)
        reports[name]={'target_ohm':target,'nominal':runs[-1],'mesh':runs,
                       'expanded_domain':expanded,'sensitivity_corners':corners}
        print(name,round(runs[-1]['zdiff_ohm'],3),[round(x['zdiff_ohm'],3) for x in corners],flush=True)
    (OUT/'cross-sections.json').write_text(json.dumps(reports,indent=2)+'\n')

if __name__=='__main__':main()
