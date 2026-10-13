# Editable checkpoint

This folder is a self-contained R02 checkpoint working tree, without CAD binaries
or raw inherited archives. Use FreeCAD 1.1.4 with Python 3.11; the exact runtime
archive and hash are recorded in tools/cad/toolchain.json.

## View and edit

Run Open-editable.FCMacro from FreeCAD's Macro dialog. It adds bundled Python
module folders to the process search path and opens four editable documents.
The holder document also contains ExtendedClip, linked to holder wall thickness.
The top-level release FCStd is an exchange snapshot, not the parametric master.

Relevant final objects:
- carrier.FCStd: LongerPCBRetainers; predecessors include BlendedCarrier and JunctionFillets.
- holder.FCStd: ThickerHolderWalls and ExtendedClip.
- tapered-baseplate.FCStd: TaperedBaseplate (BottomScale).
- 01-pcb-cap-candidate.FCStd: PCBCap, unchanged.

## Rebuild current edits

Copy this source folder before modifying it. Run with the Python executable from
the pinned FreeCAD distribution (ordinary system Python cannot import FreeCAD):

    & 'C:/path/to/FreeCAD/bin/python.exe' ./rebuild_r02.py

This regenerates the R01 retention/wall/clip changes, assembled pose, and R02
baseplate taper from included parametric FCStd checkpoint inputs. Outputs are under
generated/mouse-hats/print-test/r02. The published package above source/ stays fixed.

Geometry-build scripts and units are under designs/mouse-hats/{model,reconstruction,
print-test,baseplate-taper}. Retention/holder settings: print-test/settings.json.
Taper settings: baseplate-taper/settings.json. Existing broader/older scripts are
preserved for context; they can require historical assets omitted from this package.
The tested rebuild_r02.py entry point does not require those original archives.

The source tree is not the entire historical import pipeline. Initial extraction
from 58 STEP and mesh pose-fitting are represented by saved checkpoint inputs and
measurements. Re-running extraction/fitting requires original playground assets.

The release builder/STEP verifier are under designs/mouse-hats/release. Their
outputs go into this working tree's own releases/ folder. Export in the FreeCAD GUI
to preserve colors; use the documented export_release.py helper.
