# Rat skull print revision R01

Use **rat-skull-solid-r01.stl** from `generated/eye-tracker/rat/skull-print-r01/`.
The braincase is filled, 29 small disconnected fragments are removed, and
submillimetre gaps and surface detail are softened. The lower jaw is supplied
separately as **rat-mandible-clean-r01.stl**. Each STL is one watertight solid.
The original scan, aligned references, and selected complete assembly are preserved.

## Geometry and lineage

Revision: **ET-RAT-SKULL-PRINT-R01**. The input is the standard aligned R01 skull,
SHA-256 `06216589919dd73774323e6c0ea934ed73d23e49015531a96a82c3f4ec515b1e`.
The selected complete assembly remains **ET-RAT-MONO-R01**; its checkpoint hash
is checked before the build. This independent anatomy derivative contains no
mounting hardware and does not select a new complete assembly.

Coordinates retain the user's aligned frame: +X nose, +Y left, +Z dorsal.
One coordinate unit is assumed to be one millimetre, as in the source study;
there is no rescaling. The skull output spans approximately 46.80 × 23.57 ×
18.32 mm. Mesh processing can move the surface locally; this is not an exact
anatomical reference or a validated mounting surface.

The build separates the two main connected components (skull and mandible)
from 29 fragments totaling approximately 6.99 mm³. It voxelizes each main part
at 0.15 mm, fills local coronal hulls inside a manually chosen braincase envelope,
closes gaps with a 0.45 mm radius, fills enclosed voids, and smooths the field
with a 0.65-voxel Gaussian. The isosurface threshold is 0.45; manifold
simplification uses 0.035 mm tolerance. These values are print-design choices,
not measured anatomical constraints. The envelope control points are in build.py.
The fill closes the posterior braincase opening and modifies its underside.
The large lateral orbital openings remain visible in the comparison preview.

The resulting skull has 116,044 triangles and the jaw has 33,868. Surface
smoothing and fragment removal simplify physical features; this is not a
lower-triangle-count version of the source scan. No minimum wall thickness
is guaranteed throughout the remaining arches, teeth, or nasal region.

## Validation and use

`validation.json` records input/output hashes, bounds, volumes, and topology
checks after reopening both STLs. Each has one connected component, consistent
winding, positive volume, and no boundary edges. Cross-sections were visually
reviewed. All 45 recorded braincase sample points lie inside the revised solid;
both provisional R02 eye centers remain outside. These point checks do not
establish complete eye-surface clearance, hardware fit, or demonstrated physical fit.

Import the skull STL with millimetre units at 100% scale. Orient and place it on
the bed in the slicer. The STL retains its alignment origin, not a bed-height
translation. Import the jaw separately only if you want to print it. The jaw
has no added snap joint or attachment feature. Inspect the sliced layer preview
and supports around the teeth, nasal region, and thin lateral arches before printing.
The filled braincase is a solid model region; the slicer's infill setting still
controls how much plastic is used inside it. No printer profile or G-code is supplied.

## Reproduce

From the repository root, use the CAD tools Python environment with trimesh,
NumPy, SciPy, scikit-image 0.26.0, manifold3d 3.5.4, and matplotlib available:

```powershell
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/skull-print-r01/build.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/skull-print-r01/validate_fill.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/skull-print-r01/preview.py
```

The commands regenerate this revision under `generated/`; stop if an assertion
fails. Retained source assets and accepted checkpoints are not overwritten.
Evidence for these changes is the local source mesh, its sections, and generated
validation results; no new external research informed the closure envelope.

Source attribution: **Rat skull + mandible**, **scienceminer**, Thingiverse
469391, https://www.thingiverse.com/thing:469391. The supplied license is
**Creative Commons Attribution Share Alike**, with no version specified.
This print revision modifies that mesh; retain this attribution and the supplied
`LICENSE-source.txt` with redistributed derivatives. The source license is preserved.
