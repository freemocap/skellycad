"""Write a collision-checked file move map; perform no moves."""
from pathlib import Path, PurePosixPath
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/migration/repo-cleanup-2026-10-31'


def numbered(name):
    match = re.search(r'-r(\d+)(-l(\d+))?$', name)
    if not match:
        return name
    return f'r{int(match[1]):03d}' + (f'-l{int(match[3]):03d}' if match[3] else '') + '-' + name[:match.start()]


def mapping():
    moves = {}
    def add(old, new):
        assert (ROOT / old).exists(), old
        moves[old] = new
    for animal in ['mouse', 'rat']:
        base = f'designs/eye-tracker/{animal}'
        anatomy = {'adult-anatomy-r07','anatomy-study-r10','clean-reference-r11',
            'skull-registration-r12','surface-landmarks-r13','registered-eyes-r14',
            'symmetry-review-r15','symmetric-design-r16','adult-anatomy-r11',
            'landmark-eye-placement-r14','landmark-eyes-r04','landmark-review-r02',
            'named-landmarks-r03','registered-eyes-study-r01','skull-landmarks-study-r01'}
        current = {'raised-target-r19':'monocular'} if animal == 'mouse' else {
            'lowered-cameras-r43':'binocular', 'eye-world-print-r06':'eye-world'}
        for child in (ROOT / base).iterdir():
            n = child.name
            if n in ['README.md','active-model.json','references','__pycache__']:
                continue
            if n in current:
                target = f'{base}/variants/{current[n]}/src'
            elif child.is_dir() and n in anatomy:
                target = f'{base}/anatomy/history/{numbered(n)}'
            elif n.startswith('skull-print-'):
                target = f'{base}/anatomy/print-layouts/{numbered(n)}'
            elif n.startswith('eye-world-'):
                target = f'{base}/variants/eye-world/history/{numbered(n)}'
            elif n == 'binocular-study-r01':
                target = f'{base}/variants/binocular/history/concepts/r001-binocular-study'
            elif n.startswith('print-'):
                match = re.search(r'-r(\d+)', n)
                variant = 'binocular' if animal == 'rat' and match and int(match[1]) >= 31 else 'monocular'
                target = f'{base}/variants/{variant}/history/print-layouts/{numbered(n)}'
            elif child.is_dir() and re.search(r'-r\d+$', n):
                rev = int(re.search(r'-r(\d+)$', n)[1])
                variant = 'binocular' if animal == 'rat' and rev >= 31 else 'monocular'
                target = f'{base}/variants/{variant}/history/{numbered(n)}'
            elif n == 'checkpoints':
                target = f'{base}/variants/monocular/checkpoints/r001-baseline'
            elif n == 'inputs':
                target = f'{base}/references/rebuild-inputs'
            else:
                target = f'{base}/variants/monocular/history/r001-baseline/{n}'
            add(f'{base}/{n}', target)
        # Nested selected checkpoint is canonical, not a mutable source file.
        if animal == 'mouse':
            add(base+'/raised-target-r19/checkpoints', base+'/variants/monocular/checkpoints/r019-raised-target')
    base = 'designs/eye-tracker/marmoset'
    for child in (ROOT / base).glob('skull-print-*'):
        add(f'{base}/{child.name}', f'{base}/anatomy/print-layouts/{numbered(child.name)}')
    for camera in ['pupil-core-eye','pupil-core-eye-inherited']:
        old = f'designs/eye-tracker/shared/cameras/{camera}'
        new = f'designs/cameras/{camera}'
        add(old, new)
        for child in (ROOT / old).iterdir():
            if child.is_dir() and re.search(r'-r\d+$', child.name):
                add(f'{old}/{child.name}', f'{new}/history/{numbered(child.name)}')
    shared = 'designs/eye-tracker/shared'
    for child in (ROOT / shared).iterdir():
        if child.is_dir() and re.search(r'-r\d+$',child.name):
            add(f'{shared}/{child.name}', f'{shared}/history/{numbered(child.name)}')
    old='designs/eye-camera-ov9281'; new='designs/cameras/ov9281'
    add(old,new)
    for child in (ROOT/old/'electronics').iterdir():
        if child.name == 'three-board-e01':
            target=f'{new}/variants/three-board/src'
        elif child.name == 'r11':
            target=f'{new}/variants/slim-flex/src/electronics'
        else:
            target=f'{new}/history/electronics/r{int(child.name[1:]):03d}'
        add(f'{old}/electronics/{child.name}',target)
    add(old+'/firmware',new+'/variants/slim-flex/src/firmware')
    add(old+'/reference',new+'/references')
    for name in ['architecture','audits','mechanics','packaging','verification']:
        add(f'{old}/{name}',f'{new}/history/{name}')
    for child in (ROOT/old/'checkpoints').iterdir():
        # A snapshot is immutable: retain every path inside the package.
        add(f'{old}/checkpoints/{child.name}', f'{new}/variants/slim-flex/checkpoints/{child.name}')
    add('designs/eye-camera-og0tc','designs/cameras/og0tc')
    for name in ['electronics','mechanical','integration']:
        add(f'designs/eye-camera-og0tc/{name}',f'designs/cameras/og0tc/history/{name}')
    for child in (ROOT/'designs/enclosure').iterdir():
        if child.is_dir():
            add('designs/enclosure/'+child.name,'designs/enclosure/history/'+numbered(child.name))
    return dict(sorted(moves.items(),key=lambda x:len(x[0]),reverse=True))


def relocate(path, moves):
    for old,new in moves.items():
        if path == old or path.startswith(old+'/'):
            return new+path[len(old):]
    return path


def main():
    moves=mapping()
    inventory=json.loads((OUT/'inventory.json').read_text())['records']
    records=[]; targets=set()
    for item in inventory:
        old=item['path']; new=relocate(old,moves)
        assert new not in targets, new
        targets.add(new)
        if old.startswith('generated/'):
            action='retain-replay-input-or-output-until-archive-verified'
        elif old!=new:
            action='move-preserving-bytes'
        else:
            action='keep'
        records.append({'old':old,'new':new,'sha256':item['sha256'],'action':action})
    (OUT/'move-map.json').write_text(json.dumps({'prefixes':moves,'files':records},indent=2))
    print('Mapped',len(records),'files;',sum(r['old']!=r['new'] for r in records),'moves;',len(moves),'subtrees')


if __name__=='__main__':
    main()
