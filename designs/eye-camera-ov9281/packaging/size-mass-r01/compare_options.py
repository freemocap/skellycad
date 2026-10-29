"""Compare candidate construction assumptions without changing the circuit."""
from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parent
# Conditional package replacements: courtyard W/H, reserved height and mass.
# No order codes, equivalent electrical behavior or availability are asserted.
REPLACEMENTS={
'R_0402_1005Metric':([1.1,.8],.4,[.00008,.00015,.0003],'0201-class resistor'),
'C_0603_1608Metric':([1.9,1.0],.6,[.0007,.0015,.003],'0402-class capacitor, effective capacitance must be checked'),
'C_0805_2012Metric':([2.4,1.4],1.0,[.002,.0045,.008],'0603-class capacitor, rating and DC bias must be checked'),
'SOT-23-5':([2.5,2.5],.8,[.002,.004,.008],'Small DFN/WCSP regulator equivalent, not selected'),
'SOT-23':([2.1,1.8],.8,[.001,.0025,.005],'Small DFN transistor/diode equivalent, not selected'),
'SOIC-8_5.3x5.3mm_P1.27mm':([4.0,3.0],.8,[.006,.012,.025],'Small flash package equivalent, not selected')}
def main():
    rows=json.loads((HERE/'component-budget.json').read_text(encoding="utf-8"));base=json.loads((HERE/'mass-budget.json').read_text(encoding="utf-8"))
    variants=[{'id':'A','name':'Thin modular boards','controller_mm':[32,16],'head_mm':[14,14],'free_flex_mm':[30.3,12.5],'rigid_thickness_mm':.40,'flex_thickness_mm':.168,'construction':'Six rigid copper layers at 18um, separate two-layer 24um flex; retained connectors and packages. Custom stackup requires approval.','relative_cost':'Lowest candidate complexity; still custom thin six-layer assembly.'},
    {'id':'B','name':'Custom ultrathin rigid-flex','controller_mm':[24,12],'head_mm':[12,12],'free_flex_mm':[32.85,8],'rigid_thickness_mm':.25,'flex_thickness_mm':.12,'construction':'Six 12um rigid copper layers, integrated two-layer 12um flex. Aspirational stackup, no matching manufacturer construction verified.','relative_cost':'Premium custom construction, dense assembly and microvia development.'},
    {'id':'C','name':'Published SLIM.flex construction','controller_mm':[26,12.5],'head_mm':[12.5,12.5],'free_flex_mm':[32.85,8],'rigid_thickness_mm':.303,'flex_thickness_mm':.166,'construction':'Wuerth FLEX6_6F_030_12_2V13: 25um outer/18um inner copper; two-layer flex region. Microvias only in standard construction. Extra local support remains a study assumption.','relative_cost':'Premium HDI flex assembly; published construction basis, no project quote.'}]
    for v in variants:
        compact=v['id']!='A';parts=[]
        for r in rows:
            if r['board']=='flex-study' or r['high_g']==0:continue
            if compact and r['reference']=='J102' and r['board']=='controller':continue
            old=r['courtyard'];x0,y0,x1,y1=old['bounds_xy_mm'];dims=[x1-x0,y1-y0];mass=[r[k] for k in ['low_g','nominal_g','high_g']];h=r['height_reservation_mm'];change='Retained package'
            if compact and r['footprint'] in REPLACEMENTS:dims,h,mass,change=REPLACEMENTS[r['footprint']]
            parts.append({'board':r['board'],'reference':r['reference'],'value':r['value'],'source_footprint':r['footprint'],'source_side':old['side'],'courtyard_mm':dims,'height_mm':h,'mass_g':mass,'assumption':change})
        v['parts']=parts;components=[sum(p['mass_g'][i] for p in parts) for i in range(3)];area=math.prod(v['controller_mm'])+math.prod(v['head_mm']);flex=math.prod(v['free_flex_mm']);substrate=[]
        for i,(coverage,poly,adh,margin) in enumerate(zip([.50,.65,.80],[.00138,.00142,.0015],[.001,.0012,.0015],[.85,1,1.15])):
            if v['id']=='A':
                # Rescale observed copper coverage and core density to candidate.
                cu=sum(p['nominal_g'] for p in base['parts'] if p['name'] in ['controller copper sheets','head copper sheets'])*(area/836)*(.018/.035)
                rigid=cu*margin+area*(.4-.108)*[.0017,.0018,.0019][i]+area*.025*adh
                flexible=sum(p[['low_g','nominal_g','high_g'][i]] for p in base['parts'] if p['name'].startswith('flex'))
            elif v['id']=='B':
                rigid=area*(.072*coverage*.00891+(.25-.072)*[.0017,.0018,.0019][i]+.02*adh)*margin
                flexible=flex*(.024*.65*.00891+.096*poly)*margin+[.005,.012,.025][i]
            else:
                rigid=area*(.122*coverage*.00891+.07*poly+.06*adh+.04*.0012+.02*adh)*margin
                flexible=flex*(.036*.65*.00891+.07*poly+.06*adh)*margin
                # Local support under sensor/lens and P4; qualified stiffness unknown.
                flexible+=(100+64-6.5**2)*.15*[.0012,.0015,.0019][i]
            substrate.append(rigid+flexible+[.004,.008,.016][i])
        holder_volume=48.241337905872506 # Native support solid, geometry-validation.json
        optics=[.040+holder_volume*.00105+.009,.085+holder_volume*.0012+.011,.150+holder_volume*.0015+.014] if compact else [sum(p[k] for p in base['parts'] if p['name'] in ['lens assembly','holder','filter']) for k in ['low_g','nominal_g','high_g']]
        assembly=[.02,.04,.08] if compact else [.022,.05,.11]
        v['mass_g']={'boards':substrate,'components':components,'optics':optics,'solder_adhesive_retention':assembly,'total':[sum(x[i] for x in [substrate,components,optics,assembly]) for i in range(3)]}
        v['no_tether_in_total']=True;v['electrically_validated']=False;v['manufacturing_approved']=False
    (HERE/'options.json').write_text(json.dumps({'variants':variants,'conditional_package_replacements':REPLACEMENTS,'limits':['Intervals are screening scenarios, not certified bounds.','B/C depend on unselected electrically equivalent smaller parts and a lighter holder.','A preserves current package inventory; all variants require new routing and impedance work.','C is based on a published construction, not an approved project stackup or quote.','B is an unverified custom process target.']},indent=2)+'\n')
    print(json.dumps([{k:v[k] for k in ['id','name','mass_g']} for v in variants],indent=2))
if __name__=='__main__':main()
