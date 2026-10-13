# Tapered baseplate / Print Test R02

R02 changes only the baseplate's lower exterior. The PCB carrier, holder,
clip and cap stay at the accepted R01 shapes. R01 is preserved.

The supplied `old/df-hardware/baseplate/tall_tapered_53n_baseplate.stl`
is compared with `tall_53n_baseplate.stl`: matching triangle order permits
rigid alignment of unchanged upper geometry. The bottom polygon was uniformly
scaled by approximately 0.57004 about its vertex-average center.
We use that footprint reduction on the reconstructed native baseplate.
We do NOT copy the entire legacy taper: our taper starts at the mounting-pocket
floor (Y = 1.5 mm) and ends at the existing bottom (Y = -5 mm), protecting
all geometry at/above that floor. No skull subtraction is included.

`baseplate_taper_features.py` exposes `BottomScale` (0.5–1). `settings.json`
records dimensions in mm. A ruled loft defines the exterior stock to retain;
the difference is removed from the accepted baseplate. Scale 1 recovers it.

Run `build.py` using the pinned FreeCAD Python, then `package_r02.py`.
Run `measure_reference.py` using tools/cad/.venv/Scripts/python.exe.
Outputs are under generated/mouse-hats/baseplate-taper and print-test/r02.

Validation: one valid solid; removed volume 161.56765 mm3; no added material;
no removed material in protected mount region; zero seated-carrier overlap.
Footprint area 67.483 -> 21.928 mm2. Fresh reopen, scale edits and restore pass.
The three other print STL files have identical hashes to R01. Physical fit,
strength, supports and joint release remain untested; see R02 PRINT-NOTES.
