"""Fetch, verify and measure the vendor CAD and datasheets listed in references/vendor.json.

Files with a redistribution licence are kept in references/. The others are pinned by URL
and SHA-256 and downloaded into generated/ultraskelly/vendor/<id>/, which Git ignores.
Run from the repository root:

    python -B designs/ultraskelly/src/vendor.py fetch     # download missing pinned files
    python -B designs/ultraskelly/src/vendor.py verify    # check every file against its SHA-256
    .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe -B designs/ultraskelly/src/vendor.py extents

`extents` needs the pinned FreeCAD Python. It writes the STEP models' bounding boxes to
generated/ultraskelly/vendor/extents.json.
"""
import argparse
import hashlib
import json
import urllib.request
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
            'pca9685-step': step_extents('pca9685-step'),
            'zed-mini-step': step_extents('zed-mini-step'),
            'oak1-pcba-step': step_extents('oak1-pcba-step'),
            'oak1-enclosure-step': step_extents('oak1-enclosure-step')}}
        CACHE.mkdir(parents=True, exist_ok=True)
        (CACHE / 'extents.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
