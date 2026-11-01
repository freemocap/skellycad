"""Capture the pre-cleanup working tree without changing existing files."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/migration/repo-cleanup-2026-10-31'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    if (OUT/'inventory.json').exists():
        raise SystemExit('This one-time cleanup step is already recorded; do not overwrite preservation evidence.')
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'inventory.json').exists(), 'Starting inventory already exists'
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
    (OUT / 'git-status-before.txt').write_bytes(subprocess.check_output(['git', 'status', '--short'], cwd=ROOT))
    (OUT / 'pending-changes-before.patch').write_bytes(subprocess.check_output(['git', 'diff', '--binary'], cwd=ROOT))
    records = []
    skipped = []
    # Runtime installations and untouched import source are outside the migration.
    excluded = {'.git', '.cad-tools', 'old-cad-playground', '.venv', '__pycache__', '.idea'}
    for folder, dirs, files in os.walk(ROOT):
        base = Path(folder)
        dirs[:] = [d for d in dirs if d not in excluded and base / d != OUT]
        for name in files:
            p = base / name
            rel = p.relative_to(ROOT).as_posix()
            if p.is_symlink():
                skipped.append(rel)
                continue
            records.append({'path': rel, 'bytes': p.stat().st_size,
                            'sha256': digest(p), 'tracked': rel in tracked})
            if len(records) % 5000 == 0:
                print(f'Inventoried {len(records)} files', flush=True)
    paths = [r['path'] for r in records]
    ignored = subprocess.run(['git', 'check-ignore', '--stdin', '-z'], cwd=ROOT,
                             input='\0'.join(paths).encode(), capture_output=True)
    ignored_set = set(ignored.stdout.decode().split('\0'))
    for r in records:
        r['ignored'] = r['path'] in ignored_set
    (OUT / 'inventory.json').write_text(json.dumps({'excluded_directory_names': sorted(excluded),
        'skipped_links': skipped, 'records': records}, indent=2), encoding='utf-8')
    # Immutable rollback copy includes all authored source/native files, including pending work.
    with zipfile.ZipFile(OUT / 'source-before.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for r in records:
            if not r['path'].startswith(('generated/', '.codex-remote-attachments/')):
                z.write(ROOT / r['path'], r['path'])
    summary = {'files': len(records), 'bytes': sum(r['bytes'] for r in records),
               'source_archive_sha256': digest(OUT / 'source-before.zip')}
    (OUT / 'inventory-summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
