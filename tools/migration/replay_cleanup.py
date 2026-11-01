"""Prepare and run original-layout design workflows in an isolated workspace."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from restore_cleanup import restore

ROOT=Path(__file__).resolve().parents[2]
RECORDS=ROOT/'docs/migration/repo-cleanup-2026-10-31'


def workspace(name):
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',name):raise ValueError('Use a simple workspace name')
    return ROOT/'generated/replay'/name


def source_owners():
    return json.loads((RECORDS/'current-source-owners.json').read_text())


def selected_owners(sources):
    sources=[s.replace('\\','/').rstrip('/') for s in sources]
    owners=source_owners()
    for source in sources:
        if source not in owners:raise ValueError('Unknown source owner: '+source)
    return [owner for owner in owners if not sources or any(owner==s or owner.startswith(s+'/') for s in sources)]


def overlay_current(dest,sources=()):
    owners=source_owners();selected=selected_owners(sources)
    mapped={r['new']:r['old'] for r in json.loads((RECORDS/'move-map.json').read_text())['files']}
    planned={}
    for owner in selected:
        base=ROOT/owner
        for p in base.rglob('*'):
            if not p.is_file() or any(x in p.parts for x in ['managed_components','__pycache__']):continue
            name=p.relative_to(ROOT).as_posix()
            actual_owner=next(o for o in owners if name.startswith(o+'/'))
            if actual_owner!=owner:continue
            if p.name=='README.md' and p.parent==base and name not in mapped:continue
            if not p.resolve().is_relative_to(base.resolve()):raise ValueError('Source escapes its owner')
            old=mapped.get(name,owners[owner]+name[len(owner):]);target=(dest/old).resolve()
            if not target.is_relative_to(dest.resolve()):raise ValueError('Overlay escapes the replay workspace')
            if old in planned:raise ValueError('Two source owners map to '+old)
            if name not in mapped and target.exists():raise ValueError('New source would overwrite a different historical file: '+old)
            planned[old]=(p,target,name)
    # Validate the whole plan before modifying this newly restored workspace.
    for p,target,name in planned.values():
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    return [name for p,target,name in planned.values()]


def prepare(name,current=False,sources=()):
    if sources and not current:raise ValueError("--source requires --current")
    scope=selected_owners(sources) if current else []
    dest=workspace(name); marker=dest/'replay-workspace.json'
    if marker.exists():
        data=json.loads(marker.read_text())
        if data.get('schema_version')!=2:raise ValueError('Workspace uses an older replay contract; prepare a new workspace')
        if data.get('source_owners',[])!=scope:raise ValueError('Use a new workspace name for a different source scope')
        if data['current_sources']!=current:raise ValueError('Use a new workspace name for a different source mode')
        print(f'Prepared workspace retained without resetting edits: {dest}',flush=True)
        return dest
    restored=dest/'replay-restored.json'
    if not restored.exists():
        count=restore(dest)
        restored.write_text(json.dumps({'restored_files':count,'hashes_verified':True}))
    # Recover the original selected R01 in the isolated copy as well.
    repair=json.loads((RECORDS/'repairs.json').read_text())[0]
    shutil.copy2(dest/repair['source'],dest/repair['path'])
    overlays=[]
    if current:overlays=overlay_current(dest,sources)
    record={'schema_version':2,'source_root':str(ROOT),'current_sources':current,
        'overlaid_sources':overlays,'source_owners':scope,'runtime_path_adaptation':True,'r01_exact_recovery':repair['after_sha256']}
    marker.write_text(json.dumps(record,indent=2))
    print(f'REPLAY_READY: {dest}',flush=True)
    return dest


def original_script(name):
    path=Path(name)
    if path.is_absolute():path=path.resolve().relative_to(ROOT)
    normalized=path.as_posix()
    for r in json.loads((RECORDS/'move-map.json').read_text())['files']:
        if normalized in [r['old'],r['new']]:return r['old']
    for owner,old in source_owners().items():
        if normalized.startswith(owner+'/'):return old+normalized[len(owner):]
    return normalized


def run(name,script,runtime,arguments=()):
    dest=workspace(name)
    if not (dest/'replay-workspace.json').exists():raise ValueError('Prepare the workspace first')
    target=(dest/original_script(script)).resolve()
    if not target.is_relative_to(dest) or not target.is_file():raise ValueError('Script is not in this replay workspace')
    env=os.environ.copy();env['CAD_PLAYGROUND_ROOT']=str(dest)
    env['SKELLY_REPLAY_ORIGINAL_ROOT']=json.loads((RECORDS/'inventory-summary.json').read_text())['original_root']
    env['FREECAD_USER_HOME']=str(dest/'generated/freecad-profile')
    env['MPLCONFIGDIR']=str(dest/'generated/matplotlib')
    wrapper=dest/'run-isolated.py'
    hook=(ROOT/'tools/migration/replay_runtime.py').read_text()
    wrapper.write_text(hook,encoding='utf-8')
    if runtime=='freecad':
        spec=json.loads((ROOT/'tools/cad/toolchain.json').read_text())
        python=ROOT/'.cad-tools'/Path(spec['freecad']['archive']).stem/'bin/python.exe'
    elif runtime=='kicad':
        candidates=list(Path('C:/Program Files/KiCad').glob('*/bin/python.exe')) + list((Path.home()/'AppData/Local/Programs/KiCad').glob('*/bin/python.exe'))
        if not candidates:raise FileNotFoundError('KiCad Python is not installed')
        python=sorted(candidates)[-1]
    else:
        python=ROOT/'tools/cad/.venv/Scripts/python.exe'
        if not python.exists():python=Path(sys.executable)
    command=[str(python),'-B',str(wrapper),str(ROOT),runtime,str(target),*arguments]
    result=subprocess.run(command,cwd=dest,env=env)
    return result.returncode


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('prepare');p.add_argument('--name',required=True);p.add_argument('--current',action='store_true');p.add_argument('--source',action='append',default=[])
    r=sub.add_parser('run');r.add_argument('--name',required=True);r.add_argument('--script',required=True)
    r.add_argument('--runtime',choices=['python','freecad','kicad'],default='python')
    args,extra=parser.parse_known_args()
    if args.action=='prepare':
        if extra:parser.error('Unrecognized preparation arguments: '+' '.join(extra))
        prepare(args.name,args.current,args.source)
    else:sys.exit(run(args.name,args.script,args.runtime,extra))
