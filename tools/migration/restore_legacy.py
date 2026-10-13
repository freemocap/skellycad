"""Restore archived historical outputs without overwriting newer generated files."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', default='generated/', help='Archive path prefix, restricted to generated/')
    args = parser.parse_args()
    if not args.prefix.startswith('generated/') or '..' in Path(args.prefix).parts:
        parser.error('The prefix must be within generated/.')
    inventory = json.loads((ROOT / 'docs/migration/inventory.json').read_text())
    restored = skipped = 0
    with zipfile.ZipFile(ROOT / 'docs/migration/playground-artifacts.zip') as archive:
        for record in inventory['records']:
            member = record.get('member', '')
            if not member.startswith(args.prefix):
                continue
            target = (ROOT / member).resolve()
            if not target.is_relative_to(ROOT / 'generated'):
                raise ValueError(f'Invalid archive destination: {member}')
            if target.exists():
                skipped += 1
                continue
            data = archive.read(member)
            if hashlib.sha256(data).hexdigest() != record['sha256']:
                raise ValueError(f'Archive checksum mismatch: {member}')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            restored += 1
    print(f'Restored {restored} historical files; preserved {skipped} existing files.')


if __name__ == '__main__':
    main()
