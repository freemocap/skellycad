"""Create stage 02 in a fresh directory; retain stage 01 unchanged.

Assignments use installed KiCad footprints, not verified purchasable parts.
[@kicad10GettingStarted; @kicadLibraryLicense]
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

FOOTPRINTS = {
    'R1': 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
    'D1': 'LED_THT:LED_D5.0mm',
    'J1': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--kicad-root', type=Path, required=True)
args = parser.parse_args()
if args.output.exists():
    raise SystemExit('Choose a fresh output directory.')
source = Path(__file__).parent/'electronics/01-connected-schematic'
text = (source/'indicator.kicad_sch').read_text(encoding='utf-8')
records = {}
for ref, assignment in FOOTPRINTS.items():
    lib, name = assignment.split(':')
    footprint = args.kicad_root/'share/kicad/footprints'/f'{lib}.pretty'/f'{name}.kicad_mod'
    content = footprint.read_text(encoding='utf-8')
    assert set(re.findall(r'\(pad "([^"]+)"', content)) == {'1', '2'}
    model = re.search(r'\(model "([^"]+)"', content)[1]
    model_path = Path(model.replace('${KICAD10_3DMODEL_DIR}', str(args.kicad_root/'share/kicad/3dmodels')))
    assert model_path.is_file(), model_path
    pattern = rf'(\(property "Reference" "{ref}".*?\(property "Footprint" )""'
    text, count = re.subn(pattern, lambda match: match[1]+json.dumps(assignment), text, count=1, flags=re.S)
    assert count == 1
    records[ref] = {'footprint':assignment, 'pads':['1','2'], 'model':model,
                    'footprint_sha256':hashlib.sha256(footprint.read_bytes()).hexdigest(),
                    'model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest()}
text = text.replace('01 / A circuit is connectivity', '02 / Symbols now have footprints')
text = text.replace('Footprints and PCB layout come later. Not a fabrication release.',
                    'Footprints assigned; PCB layout comes next. Teaching packages only.')
args.output.mkdir(parents=True)
(args.output/'indicator.kicad_sch').write_text(text,encoding='utf-8')
(args.output/'indicator.kicad_pro').write_bytes((source/'indicator.kicad_pro').read_bytes())
(args.output/'source-record.json').write_text(json.dumps({
    'stage':'02-assigned-footprints','parent':'01-connected-schematic',
    'parent_sha256':hashlib.sha256((source/'indicator.kicad_sch').read_bytes()).hexdigest(),
    'schematic_sha256':hashlib.sha256(text.encode()).hexdigest(), 'units':'mm',
    'assignments':records, 'status':'Teaching packages; physical part selection and PCB layout pending',
},indent=2)+'\n')
print(args.output.resolve())
