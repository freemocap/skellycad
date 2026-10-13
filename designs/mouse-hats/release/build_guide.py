"""Four-page release guide, generated from actual assembly screenshots."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from PIL import Image,ImageChops
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'releases/mouse-hats-r02'
c=canvas.Canvas(str(OUT/'START-HERE.pdf'),pagesize=(612,792))
c.setTitle('MouseHats R02 - release and learning guide')
ink=HexColor('#17313c');muted=HexColor('#4e6570')
def text(x,y,s,size=11,color=ink):
 c.setFillColor(color);c.setFont('Helvetica',size);c.drawString(x,y,s)
def title(n,heading,sub):
 c.setFillColor(ink);c.rect(0,730,612,62,fill=1,stroke=0)
 text(36,759,heading,22,HexColor('#ffffff'));text(36,739,sub,10,HexColor('#d8e5e9'))
 text(36,24,'MOUSEHATS / R02 / 09 OCT 2026 / PRINT-TEST CANDIDATE',8,muted)
 text(562,24,str(n),9,muted)
def lines(y,rows,size=11):
 for s in rows:text(36,y,s,size);y-=17
 return y
def pic(name,x,y,w,h):
 im=Image.open(OUT/name).convert('RGB');box=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox()
 if box:im=im.crop(box)
 c.drawImage(ImageReader(im),x,y,w,h,preserveAspectRatio=True,anchor='c')
title(1,'A clear starting point','Five named parts. One assembled coordinate frame. Existing geometry preserved.')
pic('assembled.png',125,278,360,432)
lines(240,['Open MouseHats_R02.step for neutral CAD exchange (AP242, millimeters).',
 'Open MouseHats_R02.FCStd for the same clean, colored assembly in FreeCAD.',
 'Both are geometric snapshots. Editable feature documents live under source/.',
 'Use print/ for the four intended STL inputs and the printing notes.'])
lines(148,['What changed in R02?',
 'Only the baseplate lower exterior: tapered to a smaller contact footprint.',
 'R01 carrier, holder, clip and cap geometry is preserved. Earlier work remains',
 'in the playground; this folder is the clearly identified sharing checkpoint.'])
text(36,64,'Status: physical fit, strength and joint release still need a print test.',11)
c.showPage()
title(2,'Parts and relationships','Exploded reference only - offsets are for illustration, not assembly dimensions.')
pic('exploded.png',62,233,490,470)
lines(207,['MH-001  Baseplate (gold): receives the carrier stem; tapered exterior.',
 'MH-002  Carrier (cyan): PCB tray + stem + both arms + socket; one solid.',
 'MH-003  Camera holder (purple): sensor cradle, neck and ball; one solid.',
 'MH-004  Retaining clip (red): wraps the thickened holder walls.',
 'MH-005  PCB cap (green): retains/covers PCB and connector region.'],10)
lines(102,['Interfaces: stem/baseplate; ball/socket; holder/clip; tray/cap; PCB/retainers.',
 'Electronics, ribbon, screws, inserts and skull are omitted, not modeled as solids.',
 'Print carrier + holder together in the supplied pose; print accessories separately.'],10)
c.showPage()
title(3,'Controls and design intent','Edit a working copy of source/. Keep this published checkpoint unchanged.')
sections=[('Carrier / LongerPCBRetainers',[
 'Two arm-end retainers extend 1.5 mm along the board edge; lower stop 0.7 mm.',
 'Slot gap and PCB seating position stay fixed. The lower extension preserves cap fit.']),
 ('Holder / ThickerHolderWalls + ExtendedClip',[
 'Walls grow outward by 0.5 mm per side; inner sensor geometry stays fixed.',
 'Clip span grows 1.0 mm with intact retaining arms. These controls are coupled.']),
 ('Baseplate / TaperedBaseplate',[
 'BottomScale = 0.57004. Taper from Y = 1.5 mm to Y = -5 mm.',
 'Contact area: 67.483 to 21.928 mm2. Mount region at/above Y = 1.5 is preserved.']),
 ('Carrier / JunctionFillets + BlendedCarrier',[
 'Tray/arm roots R0.5, socket/arm junctions R0.3, stem/tray blend R3 mm.',
 'These changes address observed fragility; strength has not been load-tested.'])]
y=692
for heading,body in sections:
 text(36,y,heading,13);y-=24;y=lines(y,body,10)-27
lines(258,['How to explore',
 '1. Run source/Open-editable.FCMacro in FreeCAD 1.1.4 to load proxy modules',
 '   and the editable carrier, holder/clip, baseplate and cap documents.',
 '2. Change one named control in a working copy, recompute, inspect mating parts.',
 '3. Use the included rebuild_r02.py with FreeCAD Python to regenerate R02 edits',
 '   from the included parametric checkpoint. See source/README.md.',
 '4. Revalidate interfaces before creating the next revision.'],10)
lines(105,['Source provenance: reconstruction from supplied 58 STEP; two-arm paths and',
 'holder pose informed by V5 mesh; baseplate taper measured from tapered 53 mesh.',
 'The raw historical meshes/Fusion archives are not duplicated in this package.'],10)
c.showPage()
title(4,'Evidence and open questions','A release checkpoint is traceable; it is not a claim that every fit is validated.')
y=lines(690,['Verified in this package',
 'Five named, closed solids import from STEP; assembly labels and colors survive.',
 'Volume error < 0.0001 mm3; centroid/bounds error < 0.00001 mm against native CAD.',
 'The deeper STEP Boolean-readiness check still reports InvalidCurveOnSurface',
 'warnings on four parts. Basic solid validity passes. See step-roundtrip.json.',
 'Treat STEP as a qualified exchange candidate; native CAD is included as fallback.',
 'A second CAD application check has not been performed.'],11)
lines(y-30,['Existing design checks',
 'Carrier/holder have zero overlap and about 0.121 mm minimum modeled separation.',
 'A tiny clip/holder contact (~0.0045 mm3 at the recorded Boolean tolerance) remains.',
 'The new baseplate preserves the upper mount region and has no carrier overlap.',
 'These are geometric checks, not printer tolerances or a full motion analysis.'],11)
lines(359,['First print questions',
 '- Does the print-in-place ball release without breaking the neck or holder?',
 '- Do the clip, PCB and cap install securely without excessive force?',
 '- Does the ribbon route without binding through the desired camera motion?',
 '- Do support removal and handling leave the arm roots and stem intact?',
 '- Is the smaller baseplate footprint suitable for the intended mounting surface?'],11)
lines(197,['Not included in this revision',
 'Larger ball/neck/socket, additional weight-relief holes, and PCB/cap vent changes.',
 'No slicer profile, supports, printer job, measured fit or strength certification.'],11)
lines(102,['Collaboration: identify the part number, parameter, screenshot/view and revision',
 'when proposing a change. Explain the failure or intended benefit, and record',
 'which interfaces must remain fixed. See CHANGELOG.md and VALIDATION.md.'],10)
c.save()
print(OUT/'START-HERE.pdf')
