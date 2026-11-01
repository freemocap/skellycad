"""Remove only verified archive-backed intermediates and disposable bytecode."""
from pathlib import Path
import hashlib
import json
import os

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/migration/repo-cleanup-2026-10-31'


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def checked(name):
    p=(ROOT/name).resolve()
    if not p.is_relative_to(ROOT):raise ValueError(name)
    return p


def main():
    if (OUT/'removals.json').exists():
        raise SystemExit('This one-time cleanup step is already recorded; do not overwrite preservation evidence.')
    assert not (OUT/'removals.json').exists(), 'Removal audit already exists'
    removed=[];retained=[]
    # Verify the storage volumes before removing either redundant whole ZIP.
    for archive in json.loads((OUT/'archive-volumes.json').read_text()):
        combined=hashlib.sha256()
        for record in archive['volumes']:
            p=OUT/record['file'];assert sha(p)==record['sha256'],p
            with p.open('rb') as f:
                while block:=f.read(1024*1024):combined.update(block)
        assert combined.hexdigest()==archive['sha256']
        full=OUT/archive['archive']
        size=sum(v['bytes'] for v in archive['volumes'])
        if full.exists():
            assert sha(full)==archive['sha256']
            full.unlink()
        removed.append({'path':full.relative_to(ROOT).as_posix(),'bytes':size,'sha256':archive['sha256'],
            'replacement':[v['file'] for v in archive['volumes']],'reason':'Identical bounded-size archive volumes verified.'})
    for r in json.loads((OUT/'inventory.json').read_text())['records']:
        name=r['path']
        if not name.startswith('generated/'):continue
        p=checked(name)
        if not p.exists():
            removed.append({'path':name,'bytes':r['bytes'],'sha256':r['sha256'],
                'replacement':'generated-before.zip volumes:'+name,'reason':'Removed in preceding cleanup pass; exact inventoried member retained.'})
            continue
        if p.suffix.lower() in ['.fcstd','.fcbak','.fcstd1','.blend','.blend1'] or 'session-recovery' in p.parts or name.startswith(('generated/mouse-hats/','generated/cad-foundations/')):
            retained.append({'path':name,'reason':'Retain native review/recovery files and protected historical replay paths; desktop ownership is not inferred.'})
            continue
        if sha(p)!=r['sha256']:
            retained.append({'path':name,'reason':'Changed since starting inventory; preserve new work.'})
            continue
        try:p.unlink()
        except PermissionError:
            retained.append({'path':name,'reason':'Read-only or in-use original retained; exact archive member also exists.'})
            continue
        removed.append({'path':name,'bytes':r['bytes'],'sha256':r['sha256'],
            'replacement':'generated-before.zip volumes:'+name,'reason':'Exact archived intermediate; recover in isolated replay workspace.'})
        if len(removed)%3000==0:
            (OUT/'removals.partial.json').write_text(json.dumps(removed,indent=2))
            print('Removed verified intermediates',len(removed),flush=True)
    # Bytecode left old directory names visible after the source moves.
    for base in ['designs','tools']:
        for folder,dirs,files in os.walk(ROOT/base):
            dirs[:]=[d for d in dirs if d not in ['.venv','managed_components','checkpoints','.git']]
            p=Path(folder)
            if p.name!='__pycache__':continue
            for name in files:
                f=checked((p/name).relative_to(ROOT))
                if f.suffix not in ['.pyc','.pyo']:continue
                removed.append({'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,
                    'sha256':sha(f),'reason':'Disposable Python bytecode; source remains retained.'})
                f.unlink()
    for base in ['designs','tools','generated']:
        for folder,dirs,files in os.walk(ROOT/base,topdown=False):
            p=Path(folder)
            if any(x in p.parts for x in ['.venv','managed_components','checkpoints','replay','mouse-hats','cad-foundations','kicad-foundations']):continue
            if p!=ROOT/base and not list(p.iterdir()):
                assert p.resolve().is_relative_to(ROOT)
                p.rmdir()
    (OUT/'removals.json').write_text(json.dumps(removed,indent=2))
    (OUT/'retained-local-files.json').write_text(json.dumps(retained,indent=2))
    print('Removed',len(removed),'files,',sum(r['bytes'] for r in removed),'bytes; retained',len(retained),'local native/recovery or changed files',flush=True)


if __name__=='__main__':main()
