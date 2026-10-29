"""Select R11 orderable parts and preserve the R10 electrical contract.

Sources and review boundaries are recorded in electronics/r11/COMPONENTS.md.
This script creates design inputs, not a purchasing or fabrication release.
"""
from pathlib import Path
import csv
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT / 'electronics/r11'
BASE = REPO / 'generated/ov9281-r10-review-02'


def main():
    tree = ET.parse(BASE / 'source-netlist.xml').getroot()
    nets = {}
    for net in tree.find('nets'):
        for node in net.findall('node'):
            nets.setdefault(node.get('ref'), {})[node.get('pin')] = (
                None if net.get('name').startswith('unconnected-') else net.get('name'))
    inventory = list(csv.DictReader((ROOT / 'packaging/size-mass-r01/component-budget.csv').open(encoding='utf-8')))
    selected = {}
    caps = {
        '100n': ('GRM155R71C104KA88D', '0402', 16, 'X7R', .55),
        '10n': ('GRM155R71C103KA01D', '0402', 16, 'X7R', .55),
        '1u': ('GRM188R71C105KA12D', '0603', 16, 'X7R', .9),
        '4.7u': ('GRM188R61A475KE15D', '0603', 10, 'X5R', .9),
        '10u': ('GRM21BR61A106KE19L', '0805', 10, 'X5R', 1.35),
        '22u': ('GRM21BR61A226ME44L', '0805', 10, 'X5R', 1.45),
        '16p': ('GRM1555C1H160JA01D', '0402', 50, 'C0G', .55),
        '22p': ('GRM1555C1H220JA01D', '0402', 50, 'C0G', .55),
    }
    metric = {'0402': '1005', '0603': '1608', '0805': '2012'}
    for row in inventory:
        ref = row['reference']
        if ref in {'J102', 'J201', 'J301', 'J302'}:
            continue
        part = dict(reference=ref, region=row['board'], value=row['value'],
                    footprint='Camera:' + row['footprint'], manufacturer='', mpn='',
                    pin_nets=nets.get(ref, {}), populated=ref != 'R7',
                    height_max_mm=float(row['height_reservation_mm']),
                    mass_g=[float(row[k]) for k in ('low_g', 'nominal_g', 'high_g')],
                    mass_evidence='Engineering interval; component not weighed', sources=[])
        if ref.startswith('C'):
            if ref in ('C101', 'C102'):
                val = '16p'
            elif ref in ('C123', 'C124'):
                val = '22u'
            else:
                val = re.search(r'(100n|10n|22p|22u|10u|4u7|4\.7u|1u)', row['value'])[1].replace('4u7', '4.7u')
            mpn, size, volts, dielectric, height = caps[val]
            part.update(mpn=mpn, manufacturer='Murata', value=val,
                        footprint=f'Capacitor_SMD:C_{size}_{metric[size]}Metric',
                        rated_voltage_V=volts, dielectric=dielectric, height_max_mm=height,
                        sources=['murataMlccList2025', 'murata22u10v2025'])
            if size == '0603':
                part['mass_g'] = [.002, .0035, .006]
            if ref in ('C123', 'C124'):
                part['change'] = '10 uF to 22 uF; retain 0805 for effective capacitance margin'
        elif ref.startswith('R'):
            val = re.search(r'(4\.02k|4\.7k|2\.2k|499k|453k|100k|10k|1k|0)', row['value'])[1]
            code = {'4.02k': '4K02', '4.7k': '4K7', '2.2k': '2K2', '0': '0R'}.get(val, val.upper())
            part.update(manufacturer='Yageo', value=val,
                        mpn='RC0402' + ('JR' if val == '0' else 'FR') + '-07' + code + 'L',
                        rated_power_W=.063, height_max_mm=.4, sources=['yageoRc0402R11'])
        elif ref in ('L1', 'L2', 'L3'):
            part.update(mpn='MLP2012S3R3MT0S1', manufacturer='TDK', value='3.3u',
                        rated_current_A=.9, dcr_max_ohm=.247, height_max_mm=1,
                        sources=['tdkMlp2012R11'])
        selected[ref] = part

    def update(ref, **kwargs):
        selected[ref].update(kwargs)

    update('U101', mpn='ESP32-P4NRW16X', manufacturer='Espressif', value='ESP32-P4NRW16X / v3.x',
           sources=['esp32P4Datasheet', 'esp32P4HardwareGuide', 'espressifKicadLibrary'])
    update('U1', mpn='OV09281-H64A', manufacturer='OMNIVISION', value='OV9281',
           sources=['omnivisionOv9281Brief', 'antmicroOv9281Board'])
    update('U102', mpn='W25Q32JVUUIQ TR', manufacturer='Winbond', value='W25Q32JVUUIQ / 4 MB',
           footprint='Package_SON:Winbond_USON-8-2EP_3x4mm_P0.8mm_EP0.2x0.8mm',
           height_max_mm=.6, mass_g=[.010, .017, .026], sources=['winbondW25Q32JvK2026'])
    selected['U102']['pin_nets']['9'] = 'GND'
    for ref in ('U103', 'U104'):
        old = selected[ref]['pin_nets']
        update(ref, mpn='TLV62569DRLR', manufacturer='Texas Instruments', value='TLV62569DRLR',
               footprint='Camera:TI_DRL0006A_R11', height_max_mm=.6,
               mass_g=[.0015, .0025, .004], sources=['tiTlv62569'],
               pin_nets={new: old[prior] for prior, new in {'1':'5','2':'2','3':'4','4':'3','5':'1'}.items()})
        selected[ref]['pin_nets']['6'] = None
    for ref, voltage in [('U5', '18'), ('U6', '12'), ('U7', '28')]:
        old = selected[ref]['pin_nets']
        update(ref, mpn=f'TLV733{voltage}PDQNR', manufacturer='Texas Instruments', value=f'TLV733{voltage}PDQNR',
               footprint='Package_SON:Texas_X2SON-4_1x1mm_P0.65mm', height_max_mm=.4,
               mass_g=[.0005, .001, .0016], sources=['tiTlv733R11'],
               pin_nets={'1':old['5'], '2':old['2'], '3':old['3'], '4':old['1'], '5':'GND'})
    for ref in ('Q101', 'Q102', 'Q103', 'Q201'):
        update(ref, mpn='PMZB200UNEYL', manufacturer='Nexperia', value='PMZB200UNE',
               footprint='Package_TO_SOT_SMD:SOT-883', height_max_mm=.4,
               mass_g=[.0003, .0005, .0009], sources=['nexperiaPmzb200R11'])
    for ref in ('L101', 'L102'):
        update(ref, mpn='DFE252012F-2R2M=P2', manufacturer='Murata', value='2.2u / 3.3 A Isat',
               footprint='Camera:Murata_DFE252012F_R11', height_max_mm=1.2,
               mass_g=[.030, .0331, .037], mass_evidence='Manufacturer typical 0.0331 g; bounds are engineering allowances',
               inductance_H=2.2e-6, rated_current_A=2.3, saturation_current_A=3.3,
               dcr_max_ohm=.082, sources=['murataDfe252012R11', 'murataDfeMass2025'])
    update('Y101', mpn='ECS-400-10-37B2-CKM-TR', manufacturer='ECS', value='40 MHz / CL 10pF',
           footprint='Camera:ECS_ECX1637B2_R11', height_max_mm=.50,
           sources=['ecs1637b2R11', 'ecs400R11'], load_capacitance_pF=10, esr_max_ohm=40)
    update('Y1', mpn='X1G004171003100', manufacturer='Epson', value='SG-210STF 24.0000ML',
           height_max_mm=.8, sources=['epsonSG210STF'])
    update('U105', mpn='USBLC6-2P6', manufacturer='STMicroelectronics', sources=['stUsblc6'])
    update('J101', mpn='SM04B-SRSS-TB(LF)(SN)', manufacturer='JST', value='USB / JST SH / 1VBUS 2DM 3DP 4GND',
           sources=['jstShCatalog'])
    update('J103', mpn='PCB programming lands', manufacturer='PCB fabrication', sources=[],
           mass_g=[0,0,0], mass_evidence='Copper included in board mass')
    for ref in ('D201', 'D202'):
        update(ref, mpn='AP1608F3C', manufacturer='Kingbright', height_max_mm=1.1, sources=['kingbrightAP1608F3C'])
    for part in selected.values():
        part['pin_nets']={pin:('/IR_GATE' if net=='/IR_BASE' else net) for pin,net in part['pin_nets'].items()}
    for ref, part in selected.items():
        assert part['mpn'] and part['manufacturer'], ref
        assert part['pin_nets'], ref
        assert not any(x in part['value'] for x in ('TBD', 'candidate')), ref
    report = {'revision':'OV9281-P4-R11', 'baseline':str(BASE.relative_to(REPO)).replace('\\','/'),
              'status':'Selected for offline engineering; hardware and supply-chain qualification remain',
              'removed_interfaces':['J102','J201','J301','J302'],
              'schematic_only_interface_removed':'J104: obsolete external IR port, replaced by on-board R09 LED circuit',
              'component_count':len(selected), 'populated_count':sum(p['populated'] for p in selected.values()),
              'parts':dict(sorted(selected.items(), key=lambda x:(x[0].rstrip('0123456789'),int(re.search(r'\d+',x[0])[0]))))}
    (OUT/'components.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # Analytical selection screen. Detailed PCB-dependent analysis belongs to item 5.
    calculations = {
        'system_buck_nominal_V':.6*(1+453/100),
        'system_buck_tolerance_V':[.588*(1+453*.99/(100*1.01)), .612*(1+453*1.01/(100*.99))],
        'core_buck_startup_V':1.2,
        'core_buck_tolerance_before_P4_control_V':[.588*(1+.99/1.01), .612*(1+1.01/.99)],
        'buck_inductor_ripple_A_at_1MHz_Lminus20pct':{
            'system':3.318*(1-3.318/5.25)/(2.2e-6*.8*1e6),
            'core':1.3*(1-1.3/3.45)/(2.2e-6*.8*1e6)},
        'maximum_design_continuous_buck_load_A':1.0,
        'sensor_LDO_current_rating_A':.3,
        'sensor_power_envelope_W':.2,
        'sensor_LDO_individual_current_bounds_A':{v:.2/float(v) for v in ('1.2','1.8','2.8')},
        'sensor_LDO_individual_dissipation_bounds_W':{v:(3.45-float(v))*.2/float(v) for v in ('1.2','1.8','2.8')},
        'sensor_envelope_note':'0.2 W is a screening assumption above the published 0.156 W active figure, not a vendor maximum; individual bounds cannot occur simultaneously.',
        'crystal_load_pF':16/2+2,
        'crystal_stray_assumption_pF':2,
        'crystal_sensitivity_load_pF':[16*.95/2+1.5,16*1.05/2+2.5],
        'IR_nominal_current_per_LED_A':(3.318-1.3)/(1000+2*.49),
        'IR_electrical_upper_bound_per_LED_A':3.45/990,
        'IR_default':'GPIO5 low and 100 kohm gate pulldown; not an eye-safety qualification',
        'IR_gate_on_V':3.3*100/(100+2.2),
        'IR_gate_RC_typ_s':2200*89e-12,
        'flash_voltage_V':3.3,
        'flash_read_mode':'DIO, 40 MHz, 4 MB; do not program the 1.8 V flash eFuse',
        'SCCB_clock_Hz':100000,
        'SCCB_pullup_ohm':4700,
        'SCCB_low_current_A':(3.45+1.83)/(4700*.99),
        'SCCB_FET_drop_V_at_1p5V_gate':(.49*(3.45+1.83)/(4700*.99)),
        'SCCB_rise_time_s_for_200pF':.8473*4700*1.01*200e-12,
        'qualification_required':['Capacitance under DC bias and temperature, buck load-step stability',
            'USB startup/enumeration/suspend current and inrush', 'Sensor rail sequencing, rail noise and reset timing',
            'Actual SLIM.flex thermal resistance and skin-facing temperature',
            'Crystal startup, frequency and drive level', 'MIPI eye diagram and USB signal integrity',
            'Close-focus IR optics and illuminator exposure']}
    assert calculations['system_buck_tolerance_V'][0] > 3
    assert calculations['system_buck_tolerance_V'][1] < 3.6
    assert calculations['core_buck_tolerance_before_P4_control_V'][0] > .99
    assert calculations['core_buck_tolerance_before_P4_control_V'][1] < 1.3
    assert max(calculations['sensor_LDO_individual_current_bounds_A'].values()) < .3
    assert max(calculations['buck_inductor_ripple_A_at_1MHz_Lminus20pct'].values())/2+1 < 2.3
    assert calculations['SCCB_rise_time_s_for_200pF'] < 1e-6
    (OUT/'component-calculations.json').write_text(json.dumps(calculations,indent=2)+'\n',encoding='utf-8')
    print(f'{len(selected)} footprints; {report["populated_count"]} populated parts; selection screens passed')


if __name__ == '__main__':
    main()
