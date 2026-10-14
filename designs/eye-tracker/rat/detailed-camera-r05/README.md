# Rat with detailed Pupil Labs camera

This complete assembly revision replaces the earlier simplified camera with the
selected CAMERA-DUMMY-R08 rigid components: notched lens holder, fake lens,
JST connector, LEDs and PCB material regions. The optical axis uses the selected
camera datum and the existing sensor pose. The original checkpoints are preserved.

`recipe.json` pins the input assembly, camera selection and ribbon parameters.
The mouse source is its R08 complete assembly; the rat source is its R04 labeled
complete assembly, retained under `inputs` for replay. Both species retain their
original selected R01 baselines. This revision is a geometry review candidate.

The PCB poses, anatomy, carrier, holder, cap, clip, baseplate and arm seating stay
fixed. The ribbon uses the established three cylindrical bend zones at fixed
endpoint frames. Its 32.85 by 4 mm reference surface is the PCB top surface;
0.25 mm thickness extends below it to keep the end faces flush with the boards.
The geometric surface metric is checked; physical strain is not simulated.

## Review and limitations

`validation.json` records new and inherited interference separately. The larger
lens base reveals about 2.04 mm3 of interference with the existing holder.
The thicker ribbon also requires a clearance review against the finished carrier.
These are fit issues for a subsequent hardware revision, not clearance-certified
print models. The camera has not been reduced or cut away to hide interference.
No new print pack is released from this revision.

Use `open.FCMacro` through the existing FreeCAD window workflow in
[development](../../../../docs/development.md). It shows the detailed camera,
cyan optical axis and a translucent holder so the interface can be inspected.

From the repository root, rebuild with pinned FreeCAD Python:

```powershell
.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/shared/targeting/replace_camera.py designs/eye-tracker/rat/detailed-camera-r05/recipe.json
```

Outputs go to `generated/eye-tracker/rat/detailed-camera-r05`. Check `validation.json`, then
run `check_detailed_anatomy.py` with FreeCAD Python and
`check_detailed_containment.py` with the CAD tooling Python, both in
`designs/eye-tracker/shared/targeting`, passing that output directory. Surface
intersection and sampled containment are separate checks. The saved review
manifest and native checkpoint preserve the inspected result.
