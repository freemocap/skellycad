# Arm junction finishing — 2026-10-09

User accepted and committed the face-aligned arm checkpoint (`832132f`), then
authorized targeted strength/edge improvements before further user-directed
reinforcement edits and a print test.

This pass adds **0.5 mm inside fillets at four tray-root edges** (three rear,
one top) and **0.3 mm inside fillets at eight socket-collar junction edges**.
These are radius measurements. The flush outer sides of the tray roots stay
flush. Arm paths, body sections, stem fit, PCB retention and socket interiors
are preserved. General exposed-edge rounding is deferred: the useful first
change is junction support, not thinning the arms or altering fitting edges.

## Reproduce and inspect

1. Build the existing attachment concept with `build_attachment_arms.py` if needed.
2. Run `build_finished_arms.py` with the pinned FreeCAD Python runtime.
3. Run `verify_finished_arms.py` in a fresh pinned Python process.
4. Execute `show_finished_arms.py` in the live FreeCAD GUI.

Output: `generated/mouse-hats/arms/finished/finished-arm-carrier.FCStd`.
Visible cyan is the complete fused carrier; gold faces highlight junction fillets.
`JunctionFillets` has editable `TrayRootRadius` and `SocketRootRadius` properties.
Zero disables a stage. Default radii live in `arm-finishing.json`; GUI changes do
not automatically update JSON. The source arm features remain editable in this
document. Edge selection derives from attachment planes/dimensions and the collar
cylinder; it fails explicitly if the expected edges are no longer identifiable.
Do not treat arbitrary arm dimension changes as verified finished variants.

## Evidence and limits

- One valid solid; deeper OCCT geometry check passes.
- Added volume about 0.731 mm³; removed volume zero at 0.001 mm Boolean tolerance.
- Additions have zero overlap with the PCB cap, screw bore or ball-seat sphere.
- All added material stays within the tested local junction regions.
- Fresh reopen, radii `(0, 0)`, `(0.4, 0.2)`, restoration to `(0.5, 0.3)` pass.
- Full views and opposite-side views inspected in FreeCAD.

Reports are `validation.json` and `edit-validation.json` beside the generated file.
Volume differences have small Boolean integration/tolerance discrepancies; they
are not exact mass measurements. Fillets are intended to reduce stress
concentration; no strength gain has been measured or simulated.

The checkpoint file and canonical CURRENT are unchanged. This is the latest
finishing candidate. Holder movement, ribbon routing, final print orientation,
tool access and physical strength remain unverified. Next: user's observed
reinforcement needs, complete camera-head review, then slicer/print evaluation.
