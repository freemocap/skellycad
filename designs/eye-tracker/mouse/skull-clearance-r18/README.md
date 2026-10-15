# Surface-parallel raised baseplate — R18

R18 revises the R17 anatomical mount study. The baseplate mating face follows a fitted plane on the detailed skull, and the plate is raised 0.75 mm along that plane normal. The complete R16 camera assembly remains unchanged; this is a baseplate placement review.

## Surface alignment

Fit a plane to 525 dorsal ray hits over AP -3.5 to +2.5 mm and ML -2.5 to +2.5 mm in the accepted skull frame. The residual RMS is 0.125 mm. The skull is curved, so parallel means parallel to this local average plane. Its normal differs from the R17 landmark plane by 6.767 degrees. The baseplate face normal is aligned with the fitted normal; AP direction is projected into that plane to retain anatomical yaw.

The unraised datum retains R17 AP -0.5 mm and ML zero. Raising along the local surface normal introduces a small AP/ML displacement; exact final datum coordinates are recorded in `placement.json`. This explicit user-requested lift supersedes the usual instruction to preserve existing baseplate seating.

## Rear-hole clearance

The measured rear feature is the 2.9 mm diameter hole, face 35 in the extracted R16 baseplate, with axis approximately along assembly X. Its wall is highlighted orange in the CAD review. A full cylindrical envelope at this radius and axial extent is sampled with at most 0.1 mm spacing in both axial and circumferential directions. The nearest sample-to-atlas triangle distance is 5.143 mm. Subtracting a conservative 0.085 mm sampling allowance gives a 5.058 mm bound relative to this mesh, exceeding the requested 2 mm minimum. The corresponding sampled R17 clearance was 4.133 mm.

This bound addresses the existing hole envelope, including its lowest wall. It does not include an unspecified screw projecting beyond the hole, head, washer or tool-access envelope. Anatomical registration and actual specimen variation remain outside the numerical sampling bound.

## Footprint

The estimated atlas surface area lying inside the tapered base decreases from 81.474 to 71.736 mm2, approximately 12%. This compares triangle-centroid containment with area weighting; it is not an exact contact patch or cement area. The taper remains uncut source stock for later skull-surface fitting.

## Reproduce and review

Read `docs/development.md` before CAD execution. From the repository root, run `fit_surface.py` with the CAD tools Python environment, then `export_reference.py` with the pinned FreeCAD Python runtime, then `clearance.py` with the CAD tools environment. Existing detailed-reference STL from R02 is required. `build.FCMacro` verifies the R17 checkpoint and selected species checkpoint hashes, applies the saved transform and writes the generated review. Open it through the existing FreeCAD desktop pipe. Preserve the frozen native file listed in `review.json`.

No external anatomical measurements were added in this revision: the fit uses the already documented detailed atlas and accepted frame. Mesh clearance is not demonstrated physical fit. Integrating this placement into the complete camera assembly still requires matched-interface and camera-targeting checks.
