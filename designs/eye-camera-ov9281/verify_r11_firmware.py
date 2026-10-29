"""Verify R11 schematic/firmware bindings and offline build/recording evidence."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET,zlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];FW=HERE/'firmware';SPEC=HERE/'electronics/r11'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    contract=json.loads((FW/'board-contract.json').read_text());tree=ET.parse(ROOT/'generated/ov9281-r11-electronics/source-netlist.xml')
    nets={(q.get('ref'),q.get('pin')):n.get('name') for n in tree.findall('nets/net') for q in n.findall('node')}
    nodes={(q.get('ref'),q.get('pin')):q for n in tree.findall('nets/net') for q in n.findall('node')}
    comps={c.get('ref'):c for c in tree.findall('components/comp')};source=(FW/'main/camera_main.c').read_text();checked={}
    for constant,c in contract['gpio'].items():
        assert int(re.search(r'\b'+constant+r'\s*=\s*(\d+)',source).group(1))==c['gpio']
        assert nets['U101',c['pad']]==c['net'];assert re.match(r'GPIO'+str(c['gpio'])+r'(?:_|/|$)',nodes['U101',c['pad']].get('pinfunction',''))
        checked[constant]=c
    assert nets['Q103','1']==nets['U101','6'] and nets['Q103','2']=='GND' and nets['Q103','3']==nets['U1','A5']
    assert nets['R8','1']==nets['U1','E1'] and nets['R8','2']=='GND'
    assert comps['R7'].find("property[@name='dnp']") is not None and comps['R8'].find("property[@name='dnp']") is None
    assert nets['R203','1']==nets['U101','5'] and nets['R203','2']==nets['Q201','1']==nets['R204','1']
    assert nets['Q201','2']==nets['R204','2']=='GND'
    assert '.scl_speed_hz = '+str(contract['sccb_hz']) in source and '.reset_pin = -1' in source
    assert 'gpio_set_level(LED_GPIO, 0)' in source and source.count('gpio_set_level(LED_GPIO,')==1
    for pin,net in contract['usb_connector'].items():assert nets['J101',pin]==net
    for pin,net in contract['programming_pads'].items():assert nets['J103',pin]==net
    assert nets['Y1','4']=='+1V8'
    # Flash uses the P4's default 3.3 V flash output, not the raw system rail.
    assert nets['U102','8']==nets['U101','30']==nets['U101','71']=='/P4_FLASH_VDD'
    assert nodes['U101','71'].get('pinfunction')=='VDDO_FLASH_71'
    assert int(re.search(r'WIDTH = (\d+)',source).group(1))==contract['capture']['width'];assert int(re.search(r'HEIGHT = (\d+)',source).group(1))==contract['capture']['height']
    builds={}
    for mode in ['sensor','synthetic']:
        folder=ROOT/'generated/camera-firmware-r11'/mode;record=json.loads((folder/'build-report.json').read_text());assert record['compiled'] and not record['executed_on_hardware']
        for name,digest in record['source_sha256'].items():assert sha(FW/name)==digest,name
        for name,digest in record['binary_sha256'].items():assert sha(folder/'build'/name)==digest,name
        cfg=(folder/'sdkconfig').read_text()
        for required in ['CONFIG_ESP32P4_REV_MIN_FULL=300','CONFIG_TINYUSB_RHPORT_HS=y','CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y','CONFIG_ESPTOOLPY_FLASHMODE_DIO=y','CONFIG_ESPTOOLPY_FLASHFREQ_40M=y','CONFIG_CAMERA_OV9281_SID_LOW=y','CONFIG_SPIRAM=y','CONFIG_SKELLY_CSI_LANE_MBPS=800']:
            assert required in cfg,(mode,required)
        assert ('CONFIG_SKELLY_SYNTHETIC=y' in cfg)==(mode=='synthetic')
        flash=json.loads((folder/'build/flasher_args.json').read_text());files={name:sha(folder/'build'/name) for name in flash['flash_files'].values()}
        assert len(files)>=3
        linkmap=(folder/'build/skelly_eye_camera.map').read_text();excluded=['libesp_ipa.a','libesp_h264.a','libnet80211.a','libpp.a','libcoexist.a','libesp_wifi.a'];assert all(n not in linkmap for n in excluded)
        builds[mode]={'build_report_sha256':sha(folder/'build-report.json'),'flash_file_sha256':files,'flash_offsets':flash['flash_files'],'effective_config_sha256':sha(folder/'sdkconfig'),'compiled':True,'executed_on_hardware':False}
    tests=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(FW/'host'),'-p','test_camera_link.py','-v'],capture_output=True,text=True);assert tests.returncode==0,tests.stdout+tests.stderr
    recording=ROOT/'generated/camera-loopback-r11';r=json.loads((recording/'recording.json').read_text());assert not r['physical_capture_demonstrated'] and len(r['frames'])==3
    assert r['software_target']['contract_sha256']==sha(FW/'board-contract.json') and not r['software_target']['device_identity_verified']
    for f in r['frames']:
        assert f['synthetic'] and f['width']==640 and f['height']==400
        header,pixels=(recording/f['file']).read_bytes().split(b'255\n',1);assert header==b'P5\n640 400\n' and len(pixels)==256000 and f'{zlib.crc32(pixels):08x}'==f['crc32']
    report={'status':'pass','board_revision':'R11','board_contract_sha256':sha(FW/'board-contract.json'),'schematic_netlist_sha256':sha(ROOT/'generated/ov9281-r11-electronics/source-netlist.xml'),'gpio_bindings':checked,'reset_inversion_sid_low_led_off_and_connector_checks':True,'builds':builds,'host_tests':tests.stderr,'host_source_sha256':{p.name:sha(p) for p in (FW/'host').glob('*.py')},'recording_sha256':sha(recording/'recording.json'),'synthetic_frames_verified':3,'physical_camera_demonstrated':False,'uvc_implemented':False,'continuous_streaming_implemented':False,'remaining_hardware_checks':['Supply sequencing, current, inrush, USB descriptors and thermal behavior','Actual sensor clock, SCCB detection and 400 MHz clock / 800 Mbps DDR lane interpretation','Camera DMA/cache ownership under real transfers and USB interruptions','Exposure/gain behavior, throughput, close-focus IR image quality and IR exposure']}
    (SPEC/'firmware-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'pass','builds':list(builds),'synthetic_frames':3,'physical_camera_demonstrated':False},indent=2))
if __name__=='__main__':main()
