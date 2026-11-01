# Rat R12: existing skull in the atlas frame

The working skull is the existing refined high-resolution rat mesh. The atlas is a reference overlay only. The original assets, source volumes, accepted landmarks and previous checkpoints remain preserved. The complete camera assembly has not changed.

`open.FCMacro` opens a comparison with the existing skull in ivory and the atlas translucent cyan. Select **REFERENCE OVERLAY** and press Space to hide or show it. The other registered skull variants are hidden alternatives, not additional surfaces to display simultaneously.

## Registration

The fit is a proper rigid transform: scale 1.0, no reflection, no deformation. The same transform is applied to the existing high-resolution, refined, standard and low-poly meshes. It maps their established user frame into the atlas frame: X anterior, Y left, Z superior, origin at atlas bregma.

The deterministic fit uses dorsal height envelopes on a 0.5 mm XY grid, retaining the upper 8 mm and trimming the worst 15% of nearest-point correspondences. Nine translation seeds test nearby initial alignments. This emphasizes the skull roof and excludes much of the jaw; it is a surface-based registration, not a fit to independently identified homologous sutures. The SVD updates enforce a proper rotation. [@lawrenceBernalWitzgall2019]

Median roof nearest-point distance is 0.471 mm; the 90th and 95th percentiles are 1.221 and 1.911 mm. These are sampled vertex distances on the chosen envelope, not whole-skull accuracy or confidence intervals. Differences in specimen size, shape and completeness remain. There is no unsupported scaling to a presumed population median.

The unchanged atlas landmark positions have nearest-surface gaps on the registered working skull of 0.059 mm (bregma), 0.312 mm (lambda), 0.234 mm (nasion), 0.145 mm (left cheek arch) and 0.028 mm (right cheek arch). A small surface gap does not prove that a marker hits the homologous suture. Review the roof sutures, orbit/cheek-arch region and muzzle alignment before accepting the transform.

## Review and next use

The user accepted the anatomical point placements in R10. This separate rigid registration still awaits the requested visual confirmation. After acceptance, keep the existing skull as the working anatomy and hide the atlas from normal assembly views. Retain source links, license, hashes, this transform and residuals for provenance. The atlas can remain an optional comparison asset rather than a production model. No source files need deletion.

Eye positions and baseplate/camera fitting follow after registration acceptance; none are inferred from the low nearest-surface gaps alone. A future print derivative can fill the existing skull internally without changing the anatomical reference.

Run `register.py` with the CAD tools Python environment from the repository root; then open `open.FCMacro` using the existing FreeCAD session procedure in docs/development.md. `registration.json` records the transform and asset hashes; `landmarks.json` records preserved points and surface gaps.
