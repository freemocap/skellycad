# Rat R04 print pack

R04 adds a permanent **RAT R04** label to the R03 carrier and provides connected
rat anatomy prints. R03's eye poses, camera pose, ribbon route, arm geometry and
matched interfaces are preserved. The selected R01 assembly is unchanged.

## Files

- `anatomy/rat-eyes.stl`: detailed rat skull and fixed jaw, both eyes, and a 2 mm
  diameter cylinder between eye centers.
- `anatomy/rat-eyes-embedded-baseplate.stl`: the same anatomy with the R03
  baseplate fused in its reviewed position.
- `anatomy/RAT-R04-Snapmaker-U1.3mf`: four parts with explicit Orca filament
  assignments and the existing mouse project's U1 0.4 mm nozzle profiles.
- `anatomy/RAT-R04-four-colors.3mf`: portable four-material geometry.
- `anatomy/Skull.stl`, `Sclera-and-bridge.stl`, `Cornea.stl`, `Baseplate.stl`:
  non-overlapping color regions in a common print frame. Import together as
  parts of one object. Do not drop or center the regions independently.
- `hardware/RAT-R04-carrier-and-holder.stl`: labeled carrier and matched holder
  in their common mating pose. Separate carrier and holder files are alternatives,
  not additional pieces to print with this file.
- `hardware/RAT-R04-cap.stl`, `RAT-R04-clip.stl`, `RAT-R04-baseplate.stl`:
  matched separate accessories. The standalone baseplate is optional when using
  the embedded-baseplate anatomy print.

All dimensions are millimetres; use 100% scale. The physical camera, lens and
ribbon are reference hardware and are not included as printable plastic parts.

## Four-color setup

| Region | Filament slot | Preview color |
| --- | --- | --- |
| Skull and fixed jaw | 1 | Red |
| Sclera and 2 mm bridge | 3 | White |
| Cornea | 2 | Black |
| Baseplate | 4 | Yellow |

Open the U1 3MF as a project. Check these part assignments and the actual loaded
spools before slicing. These are inherited printer/material/process settings,
not a new tuned print profile. No G-code or claimed successful print is supplied.
Inspect the sliced result, supports beneath the jaw, eye bridge and overhangs,
and the ball/socket clearance. Avoid supports that permanently lock the joint.
Keep the carrier and holder's relative pose when orienting that pair on the bed.

## Geometry and lineage

The skull uses the existing `skull-print-r02` derivative: original scan detail,
inset braincase fill, fixed-jaw bridges, and removal of the previously documented
small fragments. The new eye bridge has radius 1 mm, running from
(0.75, -8.35, 0) to (0.75, 8.35, 0) in the skull frame. It is an artificial print
connection assigned to the sclera material. Eye geometry and placement remain
schematic. All anatomy regions share one translation to bed height.

The embedded plate retains its R03 shape. Skull material is removed from the
plate's overlap for mutually exclusive colors; the single-color STL is their
Boolean union. This is an embedded mock-skull print, not a fitted plate for an
actual animal. A tiny enclosed cavity at the bridge/skull interface may remain;
it is not a detached printable fragment.

`hardware-validation.json` and `anatomy-validation.json` record checks and hashes.
The native assembly includes the label; the anatomy review document contains
only the four print regions. Geometry checks do not establish physical fit.

## Rebuild

From the repository root, run in order:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/rat/print-r04/export_cad.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/print-r04/validate_hardware.py
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/rat/print-r04/check_meshes.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/print-r04/build_anatomy.py
```

The scripts verify input checkpoint hashes and stop on failed checks. Outputs go
to `generated/eye-tracker/rat/print-r04`. Preserve the R03 checkpoint and detailed
skull R02 input. Use `open.FCMacro` through the existing-window workflow in
`docs/development.md` to inspect the anatomy regions. This revision uses local
geometry and the existing Orca project format; no new external research is used.

Skull attribution: **Rat skull + mandible**, **scienceminer**, Thingiverse 469391.
The supplied license states **Creative Commons Attribution Share Alike**, with
no version specified. Retain `LICENSE-source.txt` and this attribution with
redistributed scan derivatives.
