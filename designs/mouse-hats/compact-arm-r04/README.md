# MH-T3-EYE-R04: lower root and compact rear curve

Requested from the annotated R03 screenshot: move the rear/bottom arm from the
ribbon-exit side to directly below the adjacent circular tray hole and shorten
its rearward reach substantially. This intentionally replaces R03's preserved
large ribbon loop. Camera/socket position and neutral eye aim are retained.

Root moves from [4.106774, 12.550767, 16.766297] to
[4.106774, 8.2, 12.096621] mm in assembly coordinates. Root section is 2.6 × 2 mm
to fit the material below the 4 mm hole. The curved body is 2.6 × 1.8 mm with a
smooth transition to the 3 × 2.2 mm socket section, 0.2 mm root blends, and the
existing socket clearance. The cubic route has 13 mm end handles.

Rearward projection from the panel back is reduced from 19.965 to 11.197 mm
(43.9%). New curved centerline is 28.749 mm; straight leads are additional.
The previous preserved curve plus tray extension was about 42.438 mm, also
excluding its remaining socket straight lead. These are route measurements,
not ribbon length or minimum bend-radius specifications.

The source is the hash-verified complete R03 checkpoint. The saved T3 tray region
retains the PCB catch, raised cap rail, hole geometry and matching cap interface.
Only its obsolete rear-root protrusion is removed before attaching the new arm.
`settings.json` records dimensions and source hashes; `socket-source.brep` stores
the original socket construction shape. Historical modules supply sweep and
edge-selection functions only; no older complete carrier is selected.

Run `build.py` synchronously in the pinned FreeCAD GUI. It writes the candidate
native assembly and `validation.json`. One valid carrier, zero holder/clip/PCB/
baseplate interference, unchanged 0.333165 mm holder gap, retained catch and rail,
and cap contact equal to the R03 baseline. The optical guide is unobstructed.

The smaller loop needs a physical ribbon-bend and motion check. Ribbon dimensions
and bend limits have not been supplied. The prior R03 checkpoint is preserved.
