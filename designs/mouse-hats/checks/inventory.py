"""Read-only supplied-file inventory; paths and hashes are relative to this project."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import zipfile

PROJECT = Path(__file__).resolve().parents[1]


def main():
    entries = []
    for path in sorted((PROJECT / 'old').rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(PROJECT).as_posix()
        role = 'historical-reference'
        if '/rebuild/' in relative:
            role = 'prior-inspection-artifact'
        elif path.suffix.lower() == '.step':
            role = 'candidate-cad-baseline'
        elif 'camera-assembly-2arm-v' in path.name:
            role = 'later-mesh-variant'
        elif path.suffix.lower() == '.f3d':
            role = 'original-authoring-archive'
        entry = dict(path=relative, bytes=path.stat().st_size,
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest(), role=role)
        if path.suffix.lower() in ('.f3d', '.3mf') and zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive:
                entry['archive_members'] = archive.namelist()
        entries.append(entry)
    hashes = defaultdict(list)
    for entry in entries:
        if entry['bytes']:
            hashes[entry['sha256']].append(entry['path'])
    previous = json.loads((PROJECT/'old/df-hardware/rebuild/baseline/reference-inventory.json').read_text())
    verification = []
    by_path = {e['path']: e for e in entries}
    for entry in previous:
        relative = 'old/df-hardware/' + entry['path'].removeprefix('hardware/')
        current = by_path.get(relative)
        verification.append(dict(path=relative, status='missing' if current is None else
                                 'match' if current['sha256'] == entry['sha256'] else 'changed'))
    report = dict(schema_version=1, scope='user-supplied old/ only',
        coordinate_policy='Preserve source frames; no implicit scale, centering, alignment or repair.',
        baseline_status='not selected; CAD parity precedes mesh-change reconstruction',
        stl_units='unknown until checked against a known physical dimension',
        files=entries, identical_file_groups=[paths for paths in hashes.values() if len(paths)>1],
        previous_inventory_verification=verification)
    target = PROJECT/'references.json'
    if target.exists():
        assert json.loads(target.read_text()) == report, 'Inventory changed; review before replacing baseline.'
    else:
        target.write_text(json.dumps(report, indent=2)+'\n')
    print('Files:',len(entries),'extensions:',dict(Counter(Path(e['path']).suffix.lower() for e in entries)))
    print('Prior inventory:',dict(Counter(e['status'] for e in verification)))
    print('Identical file groups:',len(report['identical_file_groups']))


if __name__ == '__main__':
    main()
