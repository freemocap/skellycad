# Print-test revision R01

Latest working print candidate, 2026-10-09. Builds on the accepted arm junction
fillets and R3 stem blend. The old canonical CURRENT remains a historical
six-part baseline; use this folder's outputs for the present test.

## Changes agreed with the user

- Extend two PCB retainers 1.5 mm along the board edge toward its middle.
- Extend the opposite/lower retainer 0.7 mm, preserving the existing cap.
  A 1.5 mm lower extension collided with the cap and was not adopted.
- Add 0.5 mm outward to the holder's side walls, including its exterior clip seat.
  The original sensor cavity, ball and neck are preserved. No original holder
  material is removed. Side-rail thickness goes from approximately 1 to 1.5 mm.
- Adapt the clip to the thicker holder: its crosspiece is 1 mm longer and each
  intact retaining arm moves outward 0.5 mm. Hook shape and arm section are kept.
  The earlier taper-to-fit-the-old-clip approach was superseded by user instruction.
- Recover the holder's pose from the supplied V5 mesh, with translation anchored
  to the unchanged spherical ball, for a print-in-place carrier/holder test.

`settings.json` is the authoritative build input in mm. The carrier's live
`Extension` / `LowerExtension` controls and holder's `OutwardThickness` property
are editable in saved files. The extended clip follows the holder property.
GUI changes do not update JSON or exported STLs automatically; rebuild to export.

## Outputs and printing scope

Under `generated/mouse-hats/print-test/r01/`:

- `carrier-and-holder-print-in-place.stl`: two separate closed bodies in their
  assembled relative positions. Keep them together; do not independently arrange
  or fuse them in the slicer. This is the articulated carrier/holder unit.
- `clip.stl`: revised clip, printed separately and installed later.
- `cap.stl` / `baseplate.stl`: unchanged parts, printed separately.
- `carrier.FCStd` / `holder.FCStd`: editable feature graphs.
- `print-in-place-review.FCStd`: assembled inspection snapshots. Gold clip is an
  installed-fit reference, NOT included in the print-in-place STL. Cap and
  baseplate references are hidden by default. Execute `show.py` in FreeCAD.
- `carrier.stl` / `holder.stl` are diagnostic individual exports; they are not
  the intended print-in-place input.

Exports are in mm and retain assembly orientation; bed orientation/supports have
not been configured. No printer job was sent. The user knows Orca slicing; inspect
the joint gap/support placement there before the test. Minimum modeled carrier/
holder separation is about 0.121 mm at this pose. This is a print-fit experiment,
not a validated free-moving joint or full motion-envelope analysis.

## Reproduce

Run with the pinned `.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe`:
`build.py`, `export_reference.py`. The accepted upstream generated arm/stem and
baseline part files must exist; see the model/reconstruction folders for builders.

Run with the analysis `tools/cad/.venv/Scripts/python.exe`: `fit_holder_pose.py`,
then `recover_ball_pose.py`. They use the already registered V5 holder shell from
the previous arms study. Rotation uses rigid trimmed ICP; translation then aligns
the known ball center to a sphere fit. No mesh is altered or scaled.

Return to pinned CAD Python: `assemble.py`, `verify.py`. Run `show.py` in the live
GUI. The assembly review is an explicit snapshot, not a mating solver.

## Evidence and limitations

Each edited part is one valid solid and passes the deeper geometry check. The
carrier additions do not overlap the cap/baseplate. The holder loses no material
and gains none inside the original inner-rail envelope. Added volumes are about
17.30 mm³ for the PCB retainers and 49.11 mm³ for holder wall stock. Reopen,
coordinated dimension edits and restoration pass; clip width tracks twice the
wall addition. Exported STLs are watertight with consistent winding; the combined
file contains exactly two shells and each accessory contains one.

The holder/carrier common volume is zero in the assembled pose. The rigid mesh
orientation fit has approximately 0.328 mm 70th-percentile nearest-sample residual,
which includes V5 shape changes and sampling; it is not a precision orientation
certificate. Sphere fitting uses 627 inlier vertices and recovers ~2.00019 mm
radius versus the native 2 mm ball. Review the visible pose before printing.

The clip retains a tiny intersection attributable to inherited skew and coincident
surfaces: ~0.0045 mm³ at 0.0001 mm Boolean tolerance (~0.0006 mm³ with exact Boolean).
It is not represented as perfect zero interference; physical clip fit remains a
test item. No clip material was shaved away to accommodate the walls.

Ball/neck enlargement, weight-reduction openings, thermal behavior, load capacity,
full camera travel and ribbon routing remain separate, unvalidated work.

R02 supersedes the print bundle with a tapered baseplate only; see ../baseplate-taper/README.md. R01 remains preserved.
