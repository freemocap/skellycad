# Rat R16 symmetric design derivative

R16 provides a symmetric skull for engineering layout, with the original R14
eye pair and optical axes. The original anatomical skull and accepted R12–R15
checkpoints remain preserved. This is an idealized derivative, not a measured
specimen or a newly registered atlas. The selected complete hardware assembly
is unchanged.

## Rigid correction first

The R15 whole-skull fitted reflection plane is rotated onto Y = 0 with a proper
rotation of 1.562309° and a translation of -0.183085 mm along Y. There is no
scale change. `validation.json` records the complete source-to-design transform;
its rotation determinant is +1. The original atlas origin becomes
(0, -0.183085, 0) mm, so the design origin must not be described as the unchanged
atlas bregma. X remains approximately anterior and Z approximately superior.

The rigid-only mesh is saved separately and available as a hidden comparison
in the native document. R15's residual reflection mismatch establishes that
rigid alignment alone does not create exact symmetry.

## Exact symmetric surface

Both left-half and right-half reflected reconstructions were evaluated after
the rigid correction. The right-half reconstruction had the smaller sum of
bidirectional mean squared surface distances on reproducible area samples and
was selected. It retains the aligned right half, cuts triangles at Y = 0,
reflects that half with corrected triangle winding, and merges seam vertices.
It does not smooth or warp thin bones. This changes the opposite side rather
than claiming a globally minimal non-rigid fit or biologically homologous
correspondence.

On 12,000 sampled points in each direction, the 95th-percentile surface distance
between rigid-only and symmetric meshes is approximately 0.196 mm in both
directions. The sampled maxima are 0.744 and 0.994 mm. These are surface distances,
not corresponding-vertex displacements or global Hausdorff bounds. The derivative
has exact paired vertex reflection within numerical tolerance (recorded maximum
0 mm). Face winding is consistent. Like the source, it is not watertight; this
is the anatomical design reference, not a solidified print export.

## Eyes, reference points and review

The symmetric R14 eye coordinates and optical directions are held fixed in the
new design frame to inspect the skull correction around the existing target.
This is an explicit design choice, not application of the skull transform to
the entire anatomical assembly. Both eyes show zero sampled radial bone
penetration using 232,980 nearby triangle samples per eye. That sampling is not
a continuous collision proof or validation of biological eye position.

Visible nasal, roof and arch reference pairs are recomputed on the derivative.
These geometric samples are not literature-labeled anatomical landmarks.
The front arch section uses X = 8 mm, Z = -10 mm; the other sections retain the
R15 sampling definitions. Hidden inherited source landmarks and original skull
objects remain in their historical R14 frame for provenance only. Do not use
their coordinates as new design-frame targets without the recorded transform
and, for surface points on the replaced half, a new surface association.

The default FreeCAD view shows only the symmetric skull and eye pair. To compare,
hide **SYMMETRIC DESIGN DERIVATIVE** and show **RIGID ONLY** using Space. Keep the
original source/checkpoint for anatomical comparison. Camera and baseplate
placement must be revalidated against this design frame in a subsequent complete
assembly revision.

## Rebuild

From the repository root, run
`tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/symmetric-design-r16/build.py`.
This verifies source and checkpoint hashes, exports both meshes, and records
the transform, checks and surface references. Then submit `open.FCMacro` through
`tools/cad/open_in_running.py --expected-pid <verified desktop PID>` as described
in `docs/development.md`. Submit `capture.FCMacro` after the view updates. The
frozen checkpoint identity is recorded in `review.json`.
