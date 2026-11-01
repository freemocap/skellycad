# Pupil ribbon-camera optics R01

This review adds both camera frusta to the complete R08 ribbon-camera module and
to a copy of the complete mouse R19 assembly. **400 x 400 at 120 Hz is the primary
mode**, per the user's 2026-10-30 instruction. Both frusta are visible: orange for
400 and blue for 192. The 400-mode optics are a conditional Pupil Cam2 estimate;
the camera's hardware ID and individual calibration remain unconfirmed.

The physical camera selection remains `CAMERA-DUMMY-R08`; the mouse selection
remains `ET-MOUSE-RAISED-TARGET-R19`. This revision adds non-printing reference
geometry without changing either accepted checkpoint or its matched parts.

## Evidence and mode interpretation

On 2026-10-30, the user transcribed this Pupil Labs email excerpt:

> Image sensor size (at 192x192 pixel): 1,15 mm x 1,15 mm; Focal length: 1,7 mm

The original email, date, serial number and hardware model ID were not inspected.
The quoted values are treated as nominal active imaging dimensions for the 192
mode, not dimensions of the whole silicon package. Their provenance is preserved
in `parameters.json`. No public URL is asserted for this private correspondence.

Pupil Labs confirms both 192 x 192 at 200 fps and 400 x 400 at 120 fps for its
200 Hz eye camera [@pupilCore200Hz]. Frame rate and output pixel count alone do
not identify how the sensor is read:

- Cropping keeps a smaller sensor region. At fixed optics, that reduces coverage.
- Binning combines neighboring pixel values. If the same sensor region is used,
  coverage is preserved while the output resolution falls [@baslerBinning2026].
- Subsampling and resizing can also reduce output resolution. A combination of
  reduction and cropping is possible; the mode pair does not distinguish them.

Changing readout mode does not change the lens's physical focal length. The focal
length expressed in output pixels can change. Pupil's Cam2 defaults contain
`fx, fy = 282.976877, 283.561467` at 192 square and
`561.471804, 562.494105` at 400 square. The source says only focal lengths were
measured; centered principal points and zero distortion are placeholders
[@pupilCoreEyeIntrinsics2026].

These defaults imply nearly equal coverage, with the 400 mode about 5% wider in
linear coverage at a fixed distance. That is inconsistent with a simple
unscaled 192-pixel crop of the 400 image. Approximately twofold sampling reduction
plus a small crop is one plausible explanation, **not a verified hardware fact**.
Cam3 has substantially different focal-length defaults, so do not apply the Cam2
numbers universally. The email's 192-mode focal length in pixels, about 283.83,
is consistent with Cam2 but does not establish camera identity.

## Geometry and uncertainty

For a centered ideal pinhole model, the full angular field is
`2 * atan(active_sensor_dimension / (2 * focal_length))`. Equivalently, use
`2 * atan(image_dimension_px / (2 * focal_length_px))`
[@edmundFovR02; @opencvCalibR02].

| Reference | Horizontal FOV | Vertical FOV | Evidence |
| --- | --- | --- | --- |
| 192 mode, email dimensions | 37.37 degrees | 37.37 degrees | 1.15 mm square / 1.7 mm |
| 192 mode, Cam2 default | 37.48 degrees | 37.41 degrees | Family default, comparison only |
| 400 mode, primary display | 39.21 degrees | 39.15 degrees | Conditional Cam2 default |

The 400 calculation uses its pixel focal lengths directly. Combining those with
1.7 mm gives an *effective* imaging width of about 1.211 mm and height of 1.209 mm;
these are derived values, not independently measured silicon dimensions.

The model includes a 1.15 mm square sensor face at the inherited hypothetical
sensor datum, a 1.7 mm focal-length guide, and two wireframe viewing pyramids.
All reference objects have `ExportForPrinting = false` and remain outside
`camera.PhysicalParts`. The original optical axis and physical solids remain intact.

The drawing places its schematic projection center 1.7 mm forward of the sensor
datum, along the existing optical axis. This is a pinhole illustration, **not a
measurement of the entrance pupil, principal planes or sensor-to-lens spacing**.
The frustum's position and image roll remain provisional. Roll follows the R08
X axis for the flat camera and the existing lens's projected X axis for the mouse.
A direction alone cannot determine a square sensor's roll. Real lenses can have
distortion and focus-dependent projection; calibration is needed for accurate
image coverage [@edmundFovR02; @opencvCalibR02].

The 20 mm extent is a display limit. It specifies neither focus distance nor
depth of field. Occlusion by the mount, eyelids or skull is not removed from the
wireframe. For the nominal 192 geometry, coverage at 15 mm from the schematic
projection center is about 10.15 mm square. The conditional 400 estimate is
about 10.69 x 10.67 mm at the same distance.

## Build and review

Read `docs/development.md` first. Use the pinned FreeCAD Python runtime from the
repository root to build into `generated/eye-tracker/shared/optics-r01/`:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/shared/cameras/pupil-core-eye/optics-r01/build.py
```

The build verifies source hashes, sensor area, focal-guide length, frustum extent,
frame handedness, transformed whole-camera references, unchanged mouse geometry
and placements, and saved-file integrity and reopening. Success prints
`OPTICS_R01_OK` and writes `validation.json` with `passed: true`. These checks do
not establish optical calibration or physical fit. Stop if validation fails.

Send this directory's `open.FCMacro` through `tools/cad/open_in_running.py` with
the freshly verified desktop listener PID. It opens the saved mouse review by
verified hash, reuses an existing matching document, and leaves unrelated work
intact. The standalone camera review is saved beside it as
`PUPIL-CAMERA-OPTICS-R01.FCStd`.

For new complete camera instances, use
`shared.camera.add_camera(document, name='EyeCamera', placement=placement, optics=True)`.
Move the returned complete module as a unit. The optical overlay moves with it.
The default `optics=False` preserves historical callers.

To resolve the remaining uncertainty, confirm the camera name (Cam2 versus Cam3)
and compare a fixed scene in both modes without moving the camera. Matching
boundaries indicate matching coverage; different boundaries indicate a crop or
other field change. Calibrate each mode at the intended focus/working distance
for quantitative image projection. This image comparison alone cannot distinguish
binning from skipping or resampling.
