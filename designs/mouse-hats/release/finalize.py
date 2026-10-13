"""Validate print shells, inventory the release and create its sharing archive."""
from pathlib import Path
import hashlib,json,zipfile,subprocess,shutil
import trimesh
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'releases/mouse-hats-r02'
# Include the final release tooling, not an earlier snapshot of it.
for p in (ROOT/'designs/mouse-hats/release').iterdir():
    if p.is_file():shutil.copy2(p,OUT/'source/designs/mouse-hats/release'/p.name)
report={}
for name,count in [('carrier-and-holder-print-in-place.stl',2),('clip.stl',1),('cap.stl',1),('baseplate.stl',1)]:
    m=trimesh.load_mesh(OUT/'print'/name);shells=m.split()
    assert m.is_watertight and m.is_winding_consistent and len(shells)==count
    report[name]={'watertight':True,'consistent_winding':True,'shells':count}
(OUT/'validation/print-meshes.json').write_text(json.dumps(report,indent=2)+'\n')
meta={'revision':'R02','date':'2026-10-09','status':'print-test candidate; STEP exchange qualified by documented warnings',
 'units':'mm','parts':5,'schema':'AP242','git_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'source_state':'working-tree snapshot; not claimed to be a clean committed tree',
 'geometry_change_this_packaging_turn':False,'all_prior_work_preserved':True,
 'runtime':'FreeCAD 1.1.4 / Python 3.11 / OCCT 7.8','history_assets_included':False}
(OUT/'RELEASE.json').write_text(json.dumps(meta,indent=2)+'\n')
# Remove only disposable runtime/backup files created in this new release folder.
for p in list(OUT.rglob('*')):
    if p.is_file() and (p.suffix.lower() in ['.pyc','.fcstd1'] or '.fcstd.' in p.name.lower()):
        assert OUT.resolve() in p.resolve().parents;p.unlink()
for p in sorted(OUT.rglob('__pycache__'),key=lambda p:len(p.parts),reverse=True):
    if not any(p.iterdir()):p.rmdir()
files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='MANIFEST-SHA256.json')
manifest={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(OUT/'MANIFEST-SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=OUT.parent/'MouseHats_R02-release.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[OUT/'MANIFEST-SHA256.json']:z.write(p,Path('MouseHats_R02')/p.relative_to(OUT))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'archive':str(archive),'files':len(files)+1,'size_mb':round(archive.stat().st_size/1e6,2)},indent=2))
