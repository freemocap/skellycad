"""Export R03 as a two-shell print-in-place unit; preserve accessory print files."""
from pathlib import Path
import json,sys,shutil,hashlib,zipfile
import FreeCAD as App
import Part,MeshPart
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'print-test']:sys.path.insert(0,str(p))
import socket_revision_features,attachment_arm_features,arm_finish_features,stem_blend_features,retention_features
OUT=ROOT/'generated/mouse-hats/print-test/r03'
OLD=OUT.parent/'r02'
carrier=App.openDocument(str(OUT/'carrier.FCStd'))
assembly=App.openDocument(str(OLD/'print-in-place-review.FCStd'))
assembly.Carrier.Shape=carrier.StrongerClearanceCarrier.Shape.copy()
assembly.Label='PRINT TEST R03 - reinforced socket joints / larger ball clearance'
assembly.recompute();assembly.saveAs(str(OUT/'print-in-place-review.FCStd'))
mesh=MeshPart.meshFromShape(Shape=Part.makeCompound([assembly.Carrier.Shape,assembly.Holder.Shape]),
                          LinearDeflection=.03,AngularDeflection=.15,Relative=False)
assert mesh.isSolid();mesh.write(str(OUT/'carrier-and-holder-print-in-place.stl'))
for name in ['clip.stl','cap.stl','baseplate.stl']:shutil.copy2(OLD/name,OUT/name)
notes='''MouseHats R03 print test - units mm

Changes from R02 after the first physical print: arm/socket attachment sections
increase from 2.4 x 1.8 to 3.0 x 2.2 mm. Collar radius 2.701637 -> 3.1 mm.
Junctions retain R0.3 blends; collar/bowl transition receives R0.2 concave blend.
Ball cavity is cleared by a 2.35 mm sphere about the unchanged 2.0 mm ball center.
Actual minimum holder/carrier distance at the print pose: 0.331722 mm (was 0.121146).
Neck and holder are unchanged. Neck opening and insert bore are preserved.

carrier-and-holder-print-in-place.stl contains TWO distinct shells positioned for
printing together. Do not independently arrange or fuse them. Choose orientation
and supports in the slicer. Keep support material out of the intended joint gap.
clip.stl, cap.stl and baseplate.stl are unchanged R02 accessories, printed separately.

This is a fit-test candidate, not a guaranteed printer clearance. Material/nozzle/
layer-height feedback was requested but not available when this export was made.
R02 looked good physically but the ball fused and the neck broke during release.
R03 aims to address adhesion and weak arm/collar links; a new print is needed.
No larger ball or stronger neck has been introduced in this revision.

Validation.json records an unchanged tiny cap/carrier contact (~0.001612 mm3 with
isolated exact Boolean checks), as well as zero holder and baseplate interference.
Full motion, retention and strength remain unvalidated.
'''
(OUT/'PRINT-NOTES.txt').write_text(notes)
files=['carrier-and-holder-print-in-place.stl','clip.stl','cap.stl','baseplate.stl']
hashes={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in files}
for n in files[1:]:assert hashes[n]==hashlib.sha256((OLD/n).read_bytes()).hexdigest()
(OUT/'print-file-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
with zipfile.ZipFile(OUT/'mouse-hats-r03-print-test.zip','w',zipfile.ZIP_DEFLATED) as z:
    for n in files+['PRINT-NOTES.txt','print-file-hashes.json','validation.json']:z.write(OUT/n,n)
    z.write(HERE/'settings.json','settings.json')
    z.write(HERE/'README.md','DESIGN-NOTES.md')
    if (OUT/'mesh-validation.json').is_file():z.write(OUT/'mesh-validation.json','mesh-validation.json')
print(OUT/'mouse-hats-r03-print-test.zip')

