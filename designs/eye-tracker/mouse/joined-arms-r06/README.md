# Joined arm junctions R06

R06 finishes the accepted R05 arm layout for a print test. The rear loop remains
at its current roomy setting, as permitted by the user. Camera, ribbon, cradle,
ball and arm routes stay in place.

Each arm tip extends 0.8 mm deeper radially into the stationary socket stem.
The extension overlaps 0.25 mm into the existing tip before fusion. Socket
engagement increases from approximately 0.044 to 2.540 mm3 for the upper arm
and from 0.080 to 4.657 mm3 for the rear arm. The axial bore is checked separately.

Junction finishing:

- Upper tray root: 0.35 mm fillet.
- Rear tray root: 0.20 mm chamfer along the three attachment edges. A fillet on
  these edges produced self-intersecting surfaces and was rejected.
- Upper and rear stem connections: 0.30 mm fillets.

The socket extracted in R03 had a curve-on-surface tolerance error that its
basic validity check did not flag. Setting its representation tolerance to
0.000001 mm resolves the detailed Boolean check without changing its surfaces.
The finished carrier must pass the detailed Boolean check, be one valid solid,
and pass collision checks before exports are written.

## Build and review

From the repository root, using the pinned FreeCAD bundled Python, run this
folder's scripts in order: `prepare.py`, `blend.py`, `finish_rear_root.py`, `clean_print_mark.py`, and `export.py`. R05 must already be generated. Preparation verifies the selected
complete-assembly checkpoint hash. Blending uses the pinned topology's junction
edges and matches their geometric signatures after each operation; changing
inputs requires rechecking those selections.

Generated artifacts are in `generated/eye-tracker/mouse/joined-arms-r06/`.
The `print` directory contains the carrier and holder together, matching cap,
clip and baseplate. The ribbon, anatomy and camera electronics are excluded.
Mesh closure and self-intersection checks are required for every STL.
Do not split and independently arrange the carrier/holder pair.

This is a print-test revision. Static geometry verification does not establish
physical strength, fatigue resistance or the full adjustment range. The original
selected checkpoint and its matched print files remain unchanged.

The obsolete raised B marking on the tray back caused coplanar STL triangle
intersections even at finer mesh settings. R06 removes only this exterior mark
(about 4.55 mm3), restoring the flat rear face; the arm routes and mating
interfaces are unchanged by that cleanup.

## Superseded print candidate

R07 in ../seated-tip-r07 corrects the upper terminal overhang found during user review. Use the R07 matched print package for the next test. The R06 checkpoint is preserved for comparison.

R07 was subsequently rejected for its tapered terminal. Use ../inset-arm-r08 for the full-thickness inward-shifted replacement and its revised ribbon route.
