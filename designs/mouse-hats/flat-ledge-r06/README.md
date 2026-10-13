# R06 flat PCB ledge

The user requested removal of the downward-facing PCB catch return. The retained ledge projects 1.6 mm from the PCB seat, is 0.4 mm thick and spans 3 mm along the edge; the thicker supporting root is preserved. This removes 2.493326 mm3 from the catch. It no longer provides the former hook's restraint against outward PCB lift; physical fit must be tested.

`build.py` replays against the hash-pinned full R04 assembly in the local FreeCAD GUI runtime. Matched cap, raised engagement rail, holder, clip, baseplate, camera pose and arm remain unchanged. Native validity, single-solid carrier, unchanged part contacts and 0.333165 mm holder clearance passed. Native volume integration tolerance is 0.0001 mm3.

The selected complete assembly is `current/checkpoints/MH-T3-EYE-R06.FCStd`. Its R04 compact arm remains a reference, not an A/B/C selection. The same subtractive change is saved in R06-A/B/C.FCStd from the preserved R05 variants. Their labels and loop sizes are retained. R05 print tests remain historical and the user is still testing them.

Exports are in `generated/mouse-hats/active/print-r06/`. Use either an A/B/C carrier-and-holder STL or the complete-reference carrier-and-holder STL, plus matched common accessories as needed. Do not print all alternatives unintentionally. Slicer settings and supports are not embedded. No print submitted.

The native ledge comparison shows the old hook in orange and new ledge in cyan.
