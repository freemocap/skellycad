# Mean camera frustum and focus assessment — R02

R02 replaces the two displayed R01 frusta with one estimate, as requested on
2026-10-30. The horizontal and vertical full angles are arithmetic means of
the email-derived 192-mode estimate and the conditional Cam2 400-mode estimate:
**38.29359 x 38.26067 degrees**. Acquisition still defaults conceptually to
400 x 400 at 120 Hz; the reference geometry no longer branches by resolution.

This mean is an engineering simplification, not a newly measured calibration or
an uncertainty interval. The underlying source values and assumptions remain in
`parameters.json`; see [R01 evidence](../optics-r01/README.md)
[@pupilCoreEyeIntrinsics2026; @opencvCalibR02]. R01 native reviews and its replay
implementation remain historical inputs, not a second actively maintained model.

## What the geometry represents

The complete R08 camera and mouse R19 assembly receive one orange wireframe
frustum and a consistent effective sensor rectangle. The rectangle is derived
from the mean angle and 1.7 mm focal length using `width = 2*f*tan(angle/2)`;
it is not a new measurement of the silicon or active region. The original
1.15 mm square specification remains recorded as the 192-mode email evidence.
The existing optical axis, all physical solids and all placements are preserved.
All new optical objects are non-printing references.

The projection center remains schematic: the inherited hypothetical sensor datum
plus 1.7 mm along the optical axis. The 20 mm extent remains a drawing limit,
not a depth-of-field boundary. The R08 lens barrel and optical surface are
mock-up geometry, not a lens prescription. Neither that barrel shape nor the
drawn focal-length segment determines the actual focus setting.

## Focus assessment

**Focus at the modeled eye distance is unverified.** A coverage frustum specifies
which directions are imaged, not which object distances are sharp. Depth of field
depends on the focus setting, aperture and required image detail/contrast
[@edmundDofR05]. These are missing for this particular lens assembly, as are its
optical principal planes and a measured sensor-to-lens optical spacing.

**User correction, 2026-10-30:** this particular lens screws in and out and is
adjustable. Use that direct observation for this assembly. The general Pupil
documentation describes a glued 200 Hz lens [@pupilCoreFixedFocus2026], but it
does not establish the condition of this unit. See [conditional focus estimates](../focus-estimates-r01/README.md)
for plausible screw travel, depth of field and replacement-lens comparisons.

`validation.json` reports the positive intersections of the preserved optical
axis with the modeled Eye1 cornea and sclera, measured from the schematic
projection center in millimetres. It separately reports the eye-center distance
from the inherited lens datum. The corneal and scleral meshes are anatomical
proxies; these distances are not measured mechanical working distances. Their
axial vertex ranges cover each whole mesh, including surfaces not visible to the
camera, and are not a required depth-of-field interval.

For pupil tracking, the apparent iris/pupil is seen through the cornea. Focusing
on an outer corneal mesh alone does not validate sharp pupil boundaries; this
model does not simulate ocular refraction. There is currently no optical evidence
that requires moving the camera, nor evidence that guarantees the present
distance will work.

A practical next check is to hold a fine, high-contrast target at the proposed
eye location under the intended illumination and acquire at 400 x 400. Sweep the
target distance around that location after adjusting and then holding the lens focus;
record the near and far distances that preserve the pupil-edge detail needed
for tracking. Confirm on representative eye images because a flat target does
not reproduce corneal optics. Alternatively obtain the factory focus distance,
f-number and depth-of-field specification, including its sharpness criterion,
from Pupil Labs. Use those results before changing camera placement or supports.

## Build and open

Read `docs/development.md` first. From the repository root, run:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/shared/cameras/pupil-core-eye/optics-r02/build.py
```

The build uses the hash-verified selected R08 camera through `shared.camera.add_camera`
and the hash-verified selected mouse R19 complete assembly. It writes new native
reviews under `generated/eye-tracker/shared/optics-r02/`. Success prints
`OPTICS_R02_OK` and records `passed: true` in `validation.json`. Checks cover mean
frustum dimensions, sensor-reference area, frame transforms, unchanged existing
geometry, ray intersections and saved-file integrity/reopening. They do not
establish optical focus or physical fit. Stop if validation fails.

Send `open.FCMacro` through the repository's native existing-session IPC with a
freshly verified desktop PID. It saves a recovery copy of the preceding R01 mouse
review before closing that task-owned tab, opens the new mouse review, and keeps
unrelated work intact. The standalone camera review is saved beside the mouse
file. `shared.camera.add_camera(..., optics=True)` now adds this single-frustum
reference to new complete camera instances; `optics='r01'` is for historical replay.
