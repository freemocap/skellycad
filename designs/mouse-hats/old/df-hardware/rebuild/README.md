# Eye-tracker reconstruction

This workspace begins with inspection and provenance. No replacement hardware has been designed yet.

## Design history

The original single-arm design evolved in CAD and was exported as STEP. The user later split the camera arm into two roughly orthogonal arms using Blender curves, skin operations, and mesh editing. The user identifies **two-arm V5** as the latest design. Its physical print/test status has not yet been established in this conversation.

V5 is authoritative for the intended current shape. Earlier STEP files may help recover unchanged interfaces but must not supersede V5's arm changes. The reconstruction should expose useful parameters rather than reproduce every historical modeling operation.

## Verified baseline

The machine-readable reports under `baseline/` record the first inspection and source hashes. They are snapshots; regenerate current reports with the [CAD commands](../../tools/cad/README.md).

- V5: 8,092 triangles, six connected shells after exact-coordinate welding. Five shells are watertight with consistent winding. The sixth is an open patch of two triangles. This does not yet establish whether the shells overlap or how they correspond to functional parts.
- V5 bounds: approximately **27.649 × 50.185 × 22.672 raw file units**. STL does not encode units; millimeters are a hypothesis to confirm against hardware.
- Assembly 53 STEP: three valid solids and 43,959 faces. Imported bounds are approximately **39.610 × 26.281 × 57.911 mm**. It is in a different reference frame/configuration from V5; no alignment has been solved.
- The two `.blend` projects in this repository contain meshes, a camera, and an empty; no curve objects or skin modifiers were found. The editable V5 arm construction is not in those saved scenes.
- Native FreeCAD parameter changes, save/reopen, and STEP export/import passed on a separate test block. This verifies the environment, not the engineering suitability of a future arm.

## Next design session

1. Review the colored V5 shell views together and name the functional features.
2. Confirm units using one measured, identifiable hardware dimension.
3. Identify camera mounts and base interfaces to preserve. Align shared geometry with an explicit transform if STEP is useful.
4. Agree on arm controls: attachment locations, segment lengths, bend radii, cross-sections, taper, and camera orientation.
5. Rebuild and compare one component before attempting the complete assembly.

`references.json` records reference roles and coordinate policy. `generated/` contains disposable, reproducible artifacts. Keep approved future designs and parameters outside `generated/` so Git can track them.
