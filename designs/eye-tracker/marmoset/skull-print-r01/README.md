# Marmoset skull print R01

**Rejected in user review on 2026-10-14. Do not use this revision for printing.**
The rectangular neck cut removes part of the rear skull, the global remesh and
decimation introduce porous topology, and the socket interiors remain ragged.
The earlier watertightness checks did not establish acceptable geometry.
This directory is retained as a failed revision record; use the subsequent
revision's review notes and assets instead.

`marmoset-skull-print-r01.stl` is a separate, simplified print derivative of the
[preserved CT scan](../references/skull/README.md). It retains the skull and jaw,
removes the neck vertebrae and six disconnected pieces, and fills the braincase.
The source is credited to Marmoset Brain Connectome / Neuroscientific Apparatus
contributors and Zimmermann Rollin and colleagues
[@marmosetCtFemale100; @zimmermannRollin2025Apparatus].

## Geometry choices

The source's largest component contains the skull, jaw, and attached cervical
geometry. The six smaller components are omitted. After voxelization at 0.15 mm,
a local cut removes material where Y < 18 mm and Z < 0 mm. This cut was chosen
from the scan sections to remove the neck while preserving the posterior skull;
it is an artificial print boundary.

A 0.30 mm morphological closing radius seals small gaps. Enclosed voids are
filled. Local convex section envelopes fill the posterior braincase, with the
minimum Y raised towards the anterior end to keep the eye sockets open.
The exact section coordinates are recorded in `validation.json`. These are
specimen-specific print choices, not anatomical measurements or a general
marmoset recipe. The largest connected solid and its outer shell are retained.

The voxel field is smoothed at sigma 1 voxel and reconstructed at level 0.43.
A preliminary 0.08 mm simplification is followed by quadric decimation targeting
100,000 triangles. Collapsed topology is normalized with Manifold. A final
0.005 mm displacement along vertex normals separates coincident surfaces before
STL export. Detached slivers produced by decimation are removed from the final
mesh. The 0.08 mm setting is **not** a bound on the complete pipeline's
surface deviation; sampled measurements are in the validation report.

These operations soften fine features and replace internal anatomy with solid
material. The original exterior is approximated, not preserved triangle for
triangle. The jaw remains in its scanned pose as part of the connected print;
it is not a separate articulated part. Slicer infill controls plastic density
inside the filled braincase.

## Units, lineage, and validation

| Property | Original scan | Print R01 |
| --- | ---: | ---: |
| Triangles | 640,726 | 92,158 |
| File size (decimal MB) | 114.64 (ASCII STL) | 4.61 (binary STL) |
| Connected components | 7 | 1 |
| Watertight | No | Yes |

Triangle count is reduced by 85.6%; file size by 96.0%. File-size reduction also
reflects binary rather than ASCII encoding. On the sampled exterior regions,
median deviation is 0.068–0.118 mm. The 95th percentile is 0.133–0.482 mm and the
largest sampled deviation is 0.968 mm. These samples cover the face, dorsal vault,
and lateral vault; they exclude the intentional neck cut and internal fill.
Five braincase probes are solid, two eye-socket probes remain empty, and two neck
probes are empty. Visual review confirmed the skull/jaw silhouette, open orbits,
removed neck, and filled central braincase in the comparison views.

Revision identifier: **ET-MARMOSET-SKULL-PRINT-R01**. No complete marmoset assembly
or `active-model.json` exists, so there is no selected checkpoint or hardware
interface to change. This derivative must not be substituted for the original
anatomy in future fitting work without reviewing its modifications.

Coordinates and scale 1.0 are retained. Units are provisionally millimetres;
the STL itself has no unit metadata. X is lateral, +Y dorsal, and +Z anterior by
visual inspection; left/right sign and anatomical registration remain unverified.

`validation.json` records input/output hashes, component counts, geometry checks,
parameters, package versions, and sampled distances to the original exterior.
The exported file must reopen as one watertight component with consistent winding
and positive volume. It must also pass Manifold's mesh constructor. Probe checks
cover the filled braincase, open eye sockets, and removed neck region. These
checks do not prove freedom from every self-intersection or minimum wall thickness.
`comparison.png` shows exterior views and central sections; its display rotation
does not affect the STL coordinates. The source-only rendering is reduced to
100,000 triangles for display; measurements use the full original source mesh.

No physical print, slicer trial, or physical-fit validation has been performed.
The fine arches and teeth still need support and printer-specific review.
Import using millimetres at 100% scale, choose orientation, place the model on
the bed, and inspect the layer preview before printing. No G-code is provided.

## Reproduce and review

From the repository root, use the existing CAD tooling environment. Required
package versions are recorded in `validation.json`; `requirements-extra.txt`
records the mesh-processing packages in addition to the base CAD environment.

1. Run the build. It verifies the preserved source hash before geometry work and
   writes regenerated outputs to `generated/eye-tracker/marmoset/skull-print-r01/`.
   Stop if any assertion fails.

   ```powershell
   & tools/cad/.venv/Scripts/python.exe designs/eye-tracker/marmoset/skull-print-r01/build.py
   ```

2. Run the exported-mesh and surface checks and render the comparison.

   ```powershell
   & tools/cad/.venv/Scripts/python.exe designs/eye-tracker/marmoset/skull-print-r01/validate_preview.py
   ```

3. Inspect `comparison.png` and `validation.json` in that generated directory.
   The saved STL beside this README is the reviewed R01 output, covered by the
   repository's existing STL Git LFS rule. Reproduction does not overwrite it.
   Put later geometry revisions in a new revision directory.

`inspect_source.py` optionally regenerates source-only views. Geometry choices
derive from local mesh inspection; the cited paper supplies provenance, not
these reconstruction parameters.

## License

The source and modified mesh use **CC BY-NC-SA 4.0**. Retain
[LICENSE-source.txt](LICENSE-source.txt), the source links, author attribution,
and this modification record when redistributing the mesh. The paper's own
CC BY 4.0 license is separate from the repository's asset license.
