# 2. Sketch-based mounting plate

Original 40 × 24 × 3 mm teaching plate, four 3.2 mm holes, 6 mm edge offsets.
Compare checkpoints/07-top-chamfer.FCStd (0.5 mm equal-leg chamfer) and
08-top-fillet.FCStd (0.5 mm radius). These are alternative features, not stacked.

## Lesson / checkpoint order

1. build.py -> 01-constrained-outline: rectangle constrained to XY origin.
2. pad_step.py -> 02-padded-plate: 3 mm thickness.
3. hole_sketch_step.py -> 03-hole-outline: radius and center constraints.
4. pocket_step.py -> 04-through-hole: ThroughAll.
5. opposite_hole_step.py -> 05-opposite-hole: equal radius, opposite margin.
6. opposite_row_step.py -> 06-four-holes: matching second row.
7. chamfer_step.py -> 07-top-chamfer.
8. fillet_comparison.py -> 08-top-fillet: rebuilds alternative in another document.

For fresh builds use ../replay.py with stages `sketch`, `pad`, `hole-sketch`,
`pocket`, `two-holes`, `four-holes`, `chamfer`, `fillet`. Functions are in model.py;
historical step scripts expect PracticeMount and fixed output names. Use them in
a working copy; do not overwrite preserved checkpoints. Exit sketch edit mode
before applying the next feature when following the legacy interactive sequence.

The lower-left sketch corner is fixed; length/width grow along +X/+Y. Hole
dependencies use constraints and expressions, not a native pattern feature.
Checks cover constraints, valid solids, expected volumes, hole placement, selected
parameter variants and edge-treatment dimensions. Edge selection is geometric
at feature creation, then stored as native edge references: major topology edits
require rechecking. See CHANGE-NOTES.md for the detailed sequence.

The historical FCBak file is preserved alongside checkpoint 05 as recovery
history; it is not another lesson. No physical print/strength claim is made.
