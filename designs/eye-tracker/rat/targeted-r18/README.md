# Rat R18: camera assembly on the caudal baseplate

R18 combines the accepted R17 baseplate pose, R16 symmetric design skull and R14
eye targets with the matched mouse camera hardware. The detailed Pupil Core R08
camera geometry is retained. It is a complete monocular review assembly, not a
print release or a replacement of the selected historical rat R01 checkpoint.

## Placement and aim

The source hardware is mouse compact-guard R16 in its local mount frame. A rigid
mount-to-skull transform maps its baseplate's rostral top point and mating-face
normal to the accepted rat R17 pose. The final baseplate has zero Boolean
symmetric-difference volume from R17. The main PCB, connector, tray, cap and
baseplate retain their relative positions.

The camera head, holder, clip and neutral socket move together. Three cylindrical
ribbon bends are solved at the unchanged 32.85 mm sheet length and 4 mm width;
the shared detailed camera uses 0.25 mm thickness. Radius parameters are at least
3.75 mm. Both rectangular supports are rebuilt at the original tray roots and
socket terminals. The upper arm uses 8 mm control handles and segmented degree-3
lofts to avoid the invalid single loft produced at the new pose. The lower guard
retains the established two-span route with a local outer waypoint (-8, 0, 20) mm.

The target is the right eye's R14 schematic frame origin, not its corneal surface
or a newly measured anatomical center. In the R16 design frame:

| Quantity | Value |
| --- | --- |
| Eye target, mm | (8.263833, -8.284850, -6.338182) |
| Lens reference, mm | (7.160183, -22.054128, 1.054315) |
| Camera direction toward eye | (0.070442, 0.878863, -0.471846) |
| Eye-center ray miss | 0.000027 mm |
| Forward lens-to-target distance | 15.667 mm |
| Difference from opposing eye optical axis | 26.289° |

The initial local search reached approximately 20.6° but intersected the tray
with the ribbon. The accepted local refinement clears that overlap at 26.3°.
This aims at the eye center but is not coaxial with the eye. It is a feasible
local solution under the retained mount/ribbon constraints, not proof of a global
optimum. The search uses chosen weights, not a simulated optical field of view.

## Validation and remaining limits

Full-solid ribbon overlap checks pass against the fixture and camera parts.
Clearance to the upper support is 1.207 mm, lower guard 1.504 mm and socket
4.757 mm. Zero distance at the tray/PCB attachment is contact without positive
overlap. Both supports engage the tray and socket; the carrier is one valid
solid, with a closed mesh and no detected self-intersections. Shared matched-part
checks pass, including carrier/baseplate separation and rail/catch membership.

Inherited carrier overlaps remain: cap 0.002218 mm³ and connector 0.059028 mm³.
Neither increases. These are explicitly retained baseline issues, not clean-fit
claims. No hardware/skull or hardware/sclera surface crossings were detected.
6,600 sampled hardware surface points are outside each closed whole-eye mesh,
including the cornea. Skull containment is not asserted because the anatomical
skull is open. The baseplate is excluded from skull interference checks as
declared uncut contact stock. Surface checks, static clearance and numerical aim
do not demonstrate physical fit, full ball-joint motion, or ribbon fatigue life.

The model retains the original source mouse document's hidden anatomy as history;
only the added rat skull and rat eye surfaces are displayed. Use the rat target
coordinates and `candidate-manifest.json`, not hidden mouse frame objects, for
further rat work. The current rat selection is deliberately unchanged.

## Rebuild and inspect

Read `docs/development.md` and `docs/eye-tracker-targeting.md` first. Use the pinned
FreeCAD Python runtime for `build.py`, then `compose.py`, then
`check_interfaces.py`. Use the CAD tooling Python for `check_containment.py`.
The build reads the saved `solution.json`; exploratory `solve.py`,
`refine_ribbon.py` and `solve_clearance.py` overwrite that solution and are not
required for reproduction. `read_source.py` regenerates the source-frame record.

Submit `open.FCMacro` with the verified existing FreeCAD desktop PID; after the
display updates, submit `capture.FCMacro`. Freeze only after the validation files
and the displayed final document agree. `review.json` identifies the frozen
checkpoint and `recipe.json` records lineage. Exporting a print pack is separate.
