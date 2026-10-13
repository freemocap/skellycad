"""Snapshot editable checkpoint sources and cached inputs; originals stay in place."""
from pathlib import Path
import shutil,json
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'releases/mouse-hats-r02'
def copy(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
for folder in ['model','reconstruction','print-test','baseplate-taper','release']:
    src=ROOT/'designs/mouse-hats'/folder
    for p in src.rglob('*'):
        if p.is_file() and p.suffix.lower() in ['.py','.json','.md'] and '__pycache__' not in p.parts:
            copy(p,OUT/'source'/p.relative_to(ROOT))
copy(ROOT/'tools/cad/toolchain.json',OUT/'source/tools/cad/toolchain.json')
for folder in ['arms','model','reconstruction','print-test/r01','print-test/r02','baseplate-taper']:
    for p in (ROOT/'generated/mouse-hats'/folder).rglob('*'):
        if p.is_file() and p.suffix.lower() in ['.fcstd','.json','.brep']:
            copy(p,OUT/'source'/p.relative_to(ROOT))
for name in ['carrier-and-holder-print-in-place.stl','clip.stl','cap.stl','baseplate.stl','PRINT-NOTES.txt']:
    copy(ROOT/'generated/mouse-hats/print-test/r02'/name,OUT/'print'/name)
for p in [ROOT/'generated/mouse-hats/print-test/r01/validation.json',ROOT/'generated/mouse-hats/print-test/r01/assembly-validation.json',ROOT/'generated/mouse-hats/baseplate-taper/validation.json']:
    copy(p,OUT/'validation'/(p.parent.name+'-'+p.name))
print('Checkpoint source snapshot and print files copied')
