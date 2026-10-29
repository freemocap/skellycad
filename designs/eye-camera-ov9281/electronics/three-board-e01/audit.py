"""Independent electrical contracts plus native pad/net validation.
[@ti953A01; @ti954A01; @tiTps2553E01; @usbIsoBudgetE01]
"""
from pathlib import Path
import json,sys,math
import pcbnew as pcb
from check_native import check
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'generated/three-board-e01'
head=json.loads((HERE/'head-interface-components.json').read_text());base=json.loads((HERE/'base-components.json').read_text())
checks=[]
def require(name,ok):
    checks.append({'check':name,'pass':bool(ok)})
    assert ok,name
def pins(parts,ref,expected):return all(parts[ref]['pin_nets'][str(k)]==v for k,v in expected.items())
native=[check('head-interface'),check('base')]
for name,parts in [('head-interface',head),('base',base)]:
    for ref,p in parts.items():
        fp=pcb.FootprintLoad(str(OUT/name/'Camera.pretty'),p['footprint'].split(':')[1])
        require(name+'/'+ref+' footprint loads',fp is not None)
        physical={x.GetNumber() for x in fp.Pads() if x.GetNumber() and x.GetNumber() not in {'MP'}}
        require(name+'/'+ref+' symbol-pad set',physical==set(p['pin_nets']))
require('Sensor lanes and polarity preserved',pins(head,'U1',{'H4':'CAM_L_CLK_N','G4':'CAM_L_CLK_P','H3':'CAM_L_D0_N','G3':'CAM_L_D0_P','F5':'CAM_L_D1_N','G5':'CAM_L_D1_P'}))
require('Serializer lane and polarity map',pins(head,'U201',{1:'CAM_L_D1_P',2:'CAM_L_D1_N',3:'CAM_L_D0_P',4:'CAM_L_D0_N',5:'CAM_L_CLK_P',6:'CAM_L_CLK_N'}))
require('Receiver lane and polarity map',pins(base,'U301',{11:'CAM_L_CLK_N',12:'CAM_L_CLK_P',13:'CAM_L_D0_N',14:'CAM_L_D0_P',15:'CAM_L_D1_N',16:'CAM_L_D1_P'}))
require('P4 dedicated CSI pins',pins(base,'U101',{45:'CAM_L_CLK_N',44:'CAM_L_CLK_P',42:'CAM_L_D0_N',43:'CAM_L_D0_P',46:'CAM_L_D1_N',47:'CAM_L_D1_P'}))
require('954 internal LDO mode and required ground',pins(base,'U301',{46:'GND',44:'GND',49:'GND'}))
require('TPS2553 WSON pin mapping, not SOT23',pins(base,'U303',{1:'TETHER_5V',2:'TETHER_ILIM',3:'TETHER_FAULT_N',4:'TETHER_EN',5:'GND',6:'B5V',7:'GND'}))
require('LPF1 returns to VDDPLL',any(p['value']=='22n' and set(p['pin_nets'].values())=={'SER_LPF1','SER_VDDPLL'} for p in head.values()))
for rail in ['SER_PLL_CAP','SER_DRV_CAP','SER_D_CAP']:
    values={p['value'] for p in head.values() if p['reference'].startswith('C') and set(p['pin_nets'].values())=={rail,'GND'}}
    require(rail+' independent required bypass',{'10u','100n','10n'}<=values)
for rail in ['RX_D_CAP','RX_CSI_CAP','RX_FPD0_CAP','RX_FPD1_CAP']:
    values={p['value'] for p in base.values() if p['reference'].startswith('C') and set(p['pin_nets'].values())=={rail,'GND'}}
    require(rail+' independent internal bypass',{'4.7u','100n'}<=values)
require('Head I2C 1.8V, base I2C 3.3V',pins(head,'U201',{23:'M1_CAM_SDA_1V8',24:'M1_CAM_SCL_1V8'}) and pins(base,'U301',{1:'BASE_SDA',2:'BASE_SCL'}))
require('Sensor SID low, alternative pullup DNP',not head['R7']['populated'] and head['R8']['populated'])
require('Both tether connectors agree on signal polarity',pins(head,'J201',{1:'H5V',2:'LINK_N',3:'LINK_P',4:'GND'}) and pins(base,'J301',{1:'TETHER_5V',2:'LINK_N',3:'LINK_P',4:'GND'}))
require('Host VBUS isolated from base main power',pins(base,'U104',{3:'B5V',5:'B5V'}) and pins(base,'J101',{1:'USB_VBUS'}) and pins(base,'Q302',{1:'USB_VBUS_GATE',3:'USB_PRESENT_N'}))
for rail,parts in [('IR_GATE',head),('CAM_NRST_1V8',head),('TETHER_EN',base),('RX_PDB',base)]:
    require(rail+' passive default low',any(p['reference'].startswith('R') and set(p['pin_nets'].values())=={rail,'GND'} for p in parts.values()))
for name,parts in [('head',head),('base',base)]:
    require(name+' two 50V coupling capacitors',sum(p['value']=='100n/50V' for p in parts.values())==2)
    require(name+' low-capacitance signal clamps',sum(p['mpn']=='TPD1E01B04DPYR' for p in parts.values())==2)
    require(name+' clean ERC',native[0 if name=='head' else 1]['erc_violations']==0)
headnets={n for p in head.values() if p['region']=='head' for n in p['pin_nets'].values() if n}
interfacenets={n for p in head.values() if p['region']=='interface' for n in p['pin_nets'].values() if n}
model={'head_power_load_A':{'nominal':.13,'planning_high':.21},'tether_36AWG_resistance_ohm_per_m':1.36,'wire_resistance_scope':'20 C copper estimate; not a qualified cable',
 'TPS2553_limit_mA_with_1pct_R':{'min':25230/(80.6*1.01)**1.016,'nominal':23950/80.6**.977,'max':22980/(80.6*.99)**.94},
 'head_voltage_at_60cm_210mA_4_75V_input':4.75-.21*(2*.6*1.36+.3),
 'RAW8_640x400_100fps_MBps':640*400*100/1e6,'RAW8_640x400_120fps_MBps':640*400*120/1e6,
 'USB_HS_iso_endpoint_payload_ceiling_MBps':3072*8000/1e6,'USB_transfer_candidate':'Bulk; RAW8 framing/host acceptance and achieved throughput unimplemented',
 'local_flex_nets':sorted(headnets&interfacenets),'addresses_7bit':{'receiver':48,'serializer':24,'sensor':96}}
(HERE/'electrical-audit.json').write_text(json.dumps({'native':native,'checks':checks,'models':model,'hardware_tested':False},indent=2)+'\n')
print(len(checks),'checks pass; budgets',model)
