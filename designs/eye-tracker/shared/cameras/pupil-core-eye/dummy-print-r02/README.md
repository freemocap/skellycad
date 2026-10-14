# Camera dummy R02

R02 follows the user's direction to match the camera geometry. Use R02, not the
superseded thickened R01 handling prototype. The four-material 3MF contains one
camera in its straight configuration, with millimetre units and separate material
regions. For Snapmaker U1, open `CAMERA-DUMMY-R02-Snapmaker-U1.3mf` as a project.
It includes explicit tool assignments 1/2/3/4, red/black/white/yellow colors, and
a Generic TPU profile for tool 4. PLA profiles and the U1 0.4 mm machine profile
come from the existing repository Orca project. TPU settings come from the
installed Snapmaker Orca Generic TPU preset; they are not tuned to the actual spool.
The older `four-materials.3mf` has display colors only and requires manual tool
assignment in Orca. The U1 project fixes that packaging omission without changing
any mesh geometry. It has passed metadata and mesh comparison checks, but has
not been visually verified in Orca or sliced. No G-code is supplied.

## Geometry and materials

| Region | Suggested U1 tool | Material |
| --- | --- | --- |
| Main PCB and notched head board | 1 | Red PLA |
| Lens holder envelope | 2 | Black PLA |
| Detailed connector and two LEDs | 3 | White PLA |
| Ribbon | 4 | Yellow TPU |

The main board remains 30.85 × 9 × 0.25 mm. The head retains its 6 × 15 mm
outline, including the narrow neck. The ribbon remains 32.85 × 4 × 0.15 mm.
Plan dimensions come from the user-confirmed R02 measurement record; thicknesses
are inherited assumptions. Lens height, connector identity and registration remain
provisional. This matches the current camera model, not verified manufacturer CAD.
The nominal M4 display cylinder is omitted because it was a reference marker,
not a modeled stock lens.

The detailed R03 JST SH connector uses the KiCad contributors' model, licensed
CC-BY-SA 4.0 with the KiCad library exception
[@kicadConnectorModels; @kicadLibraryLicense]. The included source license applies
to that component. Connector cavities, leads and outer dimensions are preserved.

The only added solid geometry closes the inherited 0.012396 mm air gaps beneath
the lens holder and LEDs so those components contact the head board. Exterior
bounds and component positions are unchanged. Overlapping interface volumes are
assigned to one material, without changing the combined exterior. The entire
camera is translated together by (0, 31.2833457947, 0.25) mm for export. The main
board's underside is on the bed. No thickening, dovetail tabs, or enlarged connector
is used in R02. No mount, camera targeting recipe, or selected checkpoint changes.

## Slice and inspect

1. Open `CAMERA-DUMMY-R02-Snapmaker-U1.3mf` in Snapmaker Orca as a project.
   Verify the U1 0.4 mm printer preset. Keep it as one object containing four parts, at 100% scale.
   If importing the four STL alternatives, import them together as one multipart
   object. Do not drop individual parts to the bed or center them separately.
2. Assign the materials in the table to the corresponding loaded tools. Select
   the actual spool profiles, especially TPU for the yellow part. The U1 project
   includes preset temperatures and extrusion settings; verify these for your spool. Snapmaker lists
   U1 compatibility for TPU of at least 90A hardness; the actual yellow spool's
   hardness remains unspecified [@snapmakerU1Multimaterial2025].
3. Use a layer strategy that retains the 0.15 mm ribbon and 0.25 mm boards. Inspect
   actual sliced layers: the entire ribbon span must have continuous toolpaths,
   and neither board nor connector details may disappear. The source dimensions
   are deliberately not rounded up to suit a coarse layer profile.
4. Account for the ribbon underside at Z=0.175 mm, above the board underside.
   Printing the source assembly flat therefore requires support beneath the thin
   ribbon; the connector also contains overhangs. Inspect the chosen support
   material, contact layers, and removal access. Do not assume the ribbon is on
   the bed. A slicer setting that independently drops it changes the geometry.
5. Check material joins at both ribbon ends. R02 preserves the source contact
   geometry and adds no retention features; adhesion and survival during support
   removal require a physical trial. Snapmaker describes interlocking for weak
   material bonds, but enabling it changes internal interfaces and has not been
   validated for this thin ribbon [@snapmakerU1Multimaterial2025].
6. After printing, inspect ribbon continuity and joins before bending it. Compare
   board fit and ribbon routing with the real camera. PLA/TPU reproduces the
   rigid/flexible regions; equivalent bending stiffness is not established.

This is a geometry-validated print candidate. Slicing, support removal, material
bond strength, mechanical stiffness and physical mount fit remain unverified.
Preserving these thin source dimensions constrains print reliability; this pack
does not claim that a stock U1 profile will resolve every feature.

## Rebuild and validation

Run from the repository root, in order:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/shared/cameras/pupil-core-eye/dummy-print-r02/build.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/shared/cameras/pupil-core-eye/dummy-print-r02/package.py
```

Outputs are in `generated/eye-tracker/shared/camera-dummy-r02`. The native FCStd,
STEP, four material STLs and multipart 3MF share the same print frame.
`parameters.json` pins source assets and the selected mouse/rat checkpoint hashes.
The builder verifies these before generating geometry. The geometry report checks
valid solids, zero material overlap, combined connectivity, board outlines and
ribbon volume. The package report checks watertight volume meshes and reads back
the 3MF to check geometry volume, units and its four component references.

Review scope for the new external source: the text of Snapmaker's material
performance article was read for TPU hardness compatibility and its discussion
of mechanical interlocking. It does not establish the strength or printability
of this design. No physical print or manufacturer camera measurement is claimed.

Rebuild the U1 project after `package.py` by running `package_u1.py` with the CAD
tooling Python. `u1-project-validation.json` checks all four part-to-tool mappings,
colors, TPU type/temperature fields, machine identity, and unchanged mesh XML.
The original portable package fails the explicit-assignment check because it lacks
`Metadata/model_settings.config`; the U1 project passes.
