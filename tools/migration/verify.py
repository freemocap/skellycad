"""Verify retained migration evidence; works after the old copy is removed."""
from pathlib import Path
import hashlib
import json
import zipfile
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    sys.path.insert(0,str(ROOT/'designs/eye-tracker'))
    from shared.paths import repository_path
    from shared.model import load_manifest
    overrides=json.loads((ROOT/'docs/migration/repo-cleanup-2026-10-31/import-overrides.json').read_text())
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
                actual = sha(repository_path(target))
                expected = overrides.get(target, {}).get('sha256', changes.get(target, {}).get('sha256', record['sha256']))
                if target in changes:
                    assert sha(ROOT / changes[target]['original']) == record['sha256'], f'Original evidence missing: {target}'
            assert actual == expected, f"Retained file changed: {record['source']}"
    manifest_path = ROOT / 'designs/eye-tracker/mouse/active-model.json'
    manifest,checkpoint = load_manifest(manifest_path)
    assert sha(checkpoint) == manifest['native_sha256']
    for key in ('build_script', 'export_script'):
        assert repository_path(manifest[key]).is_file(), key
    lineage = json.loads(repository_path(manifest['lineage']).read_text())
    checked = []
    def verify_assets(value):
        if isinstance(value, dict):
            for path_key, hash_key in [('path','sha256'),('native_checkpoint','native_sha256')]:
                if isinstance(value.get(path_key),str) and isinstance(value.get(hash_key),str):
                    path=repository_path(value[path_key])
                    assert sha(path)==value[hash_key], str(path)
                    checked.append(str(path))
            for child in value.values():verify_assets(child)
        elif isinstance(value,list):
            for child in value:verify_assets(child)
    verify_assets(lineage)
    assert checked, 'Selected lineage contains no checked inputs'
    print(f"Verified {len(inventory['records'])} migration records and {manifest['revision']} mouse baseline.")


if __name__ == '__main__':
    main()
