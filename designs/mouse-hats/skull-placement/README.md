# Skull repair and eye-aim placement study

2026-10-11. User authorized importing the supplied skull/eyes, repairing geometry,
recovering the original Blender mount placement, and aiming the normal through
the marked flat holder region toward the pupil area. This is a geometric study,
not an established surgical placement or a manufacturing release. R11B remains
the selected carrier; no accepted part or supplied source was overwritten.

## Visible review

`generated/mouse-hats/skull-placement/skull-placement-study.FCStd` contains the
repaired ivory skull, unchanged blue eye meshes, cyan R11B, gold tapered baseplate,
purple aimed holder, gold clip, and red optical-axis proxy. Original holder/skull
and the eye connector are hidden comparison objects. This file is a static pose
snapshot; change `settings.json` and rerun `build_review.py` to update the datum.

## Mesh findings and repair

- Exact-weld audit: solid skull has one nonmanifold edge and an opposite-face
  duplicate fragment. Its main 15,544-triangle surface is closed but has eight
  non-neighbor triangle intersection pairs in Blender's BVH check.
- The eyes STL contains that same skull plus two eye shells and a connector.
  Closed individual shells do not make the combined overlapping mesh a Boolean
  solid. Keep eyes separate for alignment; connector is unnecessary for this study.
- Repair: Blender 5.2.2 voxel remesh at 0.04 mm, then 0.05-ratio decimation.
  Result: 84,560 triangles, one watertight shell, consistent winding, zero detected
  non-neighbor intersection pairs. Volume changes -0.00479%.
- 3,000 seeded samples on the repaired surface: distance to original surface
  median 0.000272 mm, 95th percentile 0.002606 mm, maximum 0.019445 mm.
  This is a one-way sampled measurement, not a global error bound. BVH excludes
  vertex-sharing face pairs; it is not a formal certificate of all possible defects.
- Use `skull-repaired-main.stl` for the repaired skull in original STL coordinates.
  Eyes remain `solid_w_eyes-1.stl` and `solid_w_eyes-2.stl`; never union implicitly.

## Placement and aiming

The skull transform is recovered from `tall_mount_w_skull.blend`, then the scene's
baseplate is rigidly registered to the native uncut baseplate. No scaling. Median
nearest-vertex residual 0.01055 mm; 85th percentile 0.03248 mm; maximum 3.01 mm
reflects differing base geometry. Original scene skull coordinates agree with
the STL transform within 0.0000006 mm. Placement remains provisional: no skull
subtraction or surgical-depth adjustment was made to the current tapered baseplate.

The sensor/lens datum approximates the center of the user's marked flat plate.
Its normal is rotated about the existing ball center to a point on the eye surface
facing the lens. The eye meshes do not establish a verified pupil landmark. The
gold target is a pupil-area proxy and needs visual adjustment/confirmation.

Current candidate rotates 20.41885 degrees and aims exactly at that proxy within
numerical precision. Holder/carrier Boolean contact is 0.0024977 mm3: this pose
is not clearance-approved. The socket and arms have not been reoriented; a true
neutral joint redesign and motion/clip/ribbon/skull-clearance checks remain work
after placement and target review. This is not a finished print candidate.

## Replay and records

Use the pinned `tools/cad/.venv/Scripts/python.exe` for `audit.py`, `register.py`,
and `verify_repair.py`. Run `inspect_blender.py`, `check_intersections.py`, and
`repair_blender.py` in pinned Blender background mode. `register.py` additionally
needs `native-baseplate.json`, exported from BaseplateRebuild58.Baseplate using
Shape.tessellate(0.02), with vertices and faces. Run `build_review.py` synchronously
in the pinned FreeCAD GUI. It opens saved source shapes if their documents are
absent; snapshots do not rebuild their custom parametric dependencies.

Order: scene inspection / native export → audit → registration → intersection
check → repair → repair verification → build review. Parameters and measured
reports are preserved here; intermediate meshes and review output are disposable
under `generated/mouse-hats/skull-placement`. Supplied input files remain intact.
