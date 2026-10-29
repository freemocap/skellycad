"""Transparent screening estimates, not measured component weights."""
from pathlib import Path
import csv,json,math
HERE=Path(__file__).resolve().parent
# Grams per populated package: explicit engineering intervals, not vendor data.
# Height is a packing reservation, not a verified component height.
PACKAGES={
'R_0402_1005Metric':(.0002,.00035,.0006,.5),
'C_0402_1005Metric':(.0007,.0012,.0018,.55),
'C_0603_1608Metric':(.002,.0035,.006,.9),
'C_0805_2012Metric':(.004,.009,.016,1.3),
'L_0805_2012Metric':(.006,.011,.018,1.3),
'SOT-666':(.001,.002,.003,.7),
'SOT-23':(.006,.009,.014,1.2),
'SOT-23-5':(.009,.012,.018,1.2),
'SOIC-8_5.3x5.3mm_P1.27mm':(.07,.11,.15,2.0),
'ESP32-P4':(.135,.18,.23,1.0),
'OV9281':(.02,.035,.055,1.0),
'Crystal_SMD_2016-4Pin_2.0x1.6mm':(.004,.008,.012,.9),
'Epson_SG210STF_2.5x2.0mm_R09':(.006,.01,.015,1.0),
'Kingbright_AP1608F3C_R09':(.0015,.0025,.004,1.0),
'JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal':(.025,.045,.075,3.0),
'Hirose_FH34SRJ_24S_0.5SH_R05':(.04,.075,.12,1.0),
'ProgrammingPads_5x1mm_P1.5mm':(0,0,0,0),
'Flex_Solder_24_P0.5_R05':(0,0,0,0),'Flex_Contacts_R05':(0,0,0,0)}
def main():
    g=json.loads((HERE/'native-geometry.json').read_text(encoding="utf-8"));opt=json.loads((HERE/'optical-volumes.json').read_text(encoding="utf-8"));parts=[];rows=[]
    def add(label,lo,mid,hi,basis):parts.append({'name':label,'low_g':lo,'nominal_g':mid,'high_g':hi,'basis':basis})
    for name,b in g['boards'].items():
        flex=name=='flex-study';area=b['area_mm2'];t=.024 if flex else .035
        cu=sum(q['copper_union_area_mm2'] for q in b['layers'])*t*.00891
        add(name+' copper sheets',cu*.8,cu,cu*1.2,'Native layer polygon union; nominal copper density 8.91 g/cm3; +/-20% screening allowance for thickness and geometry, not a supplier tolerance.')
        if not flex:
            # Etched-away copper is resin-filled on four inner layers. Account
            # for that material rather than treating all vacant foil as air.
            resin=sum(area-q['copper_union_area_mm2'] for q in b['layers'][1:-1])*.035
            core=area*.331
            drill=sum(math.pi*(v['drill_mm']/2)**2*.471 for v in b['vias'])
            add(name+' laminate and resin fill',max(0,core*.85-drill)*.0017+resin*.0011, max(0,core-drill)*.0018+resin*.0013,(core*1.15)*.0019+resin*.0015,'0.331 mm nominal dielectric; 1.7-1.9 g/cm3 laminate; +/-15% thickness scenario. Inner etched regions add resin. Drill subtraction is an approximation.')
            barrel=sum(math.pi*((v['drill_mm']/2+.025)**2-(v['drill_mm']/2)**2)*.471 for v in b['vias'])*.00891
            add(name+' barrels and surface finish',barrel*.7,barrel+.003,barrel*1.4+.008,'25um nominal via plating assumption; small finish allowance; annular lands already counted in copper sheets.')
            add(name+' mask and markings',area*.008*.0011,area*.015*.0012,area*.025*.0015,'Total equivalent coating thickness 8-25um, density 1.1-1.5 g/cm3: engineering allowance.')
        else:
            # PI 25um core + 2x12.5um coverlay; adhesive 2x20 + 2x15um.
            pi=area*.05;adh=area*.07-2*2.5*12.5*.0275
            add('flex polymer and adhesive',pi*.00138+adh*.0010,pi*.00142+adh*.0012,pi*.0015+adh*.0015,'Generic PI density anchored to Kapton HN; adhesive interval assumed. Subtract contact-side tip coverlay volume as an adhesive-equivalent approximation.')
            stiff=2*2.5*12.5*.1595
            add('flex tip stiffeners',stiff*.0012,stiff*.0015,stiff*.0019,'Existing 0.1595 mm stiffener/adhesive allocation; material unselected.')
    for c in g['components']:
        lo,mid,hi,h=PACKAGES[c['footprint']];r={**c,'low_g':lo,'nominal_g':mid,'high_g':hi,'height_reservation_mm':h,'mass_evidence':'Engineering package-class interval; supplier weight unverified'};rows.append(r)
        if hi:add(c['board']+'/'+c['reference']+' '+c['value'],lo,mid,hi,'Package-class estimate; see component-budget.csv.')
    add('lens assembly',.040,.085,.150,'CH2021A 4P lens, 6x2.65mm envelope; supplier weight field is blank. Chosen broad estimate, not density times a solid lens cylinder.')
    v=opt['HolderStudy']['volume_mm3'];add('holder',v*.00105,v*.0012,v*.0015,'Actual current CAD volume; assumed lightweight polymer 1.05-1.50 g/cm3; thread and attachment unresolved.')
    v=opt['FilterReservation']['volume_mm3'];add('filter',v*.0022,v*.0025,v*.0030,'Current 5.2x0.2mm reserved disk; assumed glass density, part unselected.')
    add('solder',.012,.025,.050,'Assembly-wide allowance; not CAD solder volume.')
    add('adhesive and module-side retention',.010,.025,.060,'Allowance; no external tether, cable-side plug or external mount included.')
    totals={k:sum(p[k] for p in parts) for k in ['low_g','nominal_g','high_g']}
    result={'module_mass_excludes_tether':True,'estimates_are_not_statistical_confidence_bounds':True,'totals':totals,'parts':parts,'package_mass_evidence':'All component intervals are engineering screening assumptions; exact part weights remain unresolved. Installed footprint count is retained; no circuit simplification assumed.','source_geometry':'native-geometry.json','copper_nominal_g':sum(p['nominal_g'] for p in parts if p['name'].endswith('copper sheets'))}
    (HERE/'mass-budget.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'component-budget.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (HERE/'component-budget.csv').open('w',newline='',encoding='utf-8') as f:
        keys=['board','reference','value','footprint','low_g','nominal_g','high_g','height_reservation_mm','mass_evidence'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
    cable=[]
    for awg,od in [(28,.5),(32,.38),(36,.28)]:
        diameter=.127*92**((36-awg)/39);a=math.pi*diameter**2/4;cu=4*a*10*.00891;ins=4*(math.pi*od**2/4-a)*10
        low=cu+ins*.0010;mid=cu*1.2+ins*.0014+.003;high=cu*1.5+ins*.0022+.008
        cable.append({'awg':awg,'assumed_insulated_wire_od_mm':od,'four_conductor_copper_g_per_cm':cu,'complete_cable_g_per_cm':[low,mid,high],'mass_5_10_20_cm_nominal_g':[mid*n for n in [5,10,20]],'power_loop_ohm_at_20cm':2*1.72e-8*.2/(a*1e-6),'voltage_drop_at_0_5A_20cm_V':.5*2*1.72e-8*.2/(a*1e-6),'termination_limit':'AWG36 is outside the reviewed SH contact wire range; would need a different termination.' if awg==36 else 'Within reviewed SH AWG range; exact crimp and insulation compatibility unqualified.'})
    (HERE/'tether-budget.json').write_text(json.dumps({'excluded_from_module_target':True,'cable_side_plug_extra_g':[.02,.10],'rows':cable,'limits':['Wire diameters use the AWG geometric definition; insulation OD, braid and jacket mass are assumptions.','No impedance, ampacity, USB compliance, bend radius or cable stiffness qualification.','The 0.5 A load is a comparison scenario, not a measured camera current.','Bare conductor mass is not complete cable mass; strand construction and strain relief determine mechanical loading.']},indent=2)+'\n')
    print(json.dumps({'module':totals,'copper_nominal_g':result['copper_nominal_g'],'physical_component_count':sum(r['high_g']>0 for r in rows)},indent=2))
if __name__=='__main__':main()
