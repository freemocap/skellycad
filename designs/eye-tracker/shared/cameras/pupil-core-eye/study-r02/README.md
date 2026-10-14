# Measured camera study R02

Open `open.FCMacro` in the existing FreeCAD window. The study contains straight,
90-degree and 180-degree camera configurations, plus a separate group containing
two imported connector candidates. Select a ribbon and edit **BendDegrees** as
in R01. `camera_measured.py` builds native FreeCAD and static STEP outputs under
`generated/eye-tracker/shared/camera-study-r02/`.

## Confirmed measurements

The user measured the physical camera with calipers and confirmed this
transcription on 2026-10-13. `caliper-sketch.jpg` preserves the supplied drawing;
`measurements.json` records the dimensions and image hash. No measurement
uncertainty or tolerance was supplied: decimal precision is not a tolerance.

| Region | Dimensions in mm |
| --- | --- |
| Main PCB | 30.85 long x 9 wide |
| Free ribbon | 32.85 long x 4 wide |
| Lower camera head | 10 long x 6 wide |
| Neck | 2 long; 4 wide interpreted from sketch |
| LED section | 3 long x 6 wide |
| Full camera-head outline | 15 long x 6 wide, with neck notch |

R02 removes the source's small board/ribbon gaps by putting the measured region
boundaries together. The complete straight outline is 78.70 mm long, excluding
component overhang. The source Blender file remains unchanged. The connector,
lens enclosure and LED envelopes retain their source dimensions; their centers
move with the corrected boards. Board thickness (0.25 mm), ribbon thickness
(0.15 mm), component heights, exact optical axis and minimum bend radius remain
unmeasured. The camera head is treated as rigid for this study; the small neck
is not a second flexible segment.

The ribbon's neutral surface remains 32.85 mm long. At 90 degrees the neutral
radius is 20.913 mm; at 180 degrees it is 10.457 mm. These are route examples,
not physical bend limits. See the R01 note for the bending assumptions.

## Stock components

Two unmodified STEP files from the KiCad library are stored in
`connector-candidates/`, with original license text, source URLs and hashes
[@kicadConnectorModels; @kicadLibraryLicense]. They are community library models,
not manufacturer-certified dimensions or identified replacements:

- JST SH SM04B-SRSS-TB: four pins, 1.00 mm pitch, horizontal entry.
- JST GH SM04B-GHS-TB: four pins, 1.25 mm pitch, horizontal entry.

The four-pin count alone does not choose a model. Series, pitch and entry
direction must match. JST also lists separate top-entry GH models
[@jstGhCad]. The camera still uses its supplied connector envelope. The imported
candidates are shown beside the cameras and excluded from the camera STEP export.
They have not been scaled to make them fit. Measure between the first and fourth
contact centers and divide by three to estimate pitch; also compare the housing
keying and entry direction. Other series remain possible.

JST's official CAD portal requests personal details for email delivery and
restricts disclosure of downloaded documents; no form was submitted. KiCad is
the reusable model source chosen here. Retain its attribution and license if
redistributing the candidate collection.

**The exact lens holder has not been identified.** The user identifies M4;
R02 adds a 4 mm-diameter disk at the supplied holder's top as a nominal reference.
Its 0.15 mm display height is arbitrary, and it is not a stock lens model or
manufacturable threaded feature. The box beneath remains the Blender envelope.
An M4x0.35 miniature lens exists in the Towin catalog, but this does not establish
this camera's pitch, barrel height or holder dimensions [@towinM4LensExample].
A holder part number, barrel/holder height and thread pitch would allow an exact
replacement. No unrelated lens assembly has been substituted.

## Rebuild and validation

From the repository root, `prepare.py` regenerates the calibrated scene from the
R01 named meshes and the recorded caliper transcription. It preserves the source
component envelopes and applies separate corrections to the measured regions.
Run `open.FCMacro` for the editable GUI build, or run:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/shared/cameras/pupil-core-eye/study-r02/camera_measured.py
```

Success writes `validation.json` with `passed: true`: measured board extents,
valid ribbon solids at five bend angles, constant ribbon volume, endpoint
placement, candidate solid validity, and a valid 24-solid camera STEP export.
The three extra solids are the nominal M4 reference disks. The selected mouse
checkpoint hash was verified and its assembly remains unchanged.
