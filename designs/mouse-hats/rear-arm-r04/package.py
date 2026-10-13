"""Bundle independently printable A/B units, shared accessories and evidence."""
from pathlib import Path
import json,hashlib,zipfile
import trimesh
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/rear-arm-r04'
files=['R04A-carrier-and-holder.stl','R04B-carrier-and-holder.stl','clip.stl','cap.stl','baseplate.stl']
report={}
for name in files:
 m=trimesh.load_mesh(OUT/name);count=2 if name.startswith('R04') else 1
 assert m.is_watertight and m.is_winding_consistent and len(m.split())==count
 report[name]={'watertight':True,'winding_consistent':True,'shells':count}
(OUT/'mesh-validation.json').write_text(json.dumps(report,indent=2)+'\n')
notes='''R04 A/B rear-arm ribbon routing test. All dimensions mm.

A follows a smooth V5-guided sweep. B adds 1.25 mm more drop at the middle of
the loop. Top arm, holder, socket pose and R03 joint clearance stay fixed.

Each R04*-carrier-and-holder.stl is ONE print-in-place unit containing TWO shells.
Keep its carrier and holder together. Arrange A and B as separate complete objects
if printing both; they have the same assembly origin in their individual files.
clip.stl, cap.stl, baseplate.stl are unchanged shared R03 accessories.

Compare ribbon routing and camera adjustment with the actual camera installed.
Ribbon clearance/protection is not simulated or guaranteed. Use consistent print
settings between A/B. Keep support material out of the ball gap. No slicer profile
or print job is supplied. Read DESIGN-NOTES.md for geometry and known fit limits.
'''
(OUT/'PRINT-NOTES.txt').write_text(notes)
hashes={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in files}
for n in files[2:]:assert hashes[n]==hashlib.sha256((ROOT/'generated/mouse-hats/print-test/r03'/n).read_bytes()).hexdigest()
(OUT/'print-file-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
with zipfile.ZipFile(OUT/'mouse-hats-r04-rear-arm-options.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in files+['PRINT-NOTES.txt','validation.json','mesh-validation.json','edit-validation.json','print-file-hashes.json','comparison.png']:z.write(OUT/n,n)
 z.write(HERE/'README.md','DESIGN-NOTES.md');z.write(HERE/'settings.json','settings.json')
print(OUT/'mouse-hats-r04-rear-arm-options.zip')
