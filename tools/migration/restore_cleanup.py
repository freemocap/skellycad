"""Restore preserved rebuild inputs into an isolated, original-layout workspace.

The main checkout is never a restoration target. Existing changed files stop
restoration rather than being overwritten. Use a new destination for a fresh run.
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
from archive_io import open_archive

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / 'docs/migration/repo-cleanup-2026-10-31'


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def restore(destination, prefixes=(), include_generated=True):
    destination = Path(destination).resolve()
    allowed = (ROOT / 'generated/replay').resolve()
    if not destination.is_relative_to(allowed) or destination == allowed:
        raise ValueError('Choose a named workspace below generated/replay/')
    inventory = json.loads((RECORDS / 'inventory.json').read_text())['records']
    expected = {r['path']: r for r in inventory}
    archives = ['source-before.zip'] + (['generated-before.zip'] if include_generated else [])
    if (RECORDS/'supplied-attachments.zip').is_file():
        archives.append('supplied-attachments.zip')
    count = 0
    for name in archives:
        with open_archive(RECORDS / name) as archive:
            for item in archive.infolist():
                if prefixes and not any(item.filename.startswith(p) for p in prefixes):
                    continue
                target = (destination / item.filename).resolve()
                if not target.is_relative_to(destination):
                    raise ValueError(f'Unsafe archive member: {item.filename}')
                record = expected[item.filename]
                if target.exists():
                    if sha(target) != record['sha256']:
                        raise ValueError(f'Existing replay file differs; use a new workspace: {target}')
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256()
                temporary = target.with_name(target.name + '.restoring')
                if temporary.exists():
                    raise ValueError(f'Incomplete restoration exists: {temporary}')
                try:
                    with archive.open(item) as src, temporary.open('xb') as dst:
                        while block := src.read(1024 * 1024):
                            digest.update(block)
                            dst.write(block)
                    if digest.hexdigest() != record['sha256']:
                        raise ValueError(f'Restored hash mismatch: {item.filename}')
                    temporary.rename(target)
                except Exception:
                    if temporary.exists():
                        temporary.unlink()
                    raise
                count += 1
                if count % 3000 == 0:
                    print(f'Restored and hashed {count} files', flush=True)
    print(f'Restored {count} files into {destination}', flush=True)
    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--prefix', action='append', default=[])
    parser.add_argument('--source-only', action='store_true')
    args = parser.parse_args()
    restore(args.destination, args.prefix, not args.source_only)
