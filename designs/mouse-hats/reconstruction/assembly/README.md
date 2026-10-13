# Six-part linked assembly — 58 baseline

Current view: `02-linked-assembly.FCStd` under generated/mouse-hats/reconstruction/assembly.
Run `open_model.py` in the pinned FreeCAD GUI to load proxy modules and the saved assembly.
Run `build.py` with the pinned Python to recreate it from the six saved part models.
`parts.json` records file/object references and measured local-to-assembly placements in mm.
Keep the generated part folders beside the assembly: the FCStd is not a standalone package.
Recreate missing part models with their individual builders before building the assembly.

Two tree groups organize six App::Links:
- MountAndElectronics: purple skull baseplate, cyan PCB tray/stem, transparent green cap.
- CameraHead: gold socket, blue holder/ball, pink retaining clip.

Links reference editable final features, not BREP copies. `LinkTransform=True` preserves
source feature placements; LinkPlacement applies the measured assembly frame. Holder uses
the inverse of its assembly-to-holder transform. Clip frame was preserved from the reference
preparation report; socket frame comes from socket parameters. Tray, cap and base use identity.
The old arm is deliberately omitted, leaving the camera head unsupported in this model.

Edits to linked source documents propagate after recompute. Save the edited part document as
well as the assembly to retain edits. Existing open part documents are reused without saving
them automatically. Placements are fixed: no joint solver, automatic mating, or motion model
has been added. Geometry edits can change fit without repositioning the other parts.

## Verification

Run `verify.py` in a separate pinned Python process. Recorded results are in validation-baseline.json;
latest generated results are in generated/mouse-hats/reconstruction/assembly/validation.json.
- Fresh-process reopen: all six links resolve, each has one solid and passes deeper shape check.
- Transformed bounding boxes and solid centroids agree with the independently transformed
  source features within 1e-7 mm (actual maximum about 5.2e-15 mm).
- Cap VentRadius 2 -> 2.1 mm and baseplate BoreRadius 1.45 -> 1.55 mm propagate to assembly
  volumes; restoration passes. Tests do not save modified source files.
- All 15 pairwise common-solid operations are valid and yield 0 mm3 at 0.001 mm tolerance.
  This is a seated interference check, not a physical-fit, insertion-path or retention test.
- Socket inner sphere radius 2.1 mm and holder ball radius 2 mm have centers separated by
  0.299997 mm. Original 58 source sphere centers were checked directly and have the same
  approximately 0.3 mm offset. Radius difference alone is not uniform assembled clearance.
  The socket is an open, trimmed shape; full-sphere overlap reasoning does not establish
  overlap of its actual material. No recentering has been applied.

Inherited part qualifications remain in each part README: holder root blend approximation,
baseplate pocket-mouth discrepancy, socket source errors, omitted arm junction, and cap's
invalid reverse difference result. Assembly checks do not establish full source parity.

## Earlier review

`show_review.py` and `01-tray-cap-baseplate-review.FCStd` remain the historical three-part
static snapshot. They do not propagate changes; use the new linked assembly for ongoing work.

Next: review the six-part assembly, then select functional parameters and interface checks
for intentional changes. The deferred two-arm mesh phase requires the user's direction.
