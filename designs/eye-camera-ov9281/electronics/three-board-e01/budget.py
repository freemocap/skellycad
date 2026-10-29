"""Part-by-part mass scenarios; all figures are estimates, not measurements.
[@cdaCopperDensity2026; @ti953A01]
"""
from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parent
D=json.loads((HERE/'placement.json').read_text());boards=D['boards'];cases={}
for i,(name,cov,optics,finish) in enumerate([('low',.4,.08,.035),('nominal',.6,.15,.065),('high',.8,.28,.10)]):
    head={};base={}
    for region in ['head','interface']:
        area=math.prod(boards[region]['size']);cu=.122*cov
        head[region+'_copper']=area*cu*.00891
        head[region+'_dielectric_coverlay']=area*(.303-cu)*.00142
        head[region+'_FR4_stiffener']=area*.1*.00185
        head[region+'_adhesive']=area*.05*.0012
    area=25*5.5;cu=.036*cov
    head['free_flex']=area*(cu*.00891+(.166-cu)*.00142)
    head['populated_packages']=sum(x['mass_g'][i] for x in D['parts'] if x['board']!='base' and x['populated'])
    head['optics_holder_filter_retention']=optics;head['solder_finish_mount_strain_relief']=finish
    w,h=boards['base']['size'];cu=.106*cov
    base['PCB_copper']=w*h*cu*.00891;base['PCB_dielectric']=w*h*(.4-cu)*.00185
    base['populated_packages']=sum(x['mass_g'][i] for x in D['parts'] if x['board']=='base' and x['populated'])
    base['solder_finish']= [.025,.045,.08][i]
    electronics=sum(base.values())
    # Hollow thin-wall housing: 0.5 mm walls / lids, 6 mm outside height.
    shell=((w+1.2)*(h+1.2)*6-(w+.2)*(h+.2)*5)*.0012
    base['enclosure_reservation']=shell*[.8,1,1.3][i];base['mount_and_local_strain_relief']=[.15,.3,.6][i]
    cases[name]={'head_parts_g':head,'head_complete_g':sum(head.values()),'head_below_1g':sum(head.values())<1,'base_parts_g':base,'base_electronics_g':electronics,'base_complete_backpack_g':sum(base.values())}
tethers=[]
for length in [.3,.6]:tethers.append({'length_m':length,'bare_4x36AWG_copper_g':4*length*1000*math.pi*.127**2/4*.00891,'complete_cable_scenario_g':[length*.6,length*1.5],'excluded_from_head_target':True})
result={'status':'Engineering scenarios; no measured mass or fabricated board','cases':cases,'tether':tethers,'stack_basis':{'component_regions_mm':.303,'four_layer_copper_total_mm':.122,'free_flex_mm':.166,'free_flex_copper_total_mm':.036,'FR4_stiffener_mm':.1,'adhesive_mm':.05,'base_four_layer_mm':.4,'base_copper_total_mm':.106},
 'assumptions':['Retain conservative A01/C head stack and full-area backing. TI953 recommends at least four layers and dedicated ground.','Copper fill 40/60/80 percent; intervals are scenarios, not confidence bounds.','Package intervals inherited from R11 or explicitly estimated for new devices.','Optics, adhesive, enclosure and mounts are unqualified allocations.','Base complete mass includes housing and mounting allowance; external tether and bench power source excluded.','Backpack battery is not designed or included; intended input remains externally supplied regulated 5 V.'],
 'target_status':'Under-one-gram target is not met by the nominal conservative construction; reduce mass before design freeze.'}
(HERE/'mass-budget.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{x:y for x,y in v.items() if x.endswith('_g') and not isinstance(y,dict)} for k,v in cases.items()},indent=2))
