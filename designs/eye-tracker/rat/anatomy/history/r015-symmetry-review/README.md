# Rat R15 symmetry review

R15 preserves the R14 skull and eyes and adds ten surface references, pair
connections, current/fitted midline guides, and a hidden reflected skull overlay.
No anatomical mesh, eye transform, atlas datum or selected assembly is changed.

## New surface references

Orange points identify left/right rostral nasal-tip candidates: the most anterior
mesh vertices on each side within X > 25 mm, Z > -9 mm, |Y| < 3 mm.
Green points are first downward surface intersections at X = 22, Y = ±2 mm
(nasal roof), and X = -8, Y = ±5 mm (rear roof). Purple points are first
outside-in lateral intersections at X = 12 and -3 mm, Z = -10 mm (front/rear
arch sections). Units and directions remain the R12 atlas frame.

These are reproducible geometric reference points selected on our working mesh,
not published homologous anatomical landmarks. Roof-pair Y midpoints equal zero
by construction and therefore do not establish symmetry; their height differences
are the relevant comparison. Nasal-tip extrema can be sensitive to triangulation.

## Measured comparison

The working skull was sampled by triangle area (40,000 points, seed 15).
A robust least-squares fit varied a reflection plane's normal and offset to
reduce reflected-point nearest-neighbor distances to the original vertices and
samples. A separate dorsal-only fit tests dependence on the selected region.

| Fit region | Plane tilt from current Y normal | Plane offset from origin | Median mismatch before / after | 95th percentile before / after |
| --- | ---: | ---: | ---: | ---: |
| Whole skull | 1.562° | 0.183 mm | 0.206 / 0.171 mm | 0.556 / 0.343 mm |
| Dorsal subset | 1.000° | 0.154 mm | 0.175 / 0.156 mm | 0.355 / 0.330 mm |

The whole-skull fitted plane is
`0.012504 X + 0.999628 Y - 0.024228 Z = 0.183085 mm`.
It is a geometric candidate, not a replacement for the source atlas plane.
Nearest-neighbor point sampling has a nonzero resolution floor; remaining
distances combine mesh detail, damage, sampling and possible anatomical
asymmetry. They do not prove biological asymmetry or registration accuracy.

Across the current plane, the front arch pair differs by 0.551 mm in lateral
reflection, the rear arch pair by 0.084 mm, and the nasal roof heights by
0.597 mm. The nasal-tip pair midpoint is Y = -0.113 mm. These comparisons support
reviewing a small rigid alignment correction before deforming the skull. They
do not establish that all apparent orbital mismatch comes from alignment:
R14 eye centers remain approximate, and the mesh itself has residual mismatch.

## Review in FreeCAD

Open the checkpoint recorded in `review.json` using the existing desktop
FreeCAD session. Orange labels identify the nasal tips; green labels identify
roof samples; purple labels identify the arch sections. Red is the current
midline and green is the fitted-plane dorsal guide. The guides are at Z = 2 mm
for visibility; they are not surface sutures.

Select **MIRROR about fitted plane - Space to compare** in the model tree and
press Space to toggle the cyan reflected overlay. Full plane outlines are
available, initially hidden, in **Current midline (red) and best-fit plane
(green)**. Earlier landmark annotations are hidden to reduce clutter; their
coordinates remain in the document. Eyes and axes retain their R14 positions.

For a reproducible rebuild, run `prepare.py` with the CAD tooling Python from
the repository root, then submit `open.FCMacro` through `open_in_running.py`
with the verified desktop PID. Submit `capture.FCMacro` after the display updates.
The preparation verifies the selected complete assembly and R14 checkpoint
hashes. `audit.json` stores the source hash, methods, points and fit results.

If a symmetric design mesh is wanted after this review, create a separately
named idealized derivative, retain the original mesh and transform lineage,
and revalidate the eye locations and hardware. Do not relabel that derivative
as a measured anatomical specimen.
