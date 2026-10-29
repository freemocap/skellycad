"""Check exported netlist against the reviewed host pin map [@raspberryPiCameraPinout]."""
import sys
import xml.etree.ElementTree as ET

expected_pins = {
    'GND': [1, 4, 7, 10], 'CAM_D0_N': [2], 'CAM_D0_P': [3],
    'CAM_D1_N': [5], 'CAM_D1_P': [6], 'CAM_CLK_N': [8],
    'CAM_CLK_P': [9], 'CAM_IO0': [11], 'CAM_IO1': [12],
    'CAM_SCL': [13], 'CAM_SDA': [14], 'CAM_3V3': [15],
}
root = ET.parse(sys.argv[1]).getroot()
expected = {name: sorted((ref, str(pin)) for ref in ['J1', 'J2'] for pin in pins)
            for name, pins in expected_pins.items()}
actual = {net.attrib['name'].removeprefix('/'): sorted(
    (node.attrib['ref'], node.attrib['pin']) for node in net.findall('node'))
    for net in root.findall('./nets/net')}
if actual != expected:
    raise SystemExit(f'Pin-map mismatch: {actual!r}')
print('PASS: 12 nets, 30 endpoints; both connectors match the reviewed host map.')
