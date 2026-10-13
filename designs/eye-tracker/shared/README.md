# Shared hardware library

This folder now contains reusable hardware geometry and the assembly builder.
The first supported pairing is the inherited Pupil Core eye-camera fit profile
with the R10 printed mount.

| File or folder | Purpose |
| --- | --- |
| `cameras/pupil-core-eye-inherited/camera.json` | Approximate PCB envelope in its own local frame; exact camera revision is unconfirmed. |
| `mounts/r10-monocular/mount.json` | Compatible camera, matched geometry assets, internal PCB/holder placement and inherited clearances. |
| `mounts/r10-monocular/*.brep` | Exact native CAD geometry extracted from the accepted assembly. |
| `assembly.py` | Builds a complete assembly from a species recipe and any number of named camera instances. |
| `model.py` | Opens the selected saved checkpoint and exports its matched print groups. It does not design the geometry. |
| `validation.py` | Checks the mouse against R10 and checks interfaces before export. |
| `preview.py` | Creates the exploded hardware inspection document. This is not a printable arrangement. |
| `extract_r10.py`, `r10-extraction.json` | One-time extraction recipe and source/asset hashes. Normal builds do not run extraction. |

The carrier is rebuilt by fusing the extracted tray/mount region with the
support/socket region. The holder, cap and clip are the matched R10 shapes.
The PCB reference has a local origin at its minimum corner; the mount preset
places it. All geometry uses millimetres. Animal recipes specify rigid poses
as `translation_mm` and a normalized `rotation_xyzw` quaternion.

## What is reusable today

A recipe can reuse the pairing for multiple camera instances, each with its own
pose, role and baseplate reference. A preset declares which camera profiles it
fits; the builder rejects incompatible pairs. Changing one camera instance does
not change the others.

The R10 arm route and the holder's internal pose are frozen geometric presets,
not freely adjustable parametric sketches. To change them, create a revised
mount preset and validate its interfaces. Further extraction can make those
features parameter-driven when the rat design establishes the needed changes.
The current profile does not invent missing sensor, lens, ribbon or connector
measurements.

## Build interface

Inside the pinned FreeCAD GUI Python context, import `shared.assembly` with
`designs/eye-tracker/` on `sys.path`, then call:

```python
assembly = build_assembly(config_path, output_dir)
```

The result contains `document`, `manifest` and the resolved `config`. Fresh output
must be under root `generated/`. The species `build.py` is the usual entry point;
it also performs that design's comparison checks.
