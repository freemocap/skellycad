# ET-MOUSE-ADULT-R11: representative adult eyes

Both eyes now use the [adult reference geometry](../../shared/adult-eyes-r01/README.md),
with separate cornea/sclera envelopes and preserved +Z optical axes. Dimensions
and assumptions are documented there. These are approximate adult models,
not measured male population medians.

The complete assembly retains matched camera hardware, ribbon route and skull.
`review.json` identifies the frozen native checkpoint and source hashes.
`validation.json` records unchanged hardware and anatomy surface checks.
Existing fitting limitations remain; this is a review candidate, not a print
release. Selected checkpoints are unchanged.

Use `open.FCMacro` through the existing desktop FreeCAD pipe after following the
shared build instructions. It displays the generated complete assembly; the
frozen copy is under `checkpoints/`.
