"""Fetch, verify and measure the vendor CAD and datasheets listed in references/vendor.json.

Files with a redistribution licence are kept in references/. The others are pinned by URL
and SHA-256 and downloaded into generated/ultraskelly/vendor/<id>/, which Git ignores.
Run from the repository root:

    python -B designs/ultraskelly/src/vendor.py fetch     # download missing pinned files
    python -B designs/ultraskelly/src/vendor.py verify    # check every file against its SHA-256
    .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe -B designs/ultraskelly/src/vendor.py extents

`extents` needs the pinned FreeCAD Python. It writes STEP bounding boxes and the servo HAT
board outline to generated/ultraskelly/vendor/extents.json.
"""
import argparse
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
MANIFEST = PROJECT / 'references' / 'vendor.json'
CACHE = ROOT / 'generated' / 'ultraskelly' / 'vendor'


def entries():
    return json.loads(MANIFEST.read_text(encoding='utf-8'))['files']


def location(entry):
    if entry['retention'] == 'repository':
        return PROJECT / 'references' / entry['path']
    return CACHE / entry['id'] / entry['file']


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(entry):
    target = location(entry)
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + '.partial')
    request = urllib.request.Request(entry['url'], headers={'User-Agent': 'Mozilla/5.0 (skellycad vendor fetch)'})
    with urllib.request.urlopen(request, timeout=120) as response, open(partial, 'wb') as out:
        while chunk := response.read(1 << 20):
            out.write(chunk)
    if sha256(partial) != entry['sha256']:
        partial.unlink()
        raise ValueError(f"{entry['id']}: download does not match the pinned SHA-256; the source changed")
    partial.replace(target)
    return target


def path(item_id):
    """Return the verified local path of one vendor file, fetching a pinned file on first use."""
    entry = next(e for e in entries() if e['id'] == item_id)
    target = location(entry)
    if entry['retention'] == 'fetch' and not target.exists():
        fetch(entry)
    if sha256(target) != entry['sha256']:
        raise ValueError(f'{target}: SHA-256 differs from references/vendor.json')
    return target


def step_extents(item_id, member=None):
    """Bounding box of a STEP model in its own coordinates, millimetres."""
    import FreeCAD  # noqa: F401  # adds FreeCAD's module paths before Part
    import Part
    source = path(item_id)
    if member:
        extracted = CACHE / item_id / Path(member).name
        if not extracted.exists():
            with zipfile.ZipFile(source) as archive:
                extracted.parent.mkdir(parents=True, exist_ok=True)
                extracted.write_bytes(archive.read(member))
        source = extracted
    shape = Part.read(str(source))
    box = shape.BoundBox
    return {'file': source.name, 'solids': len(shape.Solids),
            'min_mm': [round(v, 3) for v in (box.XMin, box.YMin, box.ZMin)],
            'max_mm': [round(v, 3) for v in (box.XMax, box.YMax, box.ZMax)],
            'size_mm': [round(v, 3) for v in (box.XLength, box.YLength, box.ZLength)]}


def board_outline(item_id):
    """Board outline (EAGLE Dimension layer 20) and holes, from the board and its placed packages.

    Outline extents use wire end points, which bound convex corner arcs. Mirrored (bottom-side)
    packages are skipped unless they carry outline wires or holes, which are then rejected.
    """
    import math
    board = ET.parse(path(item_id)).getroot().find('drawing/board')
    packages = {(lib.get('name'), pkg.get('name')): pkg
                for lib in board.iterfind('libraries/library') for pkg in lib.iterfind('packages/package')}
    placed = [(board.find('plain'), 0.0, 0.0, 0.0)]
    for element in board.iterfind('elements/element'):
        package = packages[element.get('library'), element.get('package')]
        rotation = element.get('rot') or 'R0'
        if rotation.startswith('M'):
            if package.find('wire[@layer="20"]') is not None or package.find('hole') is not None:
                raise ValueError(f"{element.get('name')}: mirrored package with outline or holes")
            continue
        placed.append((package, float(element.get('x')), float(element.get('y')),
                       math.radians(float(rotation[1:]))))
    points, holes = [], []
    for container, dx, dy, angle in placed:
        c, s = math.cos(angle), math.sin(angle)
        move = lambda x, y: (round(dx + c * x - s * y, 4), round(dy + s * x + c * y, 4))
        for wire in container.iterfind('wire[@layer="20"]'):
            points += [move(float(wire.get('x1')), float(wire.get('y1'))),
                       move(float(wire.get('x2')), float(wire.get('y2')))]
        holes += [[*move(float(h.get('x')), float(h.get('y'))), float(h.get('drill'))]
                  for h in container.iterfind('hole')]
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return {'outline_min_mm': [min(xs), min(ys)], 'outline_max_mm': [max(xs), max(ys)],
            'outline_size_mm': [round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)],
            'holes_x_y_drill_mm': sorted(holes)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('command', choices=['fetch', 'verify', 'extents'])
    args = parser.parse_args()
    if args.command == 'fetch':
        for entry in entries():
            if entry['retention'] == 'fetch':
                print(entry['id'], path(entry['id']))
    elif args.command == 'verify':
        failures = 0
        for entry in entries():
            target = location(entry)
            state = 'missing' if not target.exists() else 'ok' if sha256(target) == entry['sha256'] else 'MISMATCH'
            failures += state != 'ok'
            print(f"{state:8} {entry['retention']:10} {entry['id']}")
        raise SystemExit(1 if failures else 0)
    else:
        report = {'units': 'mm', 'steps': {
            'pi5-step': step_extents('pi5-step', 'rpi-5b_no_graphics.step'),
            'motor-hat-step': step_extents('motor-hat-step'),
            'zed-mini-step': step_extents('zed-mini-step'),
            'oak1-pcba-step': step_extents('oak1-pcba-step'),
            'oak1-enclosure-step': step_extents('oak1-enclosure-step')},
            'servo-hat-board': board_outline('servo-hat-board')}
        CACHE.mkdir(parents=True, exist_ok=True)
        (CACHE / 'extents.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
