# Camera clip reconstruction

Baseline: 58nassembly.step, RightCamClip (1). Source geometry and assembly frame
are documented by checks/prepare_clip58.py and its generated measurement report.

## Stage 1 — base loft

parameters.json preserves measured underside and floor corner coordinates in mm.
These are parity controls, not inferred nominal dimensions. build_base.py creates
two fully constrained four-sided sketches and a ruled PartDesign additive loft.
Dimensions.BaseThickness controls the floor elevation, initially 1.5 mm. Changing
it holds both profile footprints fixed, so it also changes side slope.

The reference floor sits at z=1.5 mm. Its full lower slab (including material
under the future walls) was extracted by intersecting the reference with a slab.
Removing split coplanar faces yielded the four-corner top footprint saved in JSON.
No rounded dimensions or parallel-side assumptions were introduced.

Validation: one valid rebuilt solid; both sketches fully constrained; source slab
minus rebuild and rebuild minus source slab each reported 0 mm3 by FreeCAD Boolean
operations. Recomputed at 1.6 mm thickness, verified height and validity, then
restored 1.5 mm. This verifies the base only, not whole-clip parity or physical fit.

Output: generated/mouse-hats/reconstruction/camera-clip/02-base-loft.FCStd.
The cyan base is at local origin. The purple unchanged source is offset 12 mm
along X for viewing. base-validation.json records the checks. Source-reference
geometry is not an input to the native loft; its sketches and dimensions persist
in the saved document. JSON is build input, not automatically synced with UI edits.

## Stage 2 — complete clip

finish_clip.py adds LeftRetainingWall and RightRetainingWall as native ruled
additive lofts. Each uses two fully constrained seven-corner sketches describing
the wall, inward lip and lead-in slope. LeftCrown and RightCrown preserve the tiny
regions where the source front changes plane. These overlap existing wall
material and add only the small crown regions. No imported source solid is used
as a modeling feature or hidden Boolean replacement.

measure_walls.py derives the profiles from the pinned source's planar equations,
then writes wall_parameters.json. The source face IDs in that measurement script
are revision-specific; the finished model uses stored sketches and expressions,
not those source face IDs. Both base and wall JSON files use millimetres.

Full result: generated/mouse-hats/reconstruction/camera-clip/03-complete-clip.FCStd.
Cyan is the rebuilt clip at local origin; pink is the source with a display-only
12 mm X offset. complete-validation.json records one valid solid, zero measured
Boolean excess/missing volume, fully constrained sketches and successful
BaseThickness edits from 1.5 to 1.6 and back to 1.5 mm. A separate pinned-runtime
process reopened the saved file and repeated the edit without executing build
scripts. The final model has 29 faces versus 18 in the source, due to feature
boundaries and numerical plane differences; refinement did not remove them.
This is geometry parity with editable native history, not a demonstrated
reduction in geometric complexity or proof of physical fit.

Dimensions.BaseThickness moves both walls and crowns with the floor while
retaining their measured profiles. Other dimensions currently live as named
corner-coordinate constraints in the sketches. A smaller set of nominal controls
for wall thickness, lip reach and clearance would require an explicit design
simplification; these have not been substituted for measured geometry.

To reproduce in the existing pinned FreeCAD GUI: open the 58 reference and run
checks/prepare_clip58.py main() to prepare CameraClipStudy58 (or open its saved
checkpoint with that document name). Run build_base.py main(), then finish_clip.py
main(). Measurement JSON is checked in as source input; regenerate it only when
intentionally changing source data. Builders reject existing output checkpoints
and conflicting documents rather than overwriting them.
