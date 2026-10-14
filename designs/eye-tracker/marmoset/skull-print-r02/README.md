# Marmoset skull print R02

R02 replaces the rejected R01 workflow. It starts from the unchanged CT source,
preserves the original skull surface, and uses Boolean operations to add internal
material. This follows the successful approach in the rat's `skull-print-r02`.
The source remains in [references/skull](../references/skull/README.md), with
attribution and license [@marmosetCtFemale100; @zimmermannRollin2025Apparatus].

## Why R01 failed

R01's rectangular neck cut removed part of the posterior skull. Its voxelization,
decimation, and final vertex displacement created numerous small tunnels. Being
watertight did not make that topology useful for printing. Its section-based
internal fill also left ragged socket geometry and exposed artificial planes.

`check_defects.py` reproduces the rear-surface and topology failures in R01.
On 517 posterior source samples, R01 has a 2.036 mm 95th-percentile distance and
2.718 mm maximum distance from the original surface. Its Euler characteristic
is -2738, compared with -116 for the source after capping the truncated scan end.
For connected, closed, orientable surfaces, a more negative Euler characteristic
indicates more tunnels; this is useful here as a regression signal, not an
anatomical quality score.

## What R02 changes

- **Neck:** a curved ellipsoidal cutter removes the vertebrae. The only temporary
  source caps close the truncated neck scan; all cap vertices lie inside the
  cutter. The posterior skull is not cut with perpendicular axis planes.
- **Braincase:** rays from an interior seed locate the inner bone. A closed
  radial surface follows those measurements, with interpolated openings and
  a small overlap into the bone. Boolean union with the original retains the
  external scan surface. No R01 mesh is used as a geometry input.
- **Sockets:** local additive fill closes small holes and backs the socket walls.
  A 0.18 mm voxel envelope with a 1.2 mm closing radius generates this fill,
  restricted to curved masks around the sockets. It is united with the original
  mesh; the original orbital rims and walls are not subtracted or globally
  resampled. These are simplified print surfaces, not recovered anatomy.
- **Mesh size:** internal and detached shells are removed. The compact version
  uses tolerance-based simplification. Each candidate must survive STL export
  with the same Euler characteristic as the detailed model, one component,
  consistent winding, and watertightness. No forced 100,000-face budget or
  post-decimation vertex displacement is used.

The detailed output is `marmoset-skull-detailed-r02.stl`; the compact output is
`marmoset-skull-print-r02.stl`. Keep both with this record. R01 is retained only as
a rejected revision and regression input. Neither file changes a complete
assembly: the marmoset design still has no `active-model.json` or selected
hardware checkpoint.

## Coordinates and limitations

Source coordinates and scale 1.0 are retained. Millimetres remain an assumption
because STL has no unit metadata. X is lateral, +Y dorsal, +Z anterior by visual
inspection; left/right anatomical sign is unverified. The jaw remains in its
scanned pose. No hardware interface, anatomical target, or physical fit is set.

Socket backing and braincase fill deliberately change the internal anatomy. Openings in
the nasal region, jaw, and skull base remain; this is not a globally solid blob.
No global minimum wall-thickness guarantee or physical print test is claimed.
Review supports and layer previews in the intended slicer before printing.

## Reproduce and inspect

Use the CAD tooling Python environment documented in
[development.md](../../../../docs/development.md). Mesh package versions are
recorded in `requirements-mesh.txt`; Blender 5.2.2 generated the previews.
The source SHA-256 is verified before the build. Outputs
are regenerated under `generated/eye-tracker/marmoset/skull-print-r02/`, leaving
the saved revision assets untouched.

```powershell
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/marmoset/skull-print-r02/build.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/marmoset/skull-print-r02/validate.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b --python designs/eye-tracker/marmoset/skull-print-r02/render.py
```

Stop on any failed assertion. Validation checks the exported STL, posterior
surface loss, outer-vault error, three small-hole socket probes, preservation of
original bone after neck removal, and filled-braincase probes. It does not
substitute for visual review. Inspect the full-size front,
rear, oblique socket, and underside renders before accepting a revision.
Blender runs in the background and does not use the desktop FreeCAD session.
Render smoothing affects lighting only; the exported geometry is unchanged.

`check_defects.py` accepts a mesh path, so the rejected result remains testable:

```powershell
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/marmoset/skull-print-r02/check_defects.py designs/eye-tracker/marmoset/skull-print-r01/marmoset-skull-print-r01.stl
```

That command is expected to fail. Reproduction caches the source's largest mesh
component in the generated directory; the preserved ASCII source remains the
authoritative asset.

## Saved results and review

| Output | Triangles | Size (decimal MB) |
| --- | ---: | ---: |
| Detailed repaired mesh | 487,484 | 24.37 |
| Compact repaired mesh | 205,444 | 10.27 |

The compact mesh has 68% fewer triangles and is 91% smaller than the supplied
ASCII STL. Both exports have one connected, watertight, consistently oriented
surface and Euler characteristic -66. The compact export uses a 0.015 mm
simplification tolerance. A coarser candidate failed export validation and was
discarded.

The compact mesh's 1,250 sampled outer-vault points have a 0.014 mm
95th-percentile distance from the source. The detailed additive repairs remove
less than 0.000001 mm3 of the bone remaining after the neck cut (Boolean numerical
residual). These sampled and numerical checks are not a wall-thickness guarantee.
See [validation.json](validation.json) for hashes and measurements.

Front, rear, oblique socket, and underside renders were visually reviewed on
2026-10-14. The rectangular rear defect and perforated R01 surface are absent;
the socket backing is continuous across the tested small holes. Larger openings
and some scanned surface irregularity remain. See [preview.png](preview.png)
and the individual `r02-*.png` views. Slicing and physical printing have not
been validated. R02 is a new review candidate, not an accepted checkpoint.

## Attribution

Marmoset Brain Connectome / Neuroscientific Apparatus contributors;
Isabela Zimmermann Rollin and colleagues, *An open access resource for marmoset
neuroscientific apparatus*, Imaging Neuroscience 3 (2025),
DOI: 10.1162/imag_a_00483. This modified mesh uses **CC BY-NC-SA 4.0**.
Retain [LICENSE-source.txt](LICENSE-source.txt), source links, and this
modification record when redistributing it. The existing STL Git LFS rule covers
both revision meshes.
