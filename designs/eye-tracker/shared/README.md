# Shared hardware library

**Preferred Pupil Labs eye camera:** [selected complete R08 module](cameras/pupil-core-eye/README.md), including the notched lens, optical axis and flush TPU ribbon. Use it for new camera geometry; historical species checkpoints remain pinned.

For camera-to-eye placement and ribbon/support refitting, see [the targeting workflow](../../../docs/eye-tracker-targeting.md) and the recipe-driven implementation in `targeting/`. The first complete example is rat targeted R02.


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
must be under root `generated/`. The species `build.py` is the usual entry point.
The mouse entry point also compares against R10; `tools/cad/validate_rat.py`
checks the rat build against the selected mouse hardware and supplied rat mesh.

Anatomy can supply `eye_target_label` and `eye_target_status` so an estimated
orbital target is distinguished from an inherited mouse target. Source mesh
labels are preserved. Optional `source_attribution` and `source_url` identify
third-party anatomy in the complete document. The manifest's `label` restores
the design name when FreeCAD would otherwise display its checkpoint filename.

## Detailed camera and flexible ribbon study

The [Pupil Core geometry study](cameras/pupil-core-eye/study-r01/README.md)
converts the supplied named Blender parts into CAD solids and demonstrates
constant-length ribbon bending with a rigid camera head. Its macro opens three
editable configurations. Scale and thickness remain provisional; this study does
not replace the accepted mouse/rat hardware or certify a minimum bend radius.
The original `pupil-core-eye-inherited` profile remains available to existing recipes.

The [measured R02 camera study](cameras/pupil-core-eye/study-r02/README.md)
supersedes the provisional plan dimensions with user-confirmed caliper values.
It also includes two imported KiCad connector STEP candidates for identification.
Thickness and exact component identities remain open; accepted species assemblies
still use their existing fit profile.
