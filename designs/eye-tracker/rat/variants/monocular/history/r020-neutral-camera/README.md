# Rat R20: camera aligned with the neutral eye axis

R20 moves the camera lens 5.807 mm rostrally, 0.848 mm medially and 3.708 mm
ventrally relative to R19. The lens remains 14.235 mm from the schematic eye
center. Its inward optical axis opposes the eye's outward neutral axis to within
0.001 degrees, compared with 26.289 degrees in R19. This is numerical alignment
to the existing anatomical estimate, not a measurement of a living animal.

The camera head, lens, LEDs, holder, clip and socket move as one rigid group.
Both arms are refitted, retaining the continuous rear-guard curve introduced in
R19. An alternative first ribbon bend direction allows the closer alignment;
the ribbon retains its 32.85 mm length, 4 mm width and 0.25 mm thickness. No
stretching or added cable length is used. The main PCB, connector, tray, cap,
baseplate and anatomy remain unchanged, verified against R19 in
`r19-comparison.json`.

Full-solid ribbon checks detect no positive overlap with the hardware. The
smallest arm clearance is 0.374 mm at the upper support; rear-guard clearance
is 1.504 mm. End attachment contact is intentional. The carrier is one valid
solid with a closed mesh and no detected self-intersections. Matched-part checks
pass. Inherited carrier overlaps with the cap (0.002218 mm³) and connector
(0.059028 mm³) remain unchanged. No hardware/skull or hardware/sclera surface
crossings were detected; 6,600 sampled hardware points lie outside each closed
whole-eye envelope. The open skull does not establish containment clearance.

This is a complete static review candidate. The 0.374 mm clearance requires
physical review; full joint motion, ribbon fatigue and print fit are not proven.
The source R19 checkpoint and historical species selection are preserved.
The historical R01 selected file still differs from its recorded hash and is
not used as geometry input here.

## Rebuild

Read `docs/development.md` and `docs/eye-tracker-targeting.md`. From the repository
root, run `build.py`, `compose.py`, `check_interfaces.py` and `compare.py`, in
that order, with the pinned FreeCAD Python runtime. Run `check_containment.py`
with the CAD tooling Python. Builds use the saved `solution.json`.
The search scripts are exploratory and may replace that solution; they are not
part of reproduction. `recipe.json` records lineage and targeting intent.

Submit `open.FCMacro` to the verified existing desktop process. It reuses a
matching document rather than creating duplicate save paths. `focus.FCMacro`
sets the dorsal comparison view. `review.json` records the final saved native
checkpoint and hash; `candidate-manifest.json` keeps its matched parts together.
