"""Resolve retained pre-cleanup asset identifiers without filesystem aliases."""
from pathlib import Path
from functools import lru_cache
import json

ROOT = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=1)
def aliases():
    return json.loads((ROOT / 'docs/migration/repo-cleanup-2026-10-31/path-aliases.json').read_text())


def repository_path(value):
    path = Path(str(value).replace('\\', '/'))
    if path.is_absolute():
        path = path.resolve().relative_to(ROOT)
    name = path.as_posix()
    for old, new in aliases().items():
        if name == old or name.startswith(old + '/'):
            name = new + name[len(old):]
            break
    resolved = (ROOT / name).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError('Asset must stay within the repository')
    return resolved
