"""Apply the approved file map with containment, collision and hash checks."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import zipfile
from plan_cleanup import relocate

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/migration/repo-cleanup-2026-10-31'


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def contained(name):
    p=(ROOT/name).resolve()
    assert p.is_relative_to(ROOT),name
    return p


def main():
    data=json.loads((OUT/'move-map.json').read_text());moves=data['prefixes']
    nav=json.loads((OUT/'navigation.json').read_text())
    repaired=json.loads((OUT/'repairs.json').read_text())[0]
    done=[]; overrides={}
    with zipfile.ZipFile(OUT/'source-before.zip') as archive:
        # Preserve overwritten landing pages as explicit history, with original bytes.
        for r in data['files']:
            if r['new'] in nav and r['old'].endswith('/README.md'):
                if r['new'] in ['designs/README.md','designs/eye-tracker/README.md']:
                    dest=OUT/'original-navigation'/r['old']
                else:
                    dest=contained(str(Path(r['new']).parent/'history/overview-before-cleanup.md'))
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(archive.read(r['old']))
                assert sha(dest)==r['sha256']
                overrides[r['old']]=dest.relative_to(ROOT).as_posix()
    for r in data['files']:
        old,new=r['old'],r['new']
        if old==new:continue
        source=contained(old);target=contained(new)
        expected=repaired['after_sha256'] if old==repaired['path'] else r['sha256']
        if old in overrides:
            # Destination README is the new navigation page; original is retained above.
            assert sha(contained(overrides[old]))==r['sha256']
            if source.exists():
                assert sha(source)==r['sha256'],old
                source.unlink()
            done.append({'old':old,'new':new,'preserved_original':overrides[old]})
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        if source.exists():
            assert sha(source)==expected,old
            assert not target.exists(),f'Collision: {target}'
            source.rename(target)
        assert target.exists() and sha(target)==expected,new
        done.append({'old':old,'new':new,'sha256':expected})
        if len(done)%1000==0:print('Moved and verified',len(done),'files',flush=True)
    # The extra preserved local edit was created after the starting inventory.
    p=contained(repaired['preserved_previous']);q=contained(relocate(repaired['preserved_previous'],moves))
    if p.exists():
        assert sha(p)==repaired['before_sha256'];q.parent.mkdir(parents=True,exist_ok=True)
        assert not q.exists();p.rename(q)
    repaired['retained_previous']=q.relative_to(ROOT).as_posix()
    (OUT/'repairs.json').write_text(json.dumps([repaired],indent=2))
    (OUT/'moves-completed.json').write_text(json.dumps(done,indent=2))
    (OUT/'original-navigation.json').write_text(json.dumps(overrides,indent=2))
    catalog=json.loads((OUT/'checkpoint-catalog.json').read_text())
    aliases=dict(moves)
    aliases.update({r['original_checkpoint']:r['checkpoint'] for r in catalog})
    aliases=dict(sorted(aliases.items(),key=lambda kv:len(kv[0]),reverse=True))
    (OUT/'path-aliases.json').write_text(json.dumps(aliases,indent=2))
    # New manifests refer to the retained native files; frozen historical records remain untouched.
    def remap(value):
        if isinstance(value,dict):return {k:remap(v) for k,v in value.items()}
        if isinstance(value,list):return [remap(v) for v in value]
        if isinstance(value,str):return relocate(value.replace('\\','/'),aliases)
        return value
    with zipfile.ZipFile(OUT/'source-before.zip') as archive:
        for animal in ['mouse','rat']:
            old=f'designs/eye-tracker/{animal}/active-model.json'
            new=f'designs/eye-tracker/{animal}/variants/monocular/active-model.json'
            contained(new).write_text(json.dumps(remap(json.loads(archive.read(old))),indent=2))
            contained(old).write_text(json.dumps({'schema_version':1,'selection':new},indent=2))
        for variant,old in [('binocular','lowered-cameras-r43'),('eye-world','eye-world-print-r06')]:
            p=f'designs/eye-tracker/rat/{old}/review.json'
            obj=remap(json.loads(archive.read(p)))
            obj['selection_status']='review-candidate; not a selected complete assembly'
            contained(f'designs/eye-tracker/rat/variants/{variant}/review-model.json').write_text(json.dumps(obj,indent=2))
        old='designs/eye-tracker/shared/cameras/pupil-core-eye/active-model.json'
        contained('designs/cameras/pupil-core-eye/active-model.json').write_text(json.dumps(remap(json.loads(archive.read(old))),indent=2))
    # Resolve Markdown links according to their ORIGINAL location, then their mapped destination.
    changed_links=[]
    pattern=re.compile(r'(!?\[[^\]\n]*\]\()([^\s)]+)(\))')
    for r in data['files']:
        old,new=r['old'],r['new']
        if old==new or not old.endswith('.md') or '/checkpoints/' in old or '/managed_components/' in old or new in nav:
            continue
        p=contained(new)
        if not p.exists():continue
        try:
            text=p.read_text(encoding='utf-8-sig')
        except UnicodeDecodeError:
            text=p.read_text(encoding='cp1252')
        def link(m):
            url=m[2]
            if ':' in url or url.startswith('#'):return m[0]
            file,sep,fragment=url.partition('#')
            original=(ROOT/Path(old).parent/file).resolve()
            if not original.is_relative_to(ROOT):return m[0]
            rel=original.relative_to(ROOT).as_posix();mapped=relocate(rel,aliases)
            if not contained(mapped).exists():return m[0]
            target=os.path.relpath(contained(mapped),p.parent).replace('\\','/')
            return m[1]+target+(sep+fragment if sep else '')+m[3]
        updated=pattern.sub(link,text)
        if updated!=text:
            p.write_text(updated,encoding='utf-8');changed_links.append(new)
    (OUT/'markdown-link-updates.json').write_text(json.dumps(changed_links,indent=2))
    # Add short indexes only; do not rewrite individual historical narratives.
    for parent in sorted((ROOT/'designs').rglob('*')):
        if not parent.is_dir() or parent.name not in ['history','print-layouts'] or '/checkpoints/' in parent.as_posix():continue
        if any(x in parent.parts for x in ['mouse-hats','cad-foundations','managed_components']):continue
        rows=[]
        for child in sorted(parent.iterdir()):
            if child.is_dir():
                target=child.name+('/README.md' if (child/'README.md').exists() else '/')
                rows.append(f'- [{child.name}]({target})')
        index=parent/'README.md'
        if not index.exists():index.write_text('# History index\n\nEarlier studies retain their own status and limitations. Revision numbers do not select an assembly.\n\n'+'\n'.join(rows)+'\n',encoding='utf-8')
    # Empty directories only; caches are removed later under the deletion audit.
    for folder,dirs,files in os.walk(ROOT/'designs',topdown=False):
        p=Path(folder)
        if not list(p.iterdir()):
            if any(x in p.parts for x in ['mouse-hats','cad-foundations','kicad-foundations']):continue
            p.rmdir()
    print('Migration complete:',len(done),'file moves;',len(changed_links),'Markdown link updates',flush=True)


if __name__=='__main__':main()
