# Place a camera relative to an animal eye

Use this workflow when moving an eye camera, changing its anatomical target,
or adapting an existing camera mount to another animal. The current seating example is [rat targeted R03](../../designs/eye-tracker/rat/targeted-r03/recipe.json).
The shared implementation is `designs/eye-tracker/shared/targeting`.

## Inputs and frames

Start from a hash-verified complete hardware assembly and a separately verified
anatomy checkpoint. Read the species `active-model.json` even when the requested
hardware revision is a newer review candidate. Record both identities. Keep
source checkpoints and matched parts intact.

The recipe specifies the anatomy eye object, its center in skull coordinates,
the rigid mount-to-skull transform, lens reference point, desired lens position,
rest orientation and ribbon limits. The target must match the eye object's
world-space origin. The rat eye origin is its geometric center; it is not the
pupil surface. Its +Z points out through the cornea. The camera's +Z points
along its optical axis toward the eye. These directions are not interchangeable.

All internal hardware fitting uses the original mount frame. Apply
`mount_to_skull` exactly once when composing the complete assembly. Rigid
transforms must have determinant +1 and unit scale. A mirrored species layout
needs an explicit hardware design; reflecting a physical camera is not a pose.

The current camera profile is the measured Pupil Core model, with a
32.85 × 4 mm ribbon and assumed 0.15 mm thickness. It uses three cylindrical
bend zones with oblique bend axes, preserving the sheet's neutral length and
width. This is a geometric route, not a force, strain or fatigue simulation.
Each zone has radius, signed angle, bend-axis angle and preceding gap. The
user's 7 mm rod observation supplies the 3.5 mm minimum inside radius.

## Fit and rebuild

1. Set the eye target and mount placement. Preserve baseplate dimensions when
   reusing the mouse plate. The tapered bottom intentionally overlaps the skull
   as stock for a later Boolean cut. Do not lift the whole mount merely to remove
   this overlap. Declare only `skull_mount_Baseplate` as `boolean_cut_stock` in
   `skull_contact_policy`; other hardware and the ribbon must clear the skull.
   Record seating as provisional until reviewed.
2. Set the lens position and rest orientation. The pose resolver aims camera +Z
   at the target while retaining the lens reference point. The lens reference
   is the measured model's nominal lens-face center, not a calibrated optical
   entrance pupil. Reject a zero stand-off or an ambiguous half-turn roll.
3. Move the sensor, cradle, clip and socket together using the resulting rigid
   pose delta. Preserve their mating clearances. Keep the main PCB, tray, cap
   and baseplate fixed in the mount frame.
4. Solve the ribbon with fixed endpoint positions and frames. If the pose is
   infeasible, use `search_pose.py` to propose a camera rest pose while maintaining
   aim at the eye. Review the proposal, then write its lens position, orientation
   and ribbon seed into a new recipe. Search output alone is not an accepted fit.
5. Regenerate the established rectangular arms between the unchanged tray roots
   and moved socket attachments. Preserve full terminal thickness and nominal
   engagement. The upper terminal must fit inside the collar's axial extent.
   Adjust handle lengths only within a recorded search; keep the accepted arm
   style. A failed loft, unattached arm or collision stops the build.
6. Validate the finite-thickness ribbon against every rigid fixture and camera
   component. Check the finished carrier again after junction finishing. Sampled
   collision planes guide the search; full-solid Booleans are the acceptance gate.
7. Compose the complete skull-frame assembly. Check the ray's forward distance
   and miss distance, solid validity, matched-part clearances and skull/eye
   interference. Inspect the optical side and arm junctions in FreeCAD. A valid
   union does not establish proper seating or physical strength.
8. Export the matched parts only after the geometric checks pass. Verify closed
   meshes without self-intersections. Record inherited interference separately
   from new interference. Keep the model labeled as a review candidate until
   physical fit is demonstrated. Freeze the native checkpoint and its hash after
   the final GUI save; save the recipe and validation beside it.

For a saved recipe, use the pinned FreeCAD Python runtime from
[development.md](../development.md):

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/shared/targeting/run.py designs/eye-tracker/rat/targeted-r03/recipe.json --out generated/eye-tracker/rat/targeted-r03
```

Use a new output directory for a new revision. The command rebuilds the saved
solution; it does not rerun pose search, alter a selected checkpoint, or open the
desktop application. Use the species revision's `open.FCMacro` through the
existing-window workflow for desktop review. Enable parent groups first, then
explicitly hide alternative skull meshes, carrier construction solids, and the
nominal lens reference. Save and audit leaf visibility: display one skull and
one finished carrier, without their overlapping construction copies. Run `test_poses.py` with the same
runtime after changes to pose math. Run `tools/cad/check_target_anatomy.py OUTPUT_DIRECTORY`
with `tools/cad/.venv/Scripts/python.exe` after the solid/mesh validation to check
sampled containment against the dense skull. Changes to dimensions require a new camera
profile; the present ribbon builder rejects unsupported dimensions.

## Evidence and limitations

Skull surface intersections and sampled containment checks are separate from
hardware fit checks. A retained mouse baseplate may intersect or stand off from
a rat skull even when the camera assembly is internally valid. Report those
findings explicitly; do not claim an anatomical mounting fit from an aimed ray.
The anatomical eye poses remain provisional unless measured on a specimen.

This workflow preserves the dense skull mesh and the independent eye frames.
It builds on the repository's existing measured camera, R08 mouse fixtures and
rat aligned-eye definitions; it introduces no new anatomical measurements.
