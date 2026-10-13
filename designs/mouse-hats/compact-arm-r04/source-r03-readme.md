# Current mouse-hats model

**MH-T3-EYE-R03** combines the latest PCB Spring Catch geometry with the neutral
eye alignment and preserved rear ribbon loop. The single authoritative selector
is [active-model.json](active-model.json). It records the checkpoint hash, parts,
export script and print directory.

Open [the native checkpoint](checkpoints/MH-T3-EYE-R03.FCStd). It contains the full
assembly and skull references; no historical custom feature modules are needed.
Cap and approximate PCB are hidden initially to expose the catch and raised rail.

Current print files are under `generated/mouse-hats/active/print/`:

- `MH-T3-EYE-R03-carrier-and-holder.stl`: two-shell print-in-place pair.
- `MH-T3-EYE-R03-matching-cap.stl`: the matched T3/T2 deeper-hook cap.
- `MH-T3-EYE-R03-camera-clip.stl` and `MH-T3-EYE-R03-baseplate.stl`.
- `MH-T3-EYE-R03-print-pack.zip`: all four STLs plus notes.

Use the included cap. Physical emboss retains T +1.0 mm; full revision identity
is in filenames. Prior `R02-ribbon-space-carrier-and-holder.stl` was incorrect
because it omitted PCB retention improvements, and is quarantined under
`generated/mouse-hats/archive/wrong-baseline/`.

## What is retained

From the latest PCB chat: +1 mm tray, JST-ward wider/shorter catch, deeper matched
cap hook and local relief, T3's 0.7 mm raised engagement rail, labels and flush stem.
From the eye study: posterior joint position, centered holder aimed at the same
provisional eye target, original R11B ribbon-loop shape and extended tray connection.

The T3 tray region is taken directly from its saved Carrier shape. The eye-study
arm region joins it across unchanged straight root sections. `inputs.json` records
source hashes, source chat/turn, and splice planes. The native input snapshot is
durable under sources/. Historical generated files are not replay dependencies.

## Validation and limits

One deep-valid carrier. Zero PCB, holder, clip and baseplate overlap. Holder gap
0.333165 mm. T3 catch and rail have zero missing volume. Seven tray cross-sections
match T3 to under 0.000001 mm in wire length. Cap contact remains the inherited
0.00221823 mm3, unchanged from T3. Holder/clip poses and optical guide are preserved.
Native reopen and independent STL shell/winding/volume checks pass. Each print
export checks the manifest hash and PCB catch/rail presence before writing.

Physical PCB/cap insertion, ribbon fit, full motion, strength and surgical placement
remain unverified. The eye target and lens datum remain approximate. This is the
current working/print-test model, not a claim of physical validation.

## Rebuild and future edits

Run build.py through synchronous execute_code in the pinned FreeCAD GUI. It uses
the hash-verified local input snapshot and emits a fresh assembly under generated.
This is a saved geometry checkpoint with region provenance, not a new universal
parametric model. Inputs preserve both the exact T3 and eye/ribbon geometries.

For a new revision, preserve this checkpoint, validate the affected interfaces,
and update active-model.json to the new complete checkpoint and matching parts.
Run export_print.py in FreeCAD, then verify the exported meshes. The current
exporter will reject a changed checkpoint until its manifest is explicitly updated.

[Baseline reconciliation](RECONCILIATION.md) - [Historical source index](../INDEX.md)
