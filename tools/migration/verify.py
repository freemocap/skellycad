"""Verify retained migration evidence; works after the old copy is removed."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    inventory = json.loads((ROOT / 'docs/migration/inventory.json').read_text())
    archive_path = ROOT / 'docs/migration/playground-artifacts.zip'
    assert sha(archive_path) == inventory['archive_sha256'], 'Historical archive hash mismatch'
    changes_path = ROOT / 'docs/migration/changes.json'
    changes = json.loads(changes_path.read_text()) if changes_path.exists() else {}
    with zipfile.ZipFile(archive_path) as archive:
        for record in inventory['records']:
            if 'member' in record:
                actual = hashlib.sha256(archive.read(record['member'])).hexdigest()
                expected = record['sha256']
            else:
                target = record['destination']
                actual = sha(ROOT / target)
                expected = changes.get(target, {}).get('sha256', record['sha256'])
                if target in changes:
                    assert sha(ROOT / changes[target]['original']) == record['sha256'], f'Original evidence missing: {target}'
            assert actual == expected, f"Retained file changed: {record['source']}"
    manifest_path = ROOT / 'designs/eye-tracker/mouse/active-model.json'
    manifest = json.loads(manifest_path.read_text())
    assert sha(ROOT / manifest['native_checkpoint']) == manifest['native_sha256']
    for key in ('build_script', 'export_script'):
        assert (ROOT / manifest[key]).is_file(), key
    lineage = json.loads((ROOT / manifest['lineage']).read_text())
    for asset in lineage['assets']:
        assert sha(ROOT / asset['path']) == asset['sha256'], asset['path']
    print(f"Verified {len(inventory['records'])} migration records and {manifest['revision']} mouse baseline.")


if __name__ == '__main__':
    main()
