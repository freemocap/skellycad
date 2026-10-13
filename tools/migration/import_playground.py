"""One-time, non-destructive import; refuse an existing migration inventory."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'old-cad-playground'
OUT = ROOT / 'docs/migration'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inventory = OUT / 'inventory.json'
    if inventory.exists():
        raise SystemExit('Inventory exists; use verify.py instead of importing again.')
    records = []
    omitted = Counter()
    archive_path = OUT / 'playground-artifacts.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for top in SOURCE.iterdir():
            if top.name in {'.cad-tools', '.codex'}:
                omitted[top.name + ': machine-local runtime/configuration'] += 1
                continue
            files = sorted(top.rglob('*')) if top.is_dir() else [top]
            for source in files:
                if not source.is_file():
                    continue
                rel = source.relative_to(SOURCE)
                if any(p in {'.venv', '__pycache__', 'uv-cache'} for p in rel.parts):
                    omitted['rebuildable Python environments/cache'] += 1
                    continue
                if source.suffix.lower() in {'.pyc', '.log', '.lock'} or 'review-session' in rel.parts:
                    # uv.lock is a durable dependency lock, not a process lock.
                    if source.name != 'uv.lock':
                        omitted['session state/logs/bytecode'] += 1
                        continue
                sha = digest(source)
                record = {'source': rel.as_posix(), 'sha256': sha, 'bytes': source.stat().st_size}
                if rel.parts[:2] == ('releases', 'MouseHats_R02-release'):
                    target = Path('releases/mouse-hats-r02').joinpath(*rel.parts[3:])
                    if digest(SOURCE / target) != sha:
                        raise RuntimeError(f'Release duplicate differs: {rel}')
                    if source.suffix.lower() == '.fcbak':
                        record.update(archive='docs/migration/playground-artifacts.zip', member=target.as_posix(), disposition='identical-archived-release-copy')
                    else:
                        record.update(destination=target.as_posix(), disposition='identical-release-copy')
                elif rel.parts[0] == 'generated' or source.suffix.lower() == '.fcbak' or len(rel.parts) == 1:
                    archive.write(source, rel.as_posix())
                    record.update(archive='docs/migration/playground-artifacts.zip', member=rel.as_posix(), disposition='archived')
                else:
                    target = rel
                    if rel.parts[0] == '.codex-remote-attachments':
                        target = Path('designs/mouse-hats/references/photos') / (sha[:16] + source.suffix.lower())
                    dest = ROOT / target
                    if dest.exists() and digest(dest) != sha:
                        raise RuntimeError(f'Refusing to overwrite {target}')
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                    record.update(destination=target.as_posix(), disposition='copied')
                records.append(record)
    inventory.write_text(json.dumps({'source': 'old-cad-playground', 'omitted': dict(omitted),
        'archive_sha256': digest(archive_path), 'records': records}, indent=2) + '\n')
    print(json.dumps({'retained_records': len(records), 'omitted': dict(omitted),
                     'archive_MiB': round(archive_path.stat().st_size / 1024**2, 2)}, indent=2))


if __name__ == '__main__':
    main()
