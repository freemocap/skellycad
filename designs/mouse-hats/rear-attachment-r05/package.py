"""Validate and bundle the R05C print-in-place candidate."""
from pathlib import Path
import json,hashlib,zipfile
import trimesh
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/rear-attachment-r05'
files=['R05C-carrier-and-holder.stl','clip.stl','cap.stl','baseplate.stl']
report={}
for name in files:
 m=trimesh.load_mesh(OUT/name);count=2 if name.startswith('R05') else 1
 assert m.is_watertight and m.is_winding_consistent and len(m.split())==count
 report[name]={'watertight':True,'winding_consistent':True,'shells':count}
(OUT/'mesh-validation.json').write_text(json.dumps(report,indent=2)+'\n')
notes='''R05C: rear attachment rotated 30 degrees from R04B, toward the lower ribbon loop.
Units: mm. Top arm and ball/socket fit unchanged. Candidate for physical review.

R05C-carrier-and-holder.stl is one print-in-place unit containing TWO shells.
Keep the carrier and holder in their supplied relative positions. Accessories
are unchanged from R03. Comparison document offsets are display-only.

Compare ribbon routing and camera adjustment with the actual camera installed.
Ribbon clearance and protection are not simulated or guaranteed. Keep support
material out of the ball gap. No slicer profile or printer job is supplied.
Read DESIGN-NOTES.md for geometry, validation and known fit limits.
'''
(OUT/'PRINT-NOTES.txt').write_text(notes)
hashes={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in files}
for n in files[1:]:assert hashes[n]==hashlib.sha256((ROOT/'generated/mouse-hats/print-test/r03'/n).read_bytes()).hexdigest()
(OUT/'print-file-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
with zipfile.ZipFile(OUT/'mouse-hats-r05c-print-test.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in files+['PRINT-NOTES.txt','validation.json','validation-C.json','mesh-validation.json','edit-validation.json','print-file-hashes.json','comparison.png']:z.write(OUT/n,n)
 z.write(HERE/'README.md','DESIGN-NOTES.md');z.write(HERE/'settings.json','settings.json')
print(OUT/'mouse-hats-r05c-print-test.zip')
