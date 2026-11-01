"""Verify cleanup preservation, selectors, packages and maintained navigation.

Run with Python 3.11+. The default checks every preserved archive member as well
as the current checkout. --quick omits the expensive archive-byte pass.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from urllib.parse import unquote
from archive_io import open_archive

ROOT=Path(__file__).resolve().parents[2]
RECORDS=ROOT/'docs/migration/repo-cleanup-2026-10-31'
sys.path.insert(0,str(ROOT/'designs/eye-tracker'))
from shared.model import load_manifest
from shared.paths import repository_path


def read(name):return json.loads((RECORDS/name).read_text(encoding='utf-8'))
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def navigation():
    files=[*ROOT.glob('*.md'),*ROOT.glob('docs/*.md'),ROOT/'docs/migration/README.md',
           RECORDS/'README.md',RECORDS/'verification.md',*ROOT.glob('designs/**/README.md')]
    checked=0
    for p in files:
        if any(x in p.parts for x in ['checkpoints','references','managed_components','mouse-hats','cad-foundations','kicad-foundations']):continue
        # Historical narrative files retain their original-layout context. New
        # indexes remain checked; old history READMEs are not current procedures.
        if 'history' in p.parts and not p.read_text(encoding='utf-8',errors='replace').startswith(('# History index','# Historical investigations')):continue
        text=p.read_text(encoding='utf-8')
        for m in re.finditer(r'\]\(([^)]+)\)',text):
            target=m[1].split('#')[0].strip('<>')
            if not target or re.match(r'^[a-z]+:',target,re.I):continue
            q=(p.parent/unquote(target)).resolve()
            assert q.exists(),f'Broken link: {p.relative_to(ROOT)} -> {target}'
            checked+=1
    return checked


def main(quick=False):
    inventory=read('inventory.json')['records']
    source={r['path']:r for r in inventory if not r['path'].startswith('generated/')}
    generated={r['path']:r for r in inventory if r['path'].startswith('generated/')}
    changes={r['old']:r for r in read('source-changes.json')}
    moves={r['old']:r['new'] for r in read('move-map.json')['files']}
    result={'passed':False,'archive_bytes_checked':not quick,'original_files':len(inventory),
            'source_files':len(source),'generated_inputs':len(generated),'source_edits':len(changes)}
    for old,record in source.items():
        target=ROOT/moves.get(old,old)
        assert target.is_file(),f'Missing retained source: {old} -> {target}'
        expected=changes.get(old,{}).get('after_sha256',record['sha256'])
        assert sha(target)==expected,f'Changed retained source: {target}'
        if old in changes:assert changes[old]['before_sha256']==record['sha256']
        if old.startswith(('designs/mouse-hats/','designs/cad-foundations/','designs/kicad-foundations/')):
            assert target==ROOT/old and sha(target)==record['sha256']
    print('Current source files and protected historical paths verified',flush=True)
    for repair in read('repairs.json'):
        assert sha(repository_path(repair['path']))==repair['after_sha256']
        assert sha(ROOT/repair['retained_previous'])==repair['before_sha256']
    import zipfile
    catalog=read('checkpoint-catalog.json')
    for row in catalog:
        manifest,path=load_manifest(ROOT/row['manifest'])
        assert path.resolve()==(ROOT/row['checkpoint']).resolve(),row['manifest']
        assert sha(path)==row['sha256']
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None and 'Document.xml' in archive.namelist()
    result['checkpoint_records']=len(catalog)
    result['unique_checkpoints']=len({r['checkpoint'] for r in catalog})
    packages=read('retained-packages.json')
    for row in packages:assert sha(ROOT/row['retained'])==row['sha256'],row['retained']
    result['matched_package_files']=len(packages)
    archived=0
    for record in read('archive-volumes.json'):
        expected=({name:source[name] for name in record['members']} if 'members' in record else generated if record['archive'].startswith('generated') else {k:v for k,v in source.items() if not k.startswith('.codex-remote-attachments/')})
        if not quick:
            combined=hashlib.sha256()
            for volume in record['volumes']:
                p=RECORDS/volume['file'];assert p.stat().st_size==volume['bytes']
                digest=hashlib.sha256()
                with p.open('rb') as stream:
                    while block:=stream.read(8*1024*1024):digest.update(block);combined.update(block)
                assert digest.hexdigest()==volume['sha256'],str(p)
            assert combined.hexdigest()==record['sha256']
        with open_archive(RECORDS/record['archive']) as archive:
            members=set(archive.namelist())
            assert set(expected)<=members, sorted(set(expected)-members)
            for name,row in expected.items():
                assert archive.getinfo(name).file_size==row['bytes'],name
                if not quick:
                    with archive.open(name) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==row['sha256'],name
                archived+=1
                if not quick and archived%5000==0:print('Preserved archive members verified:',archived,flush=True)
    result['archived_original_files']=archived
    removals=read('removals.json')
    removed={r['path']:r for r in removals}
    retained={r['path']:r for r in read('retained-local-files.json')}
    for name,row in generated.items():
        assert name in removed or name in retained,name
        if name in removed:assert removed[name]['sha256']==row['sha256'],name
    result['audited_removals']=len(removals)
    result['retained_local_files']=len(retained)
    result['navigation_links']=navigation()
    result['passed']=True
    target=RECORDS/('verification-quick.json' if quick else 'verification.json')
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--quick',action='store_true')
    main(parser.parse_args().quick)
