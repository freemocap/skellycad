"""Create R02 from R01, replacing only the baseplate. Run with pinned CAD Python."""
from pathlib import Path
import json,hashlib,shutil,zipfile,sys
import FreeCAD as App
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/'reconstruction/baseplate'))
import baseplate_features,baseplate_taper_features
OLD=ROOT/'generated/mouse-hats/print-test/r01'
OUT=OLD.parent/'r02';OUT.mkdir(parents=True,exist_ok=True)
TAPER=ROOT/'generated/mouse-hats/baseplate-taper'
unchanged=['carrier-and-holder-print-in-place.stl','clip.stl','cap.stl']
for name in unchanged:shutil.copy2(OLD/name,OUT/name)
shutil.copy2(TAPER/'baseplate.stl',OUT/'baseplate.stl')
plate=App.openDocument(str(TAPER/'tapered-baseplate.FCStd'))
review=App.openDocument(str(OLD/'print-in-place-review.FCStd'))
review.BaseplateReference.Shape=plate.TaperedBaseplate.Shape.copy()
review.Label='PRINT TEST R02 — tapered baseplate'
review.recompute();review.saveAs(str(OUT/'print-in-place-review.FCStd'))
notes=(OLD/'PRINT-NOTES.txt').read_text()
notes=notes.replace('Mouse-hats R01 print test','Mouse-hats R02 print test')
notes+='\nR02 changes only the baseplate exterior below its mounting-pocket floor.\nBottom footprint scaled to 0.57004 of width/depth, matching the supplied tapered\nmesh. Contact area 67.483 -> 21.928 mm2. Mounting interior and upper seat unchanged.\nThe other three STL files are byte-identical to R01. R01 remains preserved.\n'
(OUT/'PRINT-NOTES.txt').write_text(notes)
files=unchanged+['baseplate.stl']
hashes={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in files}
assert all(hashes[n]==hashlib.sha256((OLD/n).read_bytes()).hexdigest() for n in unchanged)
(OUT/'print-file-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
with zipfile.ZipFile(OUT/'mouse-hats-r02-print-test.zip','w',zipfile.ZIP_DEFLATED) as z:
    for n in files+['PRINT-NOTES.txt','print-file-hashes.json']:z.write(OUT/n,n)
    z.write(HERE/'settings.json','baseplate-taper-settings.json')
    z.write(HERE.parent/'print-test/settings.json','r01-settings.json')
    z.write(TAPER/'validation.json','baseplate-validation.json')
print(OUT/'mouse-hats-r02-print-test.zip')
