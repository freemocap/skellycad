# PCB cap — native 58 reconstruction candidate

Baseline: `old/58nassembly.step / RightCap`, identified by its unique 69-face solid
after verifying the approved STEP hash. Original files remain unchanged.

## Model and controls

`PCBCapRebuild58` shows cyan reconstruction and gold reference (+20 mm Y).
Saved output: `generated/mouse-hats/reconstruction/pcb-cap/01-pcb-cap-candidate.FCStd`
relative to the playground. This model uses native FreeCAD features and needs no
custom Python proxy to reopen or edit.

Ten named sketch/extrusion pairs form the stepped cover, side wall, retaining lips,
bottom flange and locating tabs. `CapShell` joins these; `PCBCap` subtracts the
three vent cylinders and side-hole cylinder. Profiles are measured, individually
blocked sketch segments, not yet fully redesigned semantic sketch constraints.

Live properties on `Dimensions`:

- `CoverThickness`: 1 mm, applies to upper and lower cover panels. Increases grow
  inward from the measured exterior faces and can consume assembly clearance.
- `VentRadius`: 2 mm for all three vents.
- `SideHoleRadius`: 1 mm.

Hole tools extend beyond the surfaces so thickness edits retain through-holes.
Construction dimensions/profiles are recorded in millimetres in `parameters.json`.
Manual document edits do not automatically update that file.

## Verification

One solid, 69 faces, 656.5616206943354 mm³. Both source and reconstruction pass the
deeper BOP check. Fresh build and saved-file reopen/forced recompute pass.
Tested thickness 1→1.1→1 mm, vent radius 2→2.1→2 mm and side-hole radius
1→1.1→1 mm. All edits pass deeper checks; every hole remains open.

The direct geometric prototype reports zero missing/excess volume. For the native
saved/recomputed model, source-minus-candidate reports zero, and the common solid
passes its check with source volume 656.5616206943383 mm³. However, the reverse
subtraction returns an invalid unorientable result, even with 0.001 mm tolerance;
that output is rejected rather than reported as a valid volume. Full Boolean
parity is not claimed. 240 surface samples each direction agree within ~1.9e-13 mm
(numerical agreement, not a global precision or manufacturing claim).

At source assembly placements and 0.001 mm interface tolerance:

- Original cap vs original carrier: zero interference volume.
- Rebuilt cap vs rebuilt tray: zero interference volume.
- Rebuilt base plate vs rebuilt stem: zero interference volume.

These are seated-position solid checks, not insertion-path, snap-force, board-fit
or print validation. See `validation-baseline.json`. User has not yet reviewed
this cap candidate. Baseplate's pocket-mouth discrepancy remains separately noted.

## Replay

Use the playground's pinned FreeCAD Python executable:
`.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe`.

1. Run `inspect_source.py` to verify the STEP and write source BREP/face diagnostics.
2. Run `measure.py` to regenerate the profile/hole parameters and direct prototype.
3. Run `build.py` to create the native FCStd from parameters alone.
4. Run `verify.py` for independent rebuild/reopen, edits, comparisons and interfaces.
   It expects existing tray/baseplate checkpoints and writes verified BREP snapshots
   used by `../assembly/show_review.py`.

No old arm, later two-arm meshes, skull mesh or printing work is included.
