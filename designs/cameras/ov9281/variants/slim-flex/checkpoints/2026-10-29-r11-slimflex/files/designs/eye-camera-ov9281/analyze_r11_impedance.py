"""Mesh/domain and material sensitivity for uniform sections only."""
from pathlib import Path
import json
from cross_section import solve
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'designs/eye-camera-ov9281/electronics/r11/impedance-validation.json'
def main():
    cases={'CSI_flex':dict(width=.075,gap=.25,height=.05,copper=.018,er=3.4,coat=.04,coat_er=3.4),
           'CSI_component':dict(width=.075,gap=.25,height=.05,copper=.018,er=3.4,coat=.078,coat_er=3.8),
           'USB_main':dict(width=.15,gap=.1,height=.126,copper=.025,er=3.8,coat=.02,coat_er=3.8,conformal=True)}
    results={}
    for name,kwargs in cases.items():
        target=90 if name.startswith('USB') else 100
        mesh=[solve(**kwargs,step=step,domain=.75) for step in [.005,.0025,.00125]]
        domain=solve(**kwargs,step=.0025,domain=1.)
        sensitivity=[]
        for label,change in [('er_low',{'er':kwargs['er']-.3,'coat_er':kwargs['coat_er']-.3}),('er_high',{'er':kwargs['er']+.3,'coat_er':kwargs['coat_er']+.3}),('width_low',{'width':kwargs['width']-.005}),('width_high',{'width':kwargs['width']+.005}),('height_low',{'height':kwargs['height']*.9}),('height_high',{'height':kwargs['height']*1.1})]:
            sensitivity.append({'case':label,**solve(**{**kwargs,**change},step=.0025,domain=.75)})
        results[name]={'target_ohm':target,'target_percent':10,'mesh':mesh,'domain_check':domain,'mesh_last_delta_percent':100*abs(mesh[-1]['zdiff_ohm']/mesh[-2]['zdiff_ohm']-1),'domain_delta_percent':100*abs(domain['zdiff_ohm']/mesh[1]['zdiff_ohm']-1),'parameter_sensitivity':sensitivity,'nominal_within_target':abs(mesh[-1]['zdiff_ohm']/target-1)<=.1}
        OUT.write_text(json.dumps({'results':results,'scope':'2D quasi-static uniform cross-sections; engineering permittivity and tolerance assumptions. Excludes pad launches, ESD/input fanout, meander discontinuities, losses, fabrication compensation, package parasitics and eye-diagram compliance.'},indent=2)+'\n')
        print(name,round(mesh[-1]['zdiff_ohm'],3),'ohm; mesh delta',results[name]['mesh_last_delta_percent'],flush=True)
    assert all(r['nominal_within_target'] for r in results.values())
    assert all(r['mesh_last_delta_percent']<4 and r['domain_delta_percent']<3 for r in results.values())
if __name__=='__main__':main()
