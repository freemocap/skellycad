# Rat reference R11: remove display spikes

The user visually accepted the R10 landmark placements on 2026-10-14. R11 preserves their coordinates and source-status distinctions, and records that review separately from anatomical validation.

The R10 display pipeline introduced severe edge stretching: the raw marching-cubes surface had a maximum edge of 0.106 mm; decimation alone produced 42 edges above 2 mm (maximum 2.678 mm); the saved smoothed display had 4,480 edges above 2 mm (maximum 7.442 mm). These comparisons isolate the large spike amplification to mesh smoothing after decimation. That display must not be used as a fitting target.

R11 returns to the same hash-verified image volumes and threshold. A small Gaussian filter (sigma 0.045 mm) acts on the scalar intensity volume before continuous-intensity surface extraction at 0.15 mm sampling. There is no mesh decimation or post-extraction smoothing. The resulting surface is closed, has 553,754 faces, and has no edge longer than 0.260 mm. This catches the observed long-edge failure; it does not establish anatomical accuracy of threshold segmentation. Thin structures and threshold sensitivity still need review. The source volumes, R10 checkpoint and accepted landmarks remain preserved.

## Working strategy

Use this corrected atlas as the anatomical coordinate reference. Keep the existing cleaner skull as a separate potential working/print surface. If using that surface, register corresponding cranial features to the atlas with a rigid transform first; test a single uniform scale separately only if supported by measurements. Exclude mandible and differently cropped anatomy from fitting. Inspect surface residuals around the orbits and baseplate, not just global RMS. An attractive mesh alone is not more anatomically accurate.

Do not fit a cleaner mesh to the distorted R10 display or force all local differences away by nonrigid warping. The corrected atlas may itself be adequate for anatomy review. In either case, retain a separate solidified printable derivative and estimate eye positions only after the skull frame and fitting quality are established. See docs/species-anatomy-workflow.md.

Run `build.py` with the CAD tools Python environment from the repository root; open `open.FCMacro` via the existing-window procedure in docs/development.md. Outputs are under generated/eye-tracker/rat/clean-reference-r11. Existing complete assemblies remain unchanged.
