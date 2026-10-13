# Skull with embedded baseplate print

Actual-size, 1:1 skull and eyes with **only the current skull baseplate** attached.
The camera assembly attaches later. Source: hash-verified MH-T3-EYE-R03 checkpoint.
This is a separate print derivative, not a replacement for the current assembly.

## Files

**For Snapmaker Orca, use `MH-T3-EYE-R03-skull-Snapmaker-Orca.3mf`.**
This native project was reopened in installed Snapmaker Orca 2.4.0 and displays
four materials automatically. It retains the user's U1 printer, PLA and process
settings and assigns Skull=1 (red), Cornea=2 (black), Eyes=3 (white), Mount=4
(yellow), matching the four filaments configured in the project. Open as a
project to retain these assignments. It has not been sliced or sent to print.
The generic core 3MF files below are geometry/color interchange files and do not
automatically assign Orca filaments.

`assign_orca_filaments.py` reproduces the native file from the durable
`inputs/orca-source-project.3mf` snapshot. Only per-part names and extruder
assignments change; geometry, placements and project settings are byte-identical.

Exports: `generated/mouse-hats/skull-print/`

- `MH-T3-EYE-R03-skull-eyes-embedded-baseplate.stl`: one fused watertight shell.
- `MH-T3-EYE-R03-skull-eyes-four-colors-cornea-r02.3mf`: corrected corneal boundary, one assembly, four named material regions. The earlier unversioned filename is updated as a compatibility copy.
- `Skull.stl`, `Eyes.stl`, `PupilCornea.stl`, `Mount.stl`: aligned backup color parts.

The baseplate surface and attachment interface retain their source geometry.
Skull material inside the baseplate is removed from the skull color region.
Two 1.3 mm diameter connections join the floating eye meshes to nearby bone.
The black regions follow the smaller corneal spheroids up to the existing
32-vertex junction with the sclera. Two fitted oblate spheroids identify each
eye's surface patches: scleral semiaxes 1.5 / 1.5 / 1.26 mm and corneal semiaxes
0.75 / 0.75 / 0.63 mm. All original exterior triangles remain unchanged; the
color solids share an internal closing surface at the junction. This replaces
the earlier approximate camera-facing plane cut that extended onto the sclera.
These are modeled corneal boundaries, not pupil boundaries.

## Slicing

Import the 3MF as one assembly; map Skull / Eyes / PupilCornea / Mount to four
filaments (suggested ivory / white / black / cyan). Some slicers ignore standard
3MF display colors; named parts allow manual filament assignment. If importing
the four backup STLs, load them together as parts of one object and retain their
relative positions. Do not arrange or drop each part separately.

The model is upright, with its lowest point on the bed, approximately
24.00 × 12.35 × 20.05 mm. Keep 100% scale to preserve the mount interface.
Enable supports for the skull underside and overhangs. Suggested starting point
for PLA and a 0.4 mm nozzle: 0.12 mm layers, 3 walls, 15–20% infill, a 5 mm brim,
and tree/organic supports. Inspect the sliced supports beneath both eyes and
the lower skull before printing. Remove supports carefully around thin bone.

This is a geometry/material 3MF, not a sliced printer project: it contains no
machine profile, filament-slot mapping, support settings, or G-code. Physical
printability and the baseplate fit still need a test print.

## Reproduce and verify

1. Run `export_inputs.py` in pinned FreeCAD GUI to snapshot current source meshes.
2. Run `inspect_cornea.py` with the pinned Python to recover the two spheroids
   and record their face membership in `cornea-fit.json`, then run
   `tools/cad/.venv/Scripts/python.exe designs/mouse-hats/skull-print/build.py`.
3. Run `show.py` in pinned FreeCAD GUI for the saved four-color native preview.

Additional Python dependencies used: manifold3d 3.5.4, networkx 3.7, lxml 6.1.3.
`lineage.json` records source/checkpoint hashes. `settings.json` stores mm values.
`validation.json` records connected-shell, winding, overlap, volume and reopen
checks. Both STL and 3MF are reopened; the latter must contain four meshes in
one assembly with the same overall volume and bounds. Source files are preserved.

3MF packaging follows the [3MF Consortium Core specification](https://github.com/3MFConsortium/spec_core/blob/master/3MF%20Core%20Specification.md).
