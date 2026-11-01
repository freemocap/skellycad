"""Reproducible architecture screening, not hardware qualification.

Sources: [@ti953A01; @ti954A01; @omnivisionOv9281Brief;
@leopardOv9281Electrical2026; @tiTlv733R11; @cdaCopperDensity2026].
Uncited numeric inputs below are explicitly chosen engineering scenarios.
"""
from pathlib import Path
import json, math

HERE = Path(__file__).resolve().parent

def calculate():
    modes = []
    for w,h,f in [(640,400,100),(640,400,120),(1280,800,120)]:
        size=w*h; payload=size*f
        modes.append(dict(width=w,height=h,fps=f,frame_bytes=size,
            payload_MB_s=payload/1e6, payload_Mbps=payload*8/1e6,
            csi_packet_Mbps=(size+14*h+8)*f*8/1e6,
            planning_Mbps=payload*8*1.2/1e6,
            fits_2x800_Mbps_payload_screen=payload*8*1.2<1.6e9,
            fits_USB480_absolute_ceiling=payload*8<480e6,
            usb_qualification_MB_s=35 if f==100 else (40 if w==640 else None),
            four_capture_buffers_bytes=size*4, usb_stage_bytes=size,
            two_spare_buffers_stall_ms=2000/f, frame_interval_ms=1000/f,
            memory_traffic_4x_MB_s=payload*4/1e6))
    # Nominal sensor rail currents are reference operating conditions, not maxima.
    p18=.28+.0025*1.8+.052*1.8+.015+.008+.010+.022
    nominal_load_W=p18/.85+5*.024
    cables=[]
    for length in [.3,.6]:
        for case,vs,power,temp in [('nominal',5,nominal_load_W,20),('higher_load_screen',4.75,.9,40)]:
            resistance=2*length*1.5*(1+.00393*(temp-20))+.2
            discriminant=vs*vs-4*resistance*power
            assert discriminant>0
            vin=(vs+math.sqrt(discriminant))/2;current=power/vin
            cables.append(dict(length_m=length,case=case,supply_V=vs,load_W=power,
                conductor_temperature_C=temp,loop_ohm=resistance,received_V=vin,
                current_A=current,drop_V=vs-vin,cable_contact_loss_W=current**2*resistance,
                clears_3V3_input_screen=vin>=3.3))
    # Envelope minus effective copper volume = dielectric/coating volume.
    # This avoids counting solid board material and copper twice.
    regions={'head':(14*10,.303,.122),'interface':(18*10,.303,.122),'flex':(25*5.5,.166,.036)}
    masses={}
    for support in ['FR4_100um','steel_50um']:
        cases={}
        for scenario,cov,optics,pkgs,extra in [('low',.4,.08,.15,.035),('nominal',.6,.15,.21,.065),('high',.8,.28,.30,.10)]:
            parts={}
            for region,(area,t,cu) in regions.items():
                parts[region+'_copper']=area*cu*cov*.00891
                parts[region+'_dielectric_and_mask']=area*(t-cu*cov)*.00142
            # Full undersides are reserved; no unproven lightening cuts.
            parts['backing']=(320*.1*.00185 if support=='FR4_100um' else 320*.05*.0079)
            parts['backing_adhesive']=320*(.05 if support=='FR4_100um' else .025)*.0012
            parts['populated_packages']=pkgs
            parts['optics_holder_filter_retention']=optics
            parts['solder_finish_mount_strain_relief']=extra
            cases[scenario]={'parts_g':parts,'total_g':sum(parts.values())}
        masses[support]=cases
    # Package allowance includes serializer, sensor, all passives, regulators,
    # oscillator, LEDs and camera-side tether connector. It is not weighed.
    package_nominal={'sensor':.035,'serializer':.050,'connector':.045,
        'buck_inductor':.0331,'regulators':.0045,'oscillator':.008,
        'two_LEDs':.005,'remaining_passives_protection_filters':.0294}
    assert abs(sum(package_nominal.values())-.21)<1e-9
    rtrace=1.724e-8*.025/(.3e-3*18e-6)
    core_R=rtrace+.247+.05
    dvdd={'LDO_low_V':1.2*(1-.014),'sensor_min_V':1.14,
        'one_way_supply_trace_mm':25,'trace_width_mm':.3,'copper_um':18,
        'trace_ohm':rtrace,'filter_max_DCR_ohm':.247,'assumed_return_ohm':.05,
        'total_ohm':core_R,'at_52mA_V':1.2*(1-.014)-.052*core_R,
        'current_at_minimum_A':(1.2*(1-.014)-1.14)/core_R,
        'scope':'Simplified pre-route DC screen; actual load maximum, return, hot copper, transients and sequencing unresolved'}
    # Copper only: lower bound. Insulation, shield, connectors and strain relief add mass.
    area36=math.pi*.127**2/4
    tether_mass=[dict(length_m=l,bare_four_copper_conductors_g=4*l*1000*area36*.00891,
        assembly_mass_scenario_g=[l*.6,l*1.5],note='0.6-1.5 g/m is an assumption, not a cable specification') for l in [.3,.6]]
    result=dict(status='Analytical scenarios only; no measured performance',modes=modes,
        assumptions={'CSI_20percent':'Planning envelope, not a standards requirement or proof of sensor blanking',
        'wire_ohm_per_m':1.5,'wire_note':'Chosen conservative copper-class 36 AWG scenario; actual stranded cable unselected',
        'contact_loop_ohm':.2,'buck_efficiency':.85,'higher_load_W':.9,
        'thermal':'No junction-to-ambient value predicts animal-contact surface temperature'},
        local_power={'nominal_1V8_load_W':p18,'nominal_tether_delivered_W':nominal_load_W,
        'serializer_typical_W':.28,'sensor_reported_active_W':.156,
        'sensor_rail_typical_sum_W':.052*1.2+.024*2.8+.0025*1.8,
        'unallocated_sensor_power_allowance_W':.022,
        'rail_note':'1.8 V buck also supplies 1.2 V LDO input; 2.8 V analog LDO supplied from 5 V. Avoid 5-to-1.8 V linear conversion.',
        'base_station_power_allocation_W':[1.5,3.0],
        'system_source_allocation':'Separate regulated 5 V / 1 A bench supply candidate; product USB power contract and backfeed isolation unresolved'},
        cable_cases=cables,tether_mass=tether_mass,dvdd=dvdd,mass=masses,
        package_nominal_allowance_g=package_nominal,
        base_station_mass_scenario_g=[3,7],
        limitations=['Mass intervals are independent scenarios, not confidence bounds.',
        'Board stack retained from R11 for conservative comparison; new outline still needs fabricator review.',
        'No cable insertion-loss or S-parameter model: DC passing is not a high-speed channel pass.',
        'No thermal surface-temperature prediction; serializer is a substantial local heat source.',
        'Base station mass includes PCB/packages/connectors only; backpack enclosure and mounts excluded.',
        'No demonstrated frame rate, latency, focus, physical fit or eye-use qualification.'])
    assert all(c['clears_3V3_input_screen'] for c in cables)
    assert modes[0]['payload_MB_s']==25.6 and modes[-1]['fits_USB480_absolute_ceiling'] is False
    assert dvdd['at_52mA_V']>1.14
    (HERE/'budgets.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'nominal_head_g':{k:v['nominal']['total_g'] for k,v in masses.items()},'head_power_W':nominal_load_W,'cable_cases':cables},indent=2))
    return result

if __name__=='__main__':calculate()
