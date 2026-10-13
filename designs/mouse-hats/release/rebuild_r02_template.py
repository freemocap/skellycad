"""Rebuild R02 edits from the included parametric checkpoint, with pinned FreeCAD Python."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
steps=['print-test/build.py','print-test/assemble.py','print-test/package.py','baseplate-taper/build.py','baseplate-taper/package_r02.py']
for step in steps:
    subprocess.run([sys.executable,str(ROOT/'designs/mouse-hats'/step)],cwd=ROOT,check=True)
print('R02 rebuilt under source/generated/mouse-hats/print-test/r02. Published release unchanged.')

