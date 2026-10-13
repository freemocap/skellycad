"""Bundle only intended print inputs, settings and concise notes."""
from pathlib import Path
import zipfile,json,hashlib
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/print-test/r01'
files=['carrier-and-holder-print-in-place.stl','clip.stl','cap.stl','baseplate.stl']
notes='''Mouse-hats R01 print test — dimensions in mm

carrier-and-holder-print-in-place.stl contains TWO bodies in their assembled
relative positions. Keep their positions together. Do not fuse or independently
arrange them. Choose bed orientation/supports in Orca; no slicer setup is supplied.

clip.stl, cap.stl and baseplate.stl are separate parts to print and install later.
The clip shown gold in FreeCAD is an installed reference, excluded from the
print-in-place STL. Use this revised clip with the thickened holder.

Changes: two PCB tabs +1.5 mm along their edges, lower tab +0.7 mm; holder exterior
walls +0.5 mm each; clip span +1 mm. Sensor cavity and ball/neck sizes unchanged.
Carrier includes the accepted arm fillets and R3 stem blend.

This is a fit-test candidate. Modeled joint separation is about 0.121 mm at the
exported pose. Inspect support placement and joint gap in the slicer; release,
clip retention, ribbon fit and physical strength are not yet validated.
Full motion clearance and larger ball/neck redesign are still pending.
'''
(OUT/'PRINT-NOTES.txt').write_text(notes)
manifest={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in files}
(OUT/'print-file-hashes.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(OUT/'mouse-hats-r01-print-test.zip','w',zipfile.ZIP_DEFLATED) as bundle:
    for name in files+['PRINT-NOTES.txt','print-file-hashes.json']:
        bundle.write(OUT/name,name)
    bundle.write(HERE/'settings.json','settings.json')
print(OUT/'mouse-hats-r01-print-test.zip')
