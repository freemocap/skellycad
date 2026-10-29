"""Build lesson 01 in a NEW directory; never rewrite an open/accepted design.

Format: [@kicadSchematicFormat]; symbols: installed KiCad libraries.
Usage: python build_schematic.py --output <new-directory> [--kicad-root <path>]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import uuid


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'skellycad/indicator/lesson01/' + name))


def library_symbol(root, library, name):
    path = root / 'share/kicad/symbols' / (library + '.kicad_sym')
    source = path.read_text(encoding='utf-8')
    start = source.index('(symbol "' + name + '"')
    depth, quoted, escaped = 0, False, False
    for i in range(start, len(source)):
        char = source[i]
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
        elif char == ')':
            depth -= 1
            if depth == 0:
                block = source[start:i + 1]
                return block.replace(f'(symbol "{name}"', f'(symbol "{library}:{name}"', 1), {
                    'library': library, 'symbol': name,
                    'library_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                }
    raise ValueError('Unbalanced library symbol: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kicad-root', type=Path)
    args = parser.parse_args()
    candidates = [args.kicad_root, Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs/KiCad/10.0',
                  Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / 'KiCad/10.0']
    root = next((p for p in candidates if p and (p / 'bin/kicad-cli.exe').exists()), None)
    if root is None:
        raise SystemExit('Pass --kicad-root with your KiCad installation directory.')
    if args.output.exists():
        raise SystemExit('Output directory already exists; choose a fresh directory.')
    symbols, provenance = [], []
    for lib, name in [('Device', 'R'), ('Device', 'LED'), ('Connector_Generic', 'Conn_01x02')]:
        block, record = library_symbol(root, lib, name)
        symbols.append(block)
        provenance.append(record)
    sheet = uid('sheet')
    parts = [f'(kicad_sch (version 20250114) (generator "skellycad_indicator") (uuid {sheet})',
             '(paper "A4")', '(lib_symbols ' + '\n'.join(symbols) + ')']
    for ref, lib, value, x, y, angle in [
        ('J1', 'Connector_Generic:Conn_01x02', 'POWER INPUT', 152.4, 66.04, 0),
        ('R1', 'Device:R', '330', 101.6, 76.2, 0),
        ('D1', 'Device:LED', 'LED', 101.6, 96.52, 90),
    ]:
        parts.append(f'''(symbol (lib_id "{lib}") (at {x} {y} {angle}) (unit 1)
          (in_bom yes) (on_board yes) (dnp no) (uuid {uid(ref)})
          (property "Reference" "{ref}" (at {x+7.62} {y-2.54} {angle}) (effects (font (size 1.27 1.27))))
          (property "Value" "{value}" (at {x+7.62} {y} {angle}) (effects (font (size 1.27 1.27))))
          (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))
          (pin "1" (uuid {uid(ref+'/1')})) (pin "2" (uuid {uid(ref+'/2')}))
          (instances (project "indicator" (path "/{sheet}" (reference "{ref}") (unit 1)))))''')
    segments = [((147.32,66.04),(101.6,66.04)), ((101.6,66.04),(101.6,72.39)),
                ((101.6,80.01),(101.6,92.71)), ((101.6,100.33),(101.6,109.22)),
                ((101.6,109.22),(139.7,109.22)), ((139.7,109.22),(139.7,68.58)),
                ((139.7,68.58),(147.32,68.58))]
    for i, ((x1,y1),(x2,y2)) in enumerate(segments):
        parts.append(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid {uid("wire"+str(i))}))')
    for name, x, y in [('SUPPLY',116.84,66.04), ('LED_ANODE',101.6,86.36), ('RETURN',139.7,106.68)]:
        parts.append(f'(label "{name}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uid(name)}))')
    for i, (text, x, y) in enumerate([
        ('01 / A circuit is connectivity',101.6,50.8),
        ('Trace: J1.1 -> R1 -> D1 anode -> D1 cathode -> J1.2',101.6,55.88),
        ('Teaching assumptions: 5 V supply, 330 ohm resistor; LED part not selected.',101.6,119.38),
        ('Footprints and PCB layout come later. Not a fabrication release.',101.6,124.46),
    ]):
        parts.append(f'(text "{text}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid {uid("text"+str(i))}))')
    parts.extend(['(sheet_instances (path "/" (page "1")))', ')'])
    args.output.mkdir(parents=True)
    sch = args.output / 'indicator.kicad_sch'
    sch.write_text('\n'.join(parts)+'\n', encoding='utf-8')
    (args.output / 'indicator.kicad_pro').write_text(json.dumps({'meta':{'filename':'indicator.kicad_pro','version':1}}, indent=2)+'\n')
    (args.output / 'source-record.json').write_text(json.dumps({
        'stage':'01-connected-schematic', 'units':'mm', 'tested_kicad':'10.0.7',
        'symbols':provenance, 'schematic_sha256':hashlib.sha256(sch.read_bytes()).hexdigest(),
        'assumptions':{'supply_V':5, 'resistance_ohm':330, 'LED_part':'not selected'},
        'status':'Teaching circuit; no footprints, PCB, selected physical parts or powered test',
        'sources':['kicadSchematicFormat','kicad10GettingStarted','kicadLibraryLicense'],
    },indent=2)+'\n')
    print(sch.resolve())


if __name__ == '__main__':
    main()
