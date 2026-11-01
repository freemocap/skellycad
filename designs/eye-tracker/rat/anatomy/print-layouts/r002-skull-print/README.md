# Rat skull print revision R02

R02 fills the braincase while retaining the original scan surface. It replaces
R01's global smoothing with a Boolean union of the original skull and an inset
internal core. Use either of these files in `generated/eye-tracker/rat/skull-print-r02/`:

- **rat-skull-detailed-solid-r02.stl**: detailed skull with a filled braincase.
- **rat-skull-mandible-fused-r02.stl**: the same skull fused to the original jaw
  by two local bridges near the rear jaw joints.
- **rat-mandible-original-detail-r02.stl**: optional separate original-detail jaw.

`rat-skull-detailed-r02.FCStd` contains these three alternatives plus hidden
original and R01 reference meshes. The fused version is visible initially.
Hide it before showing a different alternative to avoid overlapping surfaces.
`comparison-r02.png` shows the original, R01, R02, fused version, and sections.

## What changed

The original skull and jaw are not voxelized, smoothed, or decimated. Only the
internal core uses a voxel representation: 0.15 mm pitch, an inward distance
threshold of 0.70 mm, an anterior cutoff at X = 3.5 mm, and 0.04 mm simplification
tolerance. Its starting envelope comes from the preserved R01 solid skull.
The original scan surface is restored by Boolean union with this inset core.
Independent inward-facing shells are removed to fill enclosed residual voids.
The source's 29 small disconnected fragments are omitted, as in R01.

The jaw retains its original pose. Two 2.2 mm diameter cylinders bridge gaps of
approximately 0.42 and 0.40 mm near the rear jaw joints. Each cylinder extends
0.8 mm beyond each selected surface point to overlap both parts. These are
artificial print connections, not anatomical structures. Their exact endpoints
are recorded in `validation.json`. No connection crosses the front mouth opening.

This revision does not globally thicken fine nasal anatomy, teeth, or arches.
It trades some of R01's small-feature reinforcement for original anatomical
detail. Fine sutures that exist in the source are retained on the sampled dorsal
surface; absent scan detail is not reconstructed.

## Evidence and limits

All three exported STLs reopen as one connected, watertight solid with consistent
winding and positive volume. The fused file is a Boolean union, not a collection
of touching or overlapping shells. The skull's bounds match its original main
component; the fused model's bounds match the original skull-and-jaw bounds.

A 0.35 mm XY grid casts vertical rays onto the original upper surface and selects
3,833 visible points with Z > 1 mm. All those points are within 0.001 mm of R02;
the maximum measured distance is approximately 0.00000012 mm. The same comparison
against R01 gave a median distance of 0.111 mm and a maximum of 0.456 mm.
This is a sampled surface comparison, not a proof of exact preservation of every
triangle, suture, or lateral/ventral feature. Boolean operations can subdivide
triangles without changing their surface. Cross-sections and previews were also
reviewed visually. All 45 recorded braincase probes lie inside solid material,
and both provisional eye-center probes remain outside.

Geometry validation does not establish demonstrated physical fit or print success.
No slicer profile or G-code is supplied. Import with millimetre units at 100% scale,
orient the model, and place it on the bed in your slicer. Inspect supports under
the teeth, arches, and jaw. The original alignment origin is retained, so these
STLs are not translated to bed height. Slicer infill controls plastic density
inside the filled braincase. The fused jaw is fixed, not articulated.

## Lineage and reproduction

Units are assumed millimetres, as in the source study; scale remains 1.0.
The coordinate frame remains +X nose, +Y left, +Z dorsal. The selected complete
assembly remains **ET-RAT-MONO-R01**, whose checkpoint hash is verified before
building. This separate print derivative does not replace that complete assembly
or change its matched hardware parts. R01 and supplied assets are preserved.
Input hashes, output hashes, bridge coordinates, and checks are in `validation.json`.

From the repository root, run with the CAD tools Python environment:

```powershell
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/skull-print-r02/build.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/skull-print-r02/validate_surface.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/skull-print-r02/preview.py
```

The preserved R01 STL must exist at the path pinned in `build.py` and match its
recorded hash. Commands regenerate R02 under `generated/`; stop if an assertion
fails. Dependencies are NumPy, trimesh, SciPy, scikit-image 0.26.0, manifold3d
3.5.4, rtree 1.4.1, and matplotlib. `native_review.py` uses the pinned FreeCAD
bundled Python in a hidden GUI, following the repository development workflow.

Design evidence consists of the local scan and generated geometry checks. No new
external research informed the core or bridge choices.

Source attribution: **Rat skull + mandible**, **scienceminer**, Thingiverse 469391,
https://www.thingiverse.com/thing:469391. The supplied license is **Creative Commons
Attribution Share Alike**, with no version specified. R02 is a modified derivative;
retain this attribution and `LICENSE-source.txt` when redistributing it.
