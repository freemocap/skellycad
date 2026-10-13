"""Validate separate labeled print units and package their STL files."""
from pathlib import Path
import json,hashlib,zipfile
import trimesh
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/rear-arm-r11/labeled'
report={};files=[]
for key in 'ABCDE':
 name='R11'+key+'-labeled-carrier-and-holder.stl';files.append(name)
 m=trimesh.load_mesh(OUT/name);parts=m.split()
 assert m.is_watertight and m.is_winding_consistent and len(parts)==2,name
 report[key]={'filename':name,'shells':2,'watertight':True,'consistent_winding':True,'sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest()}
(OUT/'mesh-validation.json').write_text(json.dumps(report,indent=2)+'\n')
notes='''R11 A-E labeled print-in-place candidates. Units: millimeters.
Each tray has its matching letter embossed on the EXTERIOR BACK, 3.5mm high,
0.4mm raised. PCB seating geometry and ball/socket fit are unchanged.

Import the five STL files as FIVE SEPARATE OBJECTS in Snapmaker Orca, then arrange
those objects on one plate. If offered to merge them as one multipart object,
decline. Every STL contains a carrier and holder already in their required
print-in-place relative position: keep those two shells together when moving or
rotating the object. Files intentionally share the original assembly origin, so
use the slicer's arrange command to separate objects before printing.

Use your established orientation and support settings. Keep supports out of the
ball gap; inspect the new lettering in slice preview. This package does not
contain a printer profile, supports, G-code, or a prescribed print orientation.
Shared clip/cap/baseplate have not changed and are not duplicated in this bundle.

A: approx7:50 attachment, balanced return,2.5mm straight departure.
B: approx7:30 attachment, balanced return,2.5mm straight departure.
C: approx7:40 attachment, intermediate angle,2.5mm straight departure.
D: approx7:30 attachment, broader early bend,1.5mm straight departure.
E: approx7:30 attachment, longer departure3.5mm, more level return.
Letters refer to the same A-E options as the FreeCAD comparison.
'''
(OUT/'PRINT-ME.txt').write_text(notes)
with zipfile.ZipFile(OUT/'R11-A-E-labeled-STLs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in files+['PRINT-ME.txt','label-validation.json','mesh-validation.json']:z.write(OUT/name,name)
print(OUT/'R11-A-E-labeled-STLs.zip')
