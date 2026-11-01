"""Extract reviewable sensor circuitry from pinned Antmicro source, not a release.

Source and license: [@antmicroOv9281Board; @antmicroOv9281License].
Preserves component identifiers and source sheet coordinates for comparison.
"""
from pathlib import Path
import hashlib
import json
import re
import uuid

ROOT = Path(__file__).resolve().parent


def children(source):
    depth, quoted, escaped, start = 0, False, False, 0
    for index, char in enumerate(source):
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == '(':
            depth += 1
            if depth == 2:
                start = index
        elif char == ')':
            if depth == 2:
                yield source[start:index + 1]
            depth -= 1
    if depth or quoted:
        raise ValueError('Unbalanced source')


def main():
    src = ROOT / 'reference/antmicro/ov9281-dual-camera-board.kicad_sch'
    out = ROOT / 'electronics/r01'
    if out.exists():
        raise SystemExit('Choose a new revision; do not overwrite an editor buffer.')
    # Disjoint source-sheet regions: sensor 1, three supply regulators,
    # sensor 1 supply filters, and its input-clock oscillator.
    regions = [(0, 0, 123, 130), (0, 140, 145, 202),
               (0, 220, 210, 245), (230, 30, 303, 65)]
    def region(x, y):
        return next((i for i, (a,b,c,d) in enumerate(regions)
                     if a <= x <= c and b <= y <= d), None)
    blocks, refs = [], []
    for block in children(src.read_text(encoding='utf-8')):
        kind = re.match(r'\(([^\s)]+)', block)[1]
        if kind in {'version', 'generator', 'generator_version', 'uuid', 'paper', 'lib_symbols', 'sheet_instances', 'embedded_fonts'}:
            blocks.append(block)
            continue
        if kind == 'title_block':
            blocks.append('(title_block (title "OV9281 single-head circuit draft") (date "2026-10-27") (rev "R01 - incomplete") (company "SkellyCAD; derived from Antmicro Apache-2.0"))')
            continue
        if kind not in {'symbol', 'wire', 'junction', 'no_connect', 'label', 'global_label'}:
            continue
        coords = re.findall(r'\(xy\s+([-\d.]+)\s+([-\d.]+)', block) if kind == 'wire' else re.findall(r'\(at\s+([-\d.]+)\s+([-\d.]+)', block)[:1]
        zones = [region(float(x),float(y)) for x,y in coords]
        if not zones or zones[0] is None or any(z != zones[0] for z in zones):
            continue
        if kind == 'symbol':
            refs.append(re.search(r'\(property "Reference" "([^"]+)"',block)[1])
            block = block.replace('(project "ov9281-dual-camera-board"', '(project "ov9281-head"')
        blocks.append(block)
    for i, text in enumerate([
        'R01 CIRCUIT EXTRACTION - NOT FOR FABRICATION',
        'Derived from Antmicro ea69666f / Apache-2.0. Original references retained.',
        'External nets are unfinished interfaces: flex connector and receiver pending.',
        'LED drive, USB, ESP32-P4 and optics are not implemented on this sheet.',
        'Power and clock placement between head/controller remains to be resolved.',
    ]):
        blocks.append(f'(text "{text}" (at 230 {145+i*7} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uuid.uuid5(uuid.NAMESPACE_URL,text)}"))')
    out.mkdir(parents=True)
    (out/'ov9281-head.kicad_sch').write_text('(kicad_sch\n'+'\n'.join(blocks)+'\n)\n',encoding='utf-8')
    (out/'ov9281-head.kicad_pro').write_text(json.dumps({'meta':{'filename':'ov9281-head.kicad_pro','version':1}},indent=2)+'\n')
    (out/'extraction.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_commit':'ea69666fa06f66a0691e50eebff9356cc2a08e32','source_regions_mm':regions,'references':sorted(refs),'status':'Partial circuit; interface and electrical validation pending'},indent=2)+'\n')
    print(f'Extracted {len(refs)} symbols into {out}')


if __name__ == '__main__':
    main()
