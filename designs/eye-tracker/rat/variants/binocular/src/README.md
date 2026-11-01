# Cameras lowered by 3 mm: R43

R43 lowers both lens datums by 3 mm in skull-world Z from the hash-verified R42
complete assembly. Their world X and Y coordinates remain fixed. Both cameras
are re-aimed at the existing eye centres and retain mirrored camera frames.
The main PCBs, central carrier stock, skull baseplate and anatomy stay fixed.
Dimensions are in millimetres.

The holders, clips and sockets move rigidly with their cameras. The ribbon
solver permits a common change in camera roll while preserving bilateral
symmetry. It uses the existing 32.85 by 4 by 0.25 mm ribbon model, with a 3.5 mm
minimum inside bend radius. This is a geometric ribbon fit, not a strain or
fatigue simulation.

Each camera retains two planar supports with perpendicular terminal approaches.
The top-arm search first tests the R42 root tangent projected into the updated
support plane, preserving the established attachment shape where possible.
Root and socket junctions are finished and checked again after refitting.
Broad concave bevels reinforce the upper attachments; the left bevel sits
beside its small corner fillet. The label is updated within its existing rail.

The historical species selector remains R01. Its stored hash does not match the
local historical file; it is not the geometry input for this revision. R42 is
the explicit, hash-verified source recorded in `recipe.json`.

## Build and review

Preserve existing output before rebuilding. Run `prepare.py` with tooling Python to verify the R42 source hash and seed a
fresh output directory with its native document and matched BREP inputs. The builders resume their saved working documents and records.

1. Run `search_pair.py` with tooling Python to solve the fixed lowering target.
2. Run `place.py` with pinned FreeCAD Python. It moves matched parts together,
   builds the ribbons, and checks their solid and eye-view clearances.
3. Run `candidates.py` with tooling Python, then `arms.py`, `finish.py`,
   `reinforce.py` and `label.py` with FreeCAD Python.
4. Run `check_label.py` with tooling Python, `validate.py` with FreeCAD Python,
   and `check_eyes.py` with tooling Python. Stop on any failed check.
5. After validation passes, run `open.FCMacro` in the existing FreeCAD session.
   It saves and closes obsolete task-owned documents and opens the complete
   matched assembly with the skull.
6. After the final GUI save, run `freeze.py` with FreeCAD Python. It verifies
   geometry and placements against the validated document before freezing the
   GUI-saved native file and updating its hash.

Native solid, mesh, ribbon, arm seating, camera-access, eye-view and anatomy
checks are separate from demonstrated physical fit. Eye-view checks use the
inherited padded lens-to-eye region, not a calibrated full-sensor field of view.
No new print pack is released by this revision.

The carrier mesh is validated in mount coordinates. `validation.json` records
its rigid `mesh_to_world` transform; the eye-containment check applies that
transform in double precision. Baking transformed vertices into a separate
world-coordinate mesh introduced a numerical intersection. The coordinate
study and rejected diagnostic meshes are retained in the generated outputs;
they are not print files.

## Review result

The final native geometry, fixed PCB and baseplate interfaces, 3 mm lens drop,
mirrored aiming, ribbon and eye-view clearance, arm seating, frame-aware mesh,
skull-crossing and sampled eye-containment checks passed. Physical fit remains
unverified. `review.json` identifies the complete assembly and its native hash.
