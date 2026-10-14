# Mouse landmark review R02

Use this study to correct landmark locations and descriptions in FreeCAD. Each
proposal preserves its original transferred coordinate, source ID, name evidence,
review state and notes. It does not refit the eyes or change camera hardware.
The prior study remains the provenance reference.

The detailed display is reconstructed directly from the published Maga skull
segmentation: 3,552,316 original surface triangles reduced to 180,000 for review,
then transformed by the preceding study's saved alignment
[@maga2017MouseSkullAtlas; @magaMouseCTAtlasRepository]. This is a higher-detail
reference, not a newly validated registration. The original source/license and
hashes remain in `skull-landmarks-study-r01/sources/`. No atlas anatomy is
sculpted to match the existing low-poly skull. Bone identities and landmark
anatomical names remain incomplete.

## Correct a landmark

1. Follow `docs/development.md` to send this directory's `open.FCMacro` through
   the existing FreeCAD desktop pipe. It opens the working copy and review panel;
   it never edits the frozen checkpoint directly. Existing working edits remain.
2. Select a landmark in the panel. Numeric IDs remain authoritative. The
   eye-region focus shows IDs 7–12 plus 13, 16 and 51. These are inspection
   candidates, not a claim that each ID is a verified orbital landmark.
3. Click **Pick new position on skull**, then click a visible skull surface.
   The marker moves only when the detailed reference or existing skull is hit.
   A click on a marker or empty space does not move it. Rotate the view and
   repeat as needed. The panel reports displacement from the original point.
4. Enter a proposed anatomical name and a reason or uncertainty in the text
   fields, then click **Apply name / note**. This marks a proposed correction,
   not anatomical confirmation. `ReviewState` can be set explicitly to
   `User confirmed` in the object's Review properties after inspection.
5. Click **Save correction snapshot**. The panel saves the working CAD document
   and a new UTC-stamped JSON file under `corrections/`. Older snapshots and
   original coordinates remain intact. Corrections are not silently applied to
   the eye placement or skull-registration transform.

**Reset point to original** restores the selected coordinate while retaining
its proposed name and notes. FreeCAD Undo also supports panel edits. Direct
editing of a marker's `Placement > Position` is supported; the annotation
updates when saving a correction snapshot. Keep the skull reference fixed.

The panel can show all 45 markers, switch detailed/existing skull surfaces,
and toggle the previous study's conditional candidate eyes. Comparing those
surfaces helps separate an ambiguous anatomical landmark from a mismatch in
registration. The original atlas points were transferred onto the existing
assembly frame; they have not been snapped onto either surface.

## Recommended next use

Review bregma/lambda and the bilateral eye-region points on the detailed atlas,
then compare their transferred positions on our existing skull. Keep ambiguous
names provisional. In parallel with that anatomical review, the next eye-model
step is tracing the outer globe in the downloaded Digimouse tissue slices.
Those traces can distinguish globe center from the internal lens-region center;
skull surface landmarks alone do not establish resting gaze. Source data and
the conditional orientation comparison are documented in
`../registered-eyes-study-r01/README.md`.

Blender remains an option for future mesh editing, but the immediate work is
point annotation and source comparison. The correction JSON preserves explicit
millimetre coordinates and identifiers for transfer to another tool later.

## Rebuild and checks

Run `prepare_reference.py` using `tools/cad/.venv/Scripts/python.exe` from the
repository root. It uses the preceding study's nibabel dependency and validates
its source hashes. Send `build.FCMacro` through the desktop pipe only when
creating a fresh review; it rebuilds the generated baseline. Use `open.FCMacro`
for continuing existing work. The build verifies the source study and selected
complete-assembly hashes before creating a review copy.

`panel-validation.json` records an exercised surface hit, marker movement,
unchanged original coordinate, 45-point snapshot export and reset. Test output
was written under generated, not the human correction ledger. These software
checks establish editing behavior, not anatomical accuracy. `review.json`
identifies the frozen baseline; later user edits belong to the working copy
and timestamped correction snapshots.
