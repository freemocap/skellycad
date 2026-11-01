# R08 full-thickness upper arm moved inward

R08 replaces the rejected R07 top taper. The upper attachment center moves
1.1 mm down the stationary housing axis, from 5.3 to 4.2 mm above the socket
reference point. Its terminal section remains 3.0 mm wide and 2.2 mm thick.
The resulting nominal axial span is 3.1–5.3 mm, within the collar's 2.4–5.4 mm
span. The existing curved arm generator connects the unchanged root to this
new terminal position. The rear arm retains its R06 route.

The ribbon is re-solved with both PCB positions and orientations fixed. It
retains the 32.85 × 4 mm neutral sheet and assumed 0.15 mm thickness. The new
inside radii are 3.5, 6.329 and 3.5 mm, with 1.629 mm of straight entry at the
sensor. The 3.5 mm lower bound comes from the user's 7 mm rod observation;
it is not a manufacturer bend-radius specification.

## Checkpoint and reproduction

The selected repository checkpoint remains ET-MOUSE-MONO-R01. R08 is a separate
complete assembly for review and print testing. `print-test.json` identifies its
frozen checkpoint, hash and matched parts. R06 is the input complete assembly;
R07 geometry is not used. `prepare.py` verifies the R01 and R06 checkpoint hashes.

From the repository root, run these scripts in order with the pinned FreeCAD
Python runtime described in `docs/development.md`:

1. `prepare.py`: regenerate the full-thickness arm and its embedded attachment.
2. `solve.py`: adjust the ribbon using fixed endpoint frames and local collision
   planes. Full-solid checks in subsequent steps establish collision clearance.
3. `blend.py`: finish arm junctions and preserve the R06 obsolete-label cleanup.
4. `ribbon.py`: build the finite-thickness ribbon and check retained hardware.
5. `export.py`: check the finished carrier and write the matched print meshes.

Use `open.FCMacro` through the existing-window workflow to review R08, then use
`closeup.FCMacro` with that assembly active to inspect the junction. After the
GUI save, run `package.py` with the CAD tooling Python to freeze the reviewed
checkpoint, record its hash and package the prints.

Generated outputs are under `generated/eye-tracker/mouse/inset-arm-r08`.
Keep carrier and holder in their exported relative placement and use the cap,
clip and baseplate from the same package. Geometry checks do not establish
physical fit, strength or material stress. No external technical sources were
added; the change uses local geometry and the user's routing measurements.

## Validation result

The finished carrier passes the detailed solid check as one solid. All four STL exports are closed and have no detected self-intersections. The revised ribbon has zero modeled overlap with the finished carrier; its closest gap is only 0.0065 mm, so this is a near-contact route, not a manufacturing clearance allowance. The moving holder retains 0.333165 mm clearance and the stem bore is clear. The inherited cap overlap of 0.002218 mm³ is unchanged. Inspect junction.png and assembly.png beside the generated validation report.
