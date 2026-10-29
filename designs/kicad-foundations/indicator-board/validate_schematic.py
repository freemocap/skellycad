"""Validate the lesson's intended circuit with KiCad, not our file generator.

Run with --cli <kicad-cli.exe> --output <new-report-directory>.
"""
import argparse
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cli', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
sch = Path(__file__).parent / 'electronics/01-connected-schematic/indicator.kicad_sch'
args.output.mkdir(parents=True, exist_ok=False)
for command in [
    ['sch', 'export', 'netlist', '--format', 'kicadxml', '--output', str(args.output/'netlist.xml')],
    ['sch', 'erc', '--format', 'json', '--exit-code-violations', '--output', str(args.output/'erc.json')],
    ['sch', 'export', 'svg', '--exclude-drawing-sheet', '--output', str(args.output)],
]:
    subprocess.run([str(args.cli), *command, str(sch)], check=True)
tree = ET.parse(args.output/'netlist.xml')
actual = {net.attrib['name']: sorted((node.attrib['ref'],node.attrib['pin']) for node in net.findall('node'))
          for net in tree.findall('./nets/net')}
expected = {'/SUPPLY':[('J1','1'),('R1','1')], '/LED_ANODE':[('D1','2'),('R1','2')],
            '/RETURN':[('D1','1'),('J1','2')]}
if actual != expected:
    raise SystemExit(f'Connectivity mismatch: {actual!r}')
if sorted(c.attrib['ref'] for c in tree.findall('./components/comp')) != ['D1','J1','R1']:
    raise SystemExit('Unexpected component set')
report = {'status':'passed', 'nets':actual, 'erc':'zero reported violations',
          'limits':'No footprints, component ratings, PCB, simulation or physical test validated.'}
(args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: exactly three components, three intended nets, and zero ERC violations.')
