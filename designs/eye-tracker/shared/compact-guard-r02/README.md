# Direct outward lower guard

Mouse R13 and rat R09 revise the R12/R08 complete review assemblies. The lower
root turns outward along mount -X, perpendicular to its former +Z departure.
The external straight lead is zero; a 0.4 mm embedded transition joins the
plate to the curved body. Two cubic Bezier spans blend into the preserved
outer turn and socket terminal. Body dimensions remain 2.6 by 1.8 mm.

The camera, ribbon, optical axes, anatomy, upper support and matched fixtures
retain their geometry and placement. Source and selected checkpoint hashes
are verified before building. Previous checkpoints remain unchanged.

Run `build.py` with the species revision's `recipe.json` using the pinned
FreeCAD Python described in `docs/development.md`. Then run
`check_anatomy.py mouse` or `check_anatomy.py rat`. The build checks full-solid
clearance, positive root/socket engagement, protected interface material and
one valid carrier solid. Export requires a closed mesh without detected
self-intersections. Species validation records retain the actual results.

Copy the generated native document to its `-final.FCStd` review filename and
open the species `open.FCMacro` through the existing FreeCAD desktop pipe.
Save and capture the reviewed assembly before running `freeze.py` with the
species revision directory. Do not overwrite an open review copy.

These checks cover the modeled rest position. Motion, fatigue and physical
fit remain unverified; inherited assembly interferences remain recorded in
the source manifest. This is a review revision, not a print release.
The change uses the user's sketch and local geometry, with no new research.
