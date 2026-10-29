"""Preserve the exact checked working review without promoting it to release."""
from pathlib import Path
import argparse, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[2]
DESIGN=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--name',required=True);a=ap.parse_args()
    assert Path(a.name).name==a.name and a.name not in ['.','..']
    out=DESIGN/'checkpoints'/a.name;assert not out.exists()
    manifest_path=DESIGN/'working-review.json';m=json.loads(manifest_path.read_text())
    for entry in m['files']:assert sha(ROOT/entry['path'])==entry['sha256'],entry['path']
    pcb=next((ROOT/e['path']).parent for e in m['files'] if e['path'].endswith('/head.kicad_pcb'))
    cad=next((ROOT/e['path']).parent for e in m['files'] if e['path'].endswith('.FCStd'))
    check=json.loads((pcb/'validation.json').read_text())
    for name,digest in check['sha256'].items():assert sha(pcb/name)==digest,name
    mechanical=json.loads((cad/'validation.json').read_text())
    assert mechanical['pcb_native_sha256']==check['sha256'],'Unmatched copper and native board revision'
    assert sha(Path(mechanical['native_document']))==mechanical['native_sha256']
    out.mkdir(parents=True)
    for sub,source in [('electronics',pcb),('mechanics',cad)]:
        dest=out/sub;dest.mkdir()
        for f in source.iterdir():
            if f.is_file() and not f.name.startswith('~') and (f.suffix in ['.kicad_pcb','.kicad_pro','.kicad_sch','.kicad_sym','.kicad_dru','.FCStd','.png','.json'] or f.name in ['source-netlist.xml','fp-lib-table','sym-lib-table','LICENSE-Antmicro','LICENSE-Espressif-library.md']):
                shutil.copy2(f,dest/f.name)
        for name in ['Camera.pretty','checks']:
            if (source/name).is_dir():shutil.copytree(source/name,dest/name)
    hashes={f.relative_to(out).as_posix():sha(f) for f in out.rglob('*') if f.is_file()}
    (out/'snapshot.json').write_text(json.dumps({'date':m['date'],'status':'Frozen working review; not fabrication ready','lineage':m.get('previous_snapshot'),'sha256':hashes},indent=2)+'\n')
    m['snapshot']=(out/'snapshot.json').relative_to(DESIGN).as_posix()
    manifest_path.write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps({'snapshot':m['snapshot'],'frozen_files':len(hashes),'native_and_cad_hashes_matched':True}))
if __name__=='__main__':main()
