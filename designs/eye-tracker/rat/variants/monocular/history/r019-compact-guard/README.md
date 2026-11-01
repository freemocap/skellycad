# Rat R19: tighter rear guard

R19 replaces only R18's rear guard and fused carrier. A single degree-5 Bezier
centerline replaces the two-span loop, removing the internal curve junction and
bringing the bend inward. The root and socket terminal sections retain their
dimensions and engagement. Camera aim, ribbon, upper arm, baseplate and anatomy
are inherited unchanged from the hash-verified complete R18 checkpoint.

The guard has 1.144 mm minimum static ribbon clearance and no ribbon overlap.
Tray and socket engagement volumes are 2.445 and 4.657 mm³. The carrier is one
valid solid; its exported mesh is closed and has no detected self-intersections.
No new carrier/hardware overlaps occur. R18's small cap and connector overlaps
remain unchanged. The guard has no detected surface crossings with the skull,
sclera or cornea; 2,400 sampled guard points lie outside each whole-eye envelope.
The open skull does not support a containment claim. These checks do not prove
physical fit or clearance throughout ball-joint motion.

Run `build.py`, then `check_anatomy.py` with the pinned FreeCAD Python runtime
from the repository root. `open.FCMacro` opens the generated complete assembly
in the existing desktop session and reuses an existing matching tab. The source
R18 checkpoint is preserved. `review.json` identifies the frozen R19 review.

The historical selected R01 file failed its recorded hash check before this
change. Its actual and recorded hashes are in `validation.json`. R01 was neither
used as geometry input nor modified; this candidate remains separate from that
selection. Resolve the historical mismatch before rebuilding from R01.
