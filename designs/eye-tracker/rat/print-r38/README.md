# RAT R38 trial-print hardware

Open `generated/eye-tracker/rat/print-r38/RAT-R38-all-hardware-arms-flat.stl` in your slicer using millimetres. Keep its saved orientation: the carrier and matched holders are rotated to bring the arm spans toward the bed plane, and the two clips rest on their broad faces. The STL contains five separate solid shells. It excludes electronics and anatomy.

The export selects the complete R38 assembly through `../refined-supports-r38/review.json` and verifies its SHA-256 hash. Geometry is unchanged; only rigid print placement is applied. R38 includes the thicker central PCB support, revised arms, finished junctions and RAT R38 engraving. The skull baseplate is unchanged.

`export.py` runs with the pinned FreeCAD bundled Python from the repository root. It writes individual STLs, the combined STL, a native layout and `validation.json`. Each STL is reloaded and checked for closure and self-intersections. `open.FCMacro` opens the actual combined mesh in the existing desktop session and saves the review. Output units are millimetres; STL itself does not encode units.

This is an unsliced trial-print pack. Inspect supports and socket/holder gaps in the slicer before printing. Mesh validation does not demonstrate physical fit or printed strength.
