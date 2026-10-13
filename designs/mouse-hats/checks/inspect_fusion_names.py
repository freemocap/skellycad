"""Read printable name clues from Fusion archives, without interpreting geometry."""
from pathlib import Path
import json
import re
import subprocess
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())
out = WORKSPACE/'generated/mouse-hats/inspection/fusion-name-clues.json'
results = []
for generation in (50, 52):
    source = PROJECT/f'old/df-hardware/camera-assembly/cad/{generation}nassembly/{generation}nassembly.f3d'
    with zipfile.ZipFile(source) as archive:
        names = [n for n in archive.namelist() if 'SegmentType' in n and n.endswith('.dat')]
    matches = []
    for name in names:
        # Windows libarchive supports these archives' Zstandard compression.
        member_pattern = '*/' + name.split('/', 1)[1]
        data = subprocess.run(['tar', '-xOf', str(source), '--', member_pattern],
                              check=True, capture_output=True).stdout
        for encoding, text in [('ascii', data.decode('ascii', errors='replace')),
                               ('utf-16-le', data.decode('utf-16-le', errors='replace'))]:
            for match in re.finditer(r'[ -~]{0,60}(?:clip|cap|print.?in.?place)[ -~]{0,80}', text, re.I):
                matches.append(dict(member=name, encoding=encoding, text=match.group()))
    results.append(dict(source=source.relative_to(PROJECT).as_posix(), matches=matches))
out.write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results, indent=2))
