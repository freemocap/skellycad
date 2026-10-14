# Rat skulls in the user's frame

Open [the corrected R02 skull-and-eyes review](rat-skulls-and-eyes-user-frame-r02.FCStd).
R02 revises eye placement in this frame: centers are `(0.75, -8.35, 0)` and
`(0.75, +8.35, 0)` mm, with equal outward/upward inclinations. This removes the
1.960 mm height difference inherited by the earlier coordinate transfer. The
user's origin defines the height and midline datum; bilateral symmetry is an
explicit placement assumption, not a measurement from the skull. Front and side
views were visually checked against the orbital openings. Fine anatomical fit
remains provisional. Eye geometry, colors, axes and all skull meshes are unchanged.
`eye-placement-r02.json` records the new poses; `../adjust-eyes-r02.FCMacro` rebuilds
them in a separate generated document from the retained R01 study. The original
[R01 transfer study](rat-skulls-and-eyes-user-frame-r01.FCStd) remains available.

The standard dense skull is visible initially. Expand **Skull alternatives**,
hide the visible mesh with Space, and show another to compare at the same pose.
Keep only one opaque skull visible at a time. Both eyes remain independent,
with their R02 colors and right-handed local frames.

## World frame

The unchanged user asset `../rat-skull-low-poly-aligned.stl` defines this frame:

- +X: toward the nose, rostral/anterior.
- +Y: the animal's left.
- +Z: upward through the skull roof, dorsal/superior.
- Origin: the user's approximate interocular midpoint. No extra recentering.

This distinguishes anatomical anterior (+X) from dorsal (+Z). The **eye-local**
frame still uses +Z through the cornea and +Y up. World XYZ and eye XYZ arrows
both use red/green/blue; their groups and labels identify which frame they show.

`alignment.json` stores the 4×4 source-to-aligned transform, inverse, source
hashes, frame description and validation. With column-vector coordinates:

```text
p_aligned = R * p_original + t

R ≈ [ 1          0          0         ]
    [ 0         -0.9931734 -0.1166475 ]
    [ 0          0.1166475 -0.9931734 ]

t ≈ (-0.2218240, 1.1658742, 6.0731593) mm
```

Use the full-precision JSON for computation. Coordinates are assumed mm,
consistent with prior work; STL itself contains no unit metadata.

## Assets and detail

| File | Triangles | Purpose |
| --- | ---: | --- |
| `rat-skull-low-poly-aligned-r01.stl` | 24,550 | Recovered transform applied to the original low-poly mesh; validation counterpart to the unchanged user anchor. |
| `rat-skull-standard-aligned-r01.stl` | 110,116 | Standard dense source, exact common transform. Default review mesh. |
| `rat-skull-high-res-aligned-r01.stl` | 102,342 | Source named high_res, exact common transform. |
| `rat-skull-high-res-refined-aligned-r01.stl` | 102,342 | Optional extra rigid overlap correction, followed by the same common transform. |

Every export retains the source's triangle order, count and per-triangle attribute
bytes. Vertex positions and normals are rigidly transformed. There is no scaling,
reflection, decimation, smoothing, hole filling or anatomical remodeling. Existing
suture geometry is retained to STL floating-point precision; no missing detail
is reconstructed. Filename and triangle count alone do not rank anatomical detail.

The standard mesh is watertight under the recorded check; low-poly and high_res
retain their original non-watertight topology. Registration does not repair them.
All originals and the user's anchor remain unchanged.

## Recovery and validation

The original low-poly and user-aligned meshes contain the same 24,550 triangles
in the same order. Their 73,650 corresponding triangle corners constrain a proper
rigid least-squares fit. The centering/SVD/determinant-correction method follows
the Kabsch formulation [@lawrenceBernalWitzgall2019].

The fit has RMS error **0.000000485 mm** and maximum error **0.000001765 mm**.
Fitting alternating faces and evaluating the other half also passes. These tiny
numbers measure file-to-file transformation agreement, not anatomical accuracy.
Applied scale is exactly 1; the diagnostic unconstrained scale is approximately
1.000000004. The rotation determinant is +1.

Serialized output checks cover inverse-transform vertex residuals, edge lengths,
triangle counts, STL attributes and unchanged topology. All point/edge differences
are below 0.000005 mm. This quantifies numerical preservation of the denser assets.

### Why the optional high_res correction exists

The supplied surfaces already differ before applying the common transform.
A separate fit of high_res to the standard source finds an approximately
`(+0.161, -0.731, -0.062)` mm translation and a very small rotation in the original
source frame. The optional file composes that correction **before** the common
transform. The exact common-transform export remains available for comparison.

This fit uses deterministic area-weighted samples, nearest-sample correspondences,
85% trimmed proper rigid updates and a 100-iteration cap; it converged in 54 steps.
Independent exact point-to-triangle checks on 512 surface samples per direction
show median distances improving from 0.231/0.279 mm to 0.102/0.097 mm.
The 95th-percentile distances improve from 0.640/0.798 mm to 0.448/0.124 mm.
The high-to-standard sampled maximum increases from 0.824 to 0.904 mm, so this
is an overall-overlap candidate, not a promise that every feature fits better.
The two surfaces are not identical. Distances are not full Hausdorff measurements
and the correction has not been validated against anatomical landmarks.
See `high-res-refinement.json` for both complete transforms and diagnostics.

## R01 eye transfer and previous work

Current R02 eye poses were read from the open FreeCAD study and retained in
`source-eye-placement.json`. Their centers and outward axes are transferred
through the original skull frame into this frame. The local Y axes are projected
toward world +Z to set roll without reflecting either eye. Their new transforms
are in `eye-placement.json`; both basis determinants are +1.

The transferred eye midpoint is approximately `(0.744, 0.370, -0.706)` mm,
about 1.09 mm from the user's origin. That is consistent with an approximate
origin and provisional eyeball placement. The origin is deliberately preserved;
the eyes are not forced to symmetry or recentered. This is a coordinate transfer,
not a new anatomical fit. Save subsequent manual adjustments as a new revision.

The selected monocular hardware checkpoint and earlier reference documents remain
unchanged. A future complete assembly can adopt this anatomy frame explicitly;
mixing its coordinates directly with the old hardware frame would be incorrect.

## Reproduce

From the repository root with the configured CAD tools environment:

```powershell
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/references/skull/align_to_user_frame.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/references/skull/refine_high_res.py
```

Both write into ignored `generated/eye-tracker/rat/skull-aligned-r01/`. Retained
assets here are not overwritten. Run `../review-aligned-r01.FCMacro` inside the
existing FreeCAD GUI to reproduce the native study from the retained assets.

Source: **Rat skull + mandible**, scienceminer, Thingiverse 469391. The supplied
license is **Creative Commons Attribution Share Alike**, with no version specified.
These are rigidly transformed derivatives of those meshes; retain their attribution
and supplied license. See `../thingiverse-469391/LICENSE.txt` and `../provenance.json`.
