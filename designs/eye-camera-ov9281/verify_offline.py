"""Recheck the selected artifact bundle; distinguish checks from release gates.

Does not alter native CAD files, flash devices, or report simulated pixels as
camera capture. Run after building both firmware variants with build.py.
"""
from pathlib import Path
import hashlib, json, re, subprocess, sys, xml.etree.ElementTree as ET
from system_analysis import analysis

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify():
    selection=json.loads((HERE/'controller-selection.json').read_text())
    board=HERE/Path(selection['validation']).parent
    validation=json.loads((board/'validation.json').read_text())
    for name,digest in validation['sha256'].items():assert sha(board/name)==digest,name
    parent=json.loads((board/'routing-r08.json').read_text())['parent_sha256']
    for name,digest in parent.items():assert sha(HERE/'electronics/r07'/name)==digest,name
    tree=ET.parse(board/'source-netlist.xml')
    nets={(q.get('ref'),q.get('pin')):n.get('name') for n in tree.findall('.//nets/net') for q in n}
    source=(HERE/'firmware/main/camera_main.c').read_text()
    bindings={'LED_GPIO':'/LED_PWM','RESET_ASSERT_GPIO':'/CAM_RESET_ASSERT',
              'SCL_GPIO':'/CAM_SCL_3V3','SDA_GPIO':'/CAM_SDA_3V3'}
    checked={}
    for constant,net in bindings.items():
        pin=re.search(r'\b'+constant+r'\s*=\s*(\d+)',source).group(1)
        assert nets[('U101',pin)]==net
        checked[constant]={'gpio':int(pin),'schematic_net':net}
    assert nets[('Q103','1')]==nets[('U101','6')]
    assert nets[('Q103','2')]=='GND'
    assert nets[('Q103','3')]==nets[('U1','A5')]
    assert nets[('R8','1')]==nets[('U1','E1')]
    assert nets[('R8','2')]=='GND'
    comps={x.get('ref'):x for x in tree.findall('.//components/comp')}
    assert comps['R7'].find("property[@name='dnp']") is not None
    assert comps['R8'].find("property[@name='dnp']") is None
    assert 'CONFIG_CAMERA_OV9281_SID_LOW=y' in (HERE/'firmware/sdkconfig.defaults').read_text()
    builds={}
    for mode in ['sensor','synthetic']:
        folder=ROOT/'generated'/('camera-firmware-'+mode)
        record=json.loads((folder/'build-report.json').read_text())
        assert record['compiled'] and not record['executed_on_hardware']
        for name,digest in record['source_sha256'].items():assert sha(HERE/'firmware'/name)==digest,name
        for name,digest in record['binary_sha256'].items():assert sha(folder/'build'/name)==digest,name
        config=(folder/'sdkconfig').read_text()
        assert 'CONFIG_ESP32P4_REV_MIN_FULL=300' in config
        assert 'CONFIG_TINYUSB_RHPORT_HS=y' in config
        assert ('CONFIG_SKELLY_SYNTHETIC=y' in config)==(mode=='synthetic')
        builds[mode]=record
    tests=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(HERE/'firmware/host'),'-p','test_*.py','-v'],capture_output=True,text=True)
    assert tests.returncode==0,tests.stdout+tests.stderr
    # The linked binary has no camera codec/IPA or radio blob library. This is
    # a narrow map check, not a legal audit of every toolchain runtime object.
    linkmap=(ROOT/'generated/camera-firmware-sensor/build/skelly_eye_camera.map').read_text()
    excluded=['libesp_ipa.a','libesp_h264.a','libnet80211.a','libpp.a','libcoexist.a','libesp_wifi.a']
    assert all(name not in linkmap for name in excluded)
    inventory=json.loads((board/'inventory.json').read_text())
    assert len(inventory['items'])==sum(x['footprints'] for x in validation['boards'].values())
    mechanical_folder=ROOT/'generated/ov9281-r08-desktop'
    mechanical=json.loads((mechanical_folder/'review-status.json').read_text())
    export_sources=json.loads((mechanical_folder/'source-record.json').read_text())
    assert export_sources['native_sha256']==validation['sha256']
    assert mechanical['pin_xy_alignment_checks']==24
    for name,entry in mechanical['boards'].items():
        assert entry['valid'] and entry['solids']>0
        assert sha(mechanical_folder/(name+'.step'))==entry['source_sha256']
    mechanical['saved_document_sha256']=sha(mechanical_folder/'OV9281-R08-PCB-REVIEW.FCStd')
    oscillator={'reference':'Y1','value':comps['Y1'].findtext('value'),
        'supply_net':nets[('Y1','4')],'description':comps['Y1'].findtext('description'),
        'status':'Unresolved 3.3 V part metadata versus 1.8 V supply; verify exact part and land pattern before assembly'}
    result={'revision':selection['revision'],'offline_checks_passed':True,
        'fabrication_ready':False,'physical_camera_demonstrated':False,
        'native_file_hashes':validation['sha256'],'firmware_gpio_bindings':checked,
        'reset_inversion_and_sid_low_netlist_checks':True,'builds':builds,
        'host_test_output':tests.stderr,'excluded_link_libraries_checked':excluded,
        'unconnected_items':{n:d['unconnected_items'] for n,d in validation['boards'].items()},
        'oscillator_selection_conflict':oscillator,'analysis':analysis(),'mechanical_review':mechanical,
        'remaining_computer_work':['Finish PCB routing including MIPI/USB constraints and flash.',
            'Resolve Y1 voltage/land-pattern conflict; complete component and power-sequencing audit.',
            'Complete illumination circuit and select lens, filter and mechanical interfaces.',
            'Define manufacturer stackup, impedance and assembly constraints.',
            'Resolve 400/800 Mbps receiver timing discrepancy; add exposure/gain controls and continuous transport.'],
        'hardware_required':['Power sequencing/current/thermal measurements.',
            'Actual RAW8 frames, CSI timing, USB enumeration and throughput.',
            '940 nm focus/field-of-view and LED optical exposure measurements.',
            'Assembly fit, bending, mass and durability.']}
    dest=HERE/'verification';dest.mkdir(exist_ok=True)
    (dest/'offline-report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['revision','offline_checks_passed','fabrication_ready','physical_camera_demonstrated','unconnected_items']},indent=2))

if __name__=='__main__':verify()
