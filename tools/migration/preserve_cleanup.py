"""Preserve every inventoried generated file and recover the exact rat R01."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/migration/repo-cleanup-2026-10-31'


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    if (OUT/'archive-volumes.json').exists():
        raise SystemExit('This one-time cleanup step is already recorded; do not overwrite preservation evidence.')
    inv=json.loads((OUT/'inventory.json').read_text())['records']
    target=OUT/'generated-before.zip'
    assert not target.exists(), 'Retention archive already exists'
    records=[r for r in inv if r['path'].startswith('generated/')]
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
        for i,r in enumerate(records):
            path=ROOT/r['path']
            assert sha(path)==r['sha256'],r['path']
            archive.write(path,r['path'])
            if i%2000==0:print('Preserved generated files',i,'/',len(records),flush=True)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist())==len(records)
    evidence={'files':len(records),'uncompressed_bytes':sum(r['bytes'] for r in records),
        'archive':'generated-before.zip','archive_sha256':sha(target),'zip_integrity':True}
    (OUT/'generated-retention.json').write_text(json.dumps(evidence,indent=2))
    base=ROOT/'designs/eye-tracker/rat/checkpoints'
    selected=base/'ET-RAT-MONO-R01.FCStd'
    recovered=base/'ET-RAT-MONO-R01-local-edited-before-cleanup.FCStd'
    backup=base/'ET-RAT-MONO-R01.20261013-134340.FCBak'
    expected=json.loads((base.parent/'active-model.json').read_text())['native_sha256']
    assert sha(backup)==expected
    with zipfile.ZipFile(backup) as z:
        assert z.testzip() is None and 'Document.xml' in z.namelist()
    assert not recovered.exists()
    before=sha(selected)
    shutil.copy2(selected,recovered)
    assert sha(recovered)==before
    shutil.copy2(backup,selected)
    assert sha(selected)==expected
    repairs=[{'path':selected.relative_to(ROOT).as_posix(),'before_sha256':before,
        'after_sha256':expected,'preserved_previous':recovered.relative_to(ROOT).as_posix(),
        'source':backup.relative_to(ROOT).as_posix(),
        'reason':'Recover exact originally selected bytes; preserve later local edit separately.'}]
    (OUT/'repairs.json').write_text(json.dumps(repairs,indent=2))
    print(json.dumps(evidence),flush=True)
    print('Recovered exact selected R01; local edited document preserved.',flush=True)


if __name__=='__main__':main()
