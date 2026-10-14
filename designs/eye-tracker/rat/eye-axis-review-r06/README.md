# ET-RAT-EYE-AXES-R06: eye optical axes

Complete assembly from `designs/eye-tracker/rat/detailed-camera-r05/checkpoints/ET-RAT-DETAILED-R05.FCStd` with two visible eye axes.
Eye +Z points through the corneal apex; green and magenta distinguish the eyes.
Cyan is the camera axis. Shapes and world placement are preserved.

See [anatomical audit](../../shared/eye-anatomy-audit-r01/README.md) for
measurements, literature, confidence and proposed mouse-eye corrections.
`review.json` identifies the frozen native checkpoint and SHA-256.
`axis-validation.json` records axis and placement checks. Existing holder and
ribbon interference remains; this is not a print release or demonstrated fit.
The species active-model selection is unchanged.

Read the repository development workflow before rebuilding. Use the pinned
FreeCAD Python to run `designs/eye-tracker/shared/eye-anatomy-audit-r01/add_axes.py`
with this folder's `recipe.json`. The generated complete assembly can then be
opened with `open.FCMacro` through the existing desktop pipe. The immutable
review copy is under `checkpoints/`.
