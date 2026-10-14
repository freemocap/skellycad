# Mouse eyes in the accepted landmark frame — R04

This anatomy review places both adult eye envelopes in the skull frame accepted by the user on 2026-10-14. Original landmark coordinates remain unchanged. The English names are accepted CAD interpretations of source IDs; user acceptance does not establish an author-provided naming dictionary. The source atlas and landmarks are preserved in skull-landmarks-study-r01 [@maga2017MouseSkullAtlas; @magaMouseCTAtlasRepository].

## Placement recipe

The origin is landmark 13 (bregma). X points from landmark 16 (lambda) toward bregma. Y points left, using the averaged paired orbital references (9,8) and (11,10), orthogonalized against X. Z is X cross Y. `placement.json` stores this proper orthonormal basis in assembly coordinates.

The landmarks define the reference frame, but do not directly measure globe centers. For those centers, this study fits spheres to 21 manually interpreted outer-tissue points per eye across three orthogonal Digimouse cryosections. `tissue-rim-picks.json` preserves the picks. They are sparse, approximate local observations, not published landmarks or an expert segmentation. The Digimouse cranial surface is registered directly to the detailed atlas using a proper similarity transform, initialized from the previous study [@dogdas2007Digimouse; @uscDigimouseDownloads].

Only fitted centers are transferred. Adult eye shapes retain the previous 3.30 mm transverse diameter and 3.34 mm axial extent, including their corneal geometry [@henriksson2009MouseCornea; @schmucker2005MouseEye]. The source fitted radii (1.386 and 1.393 mm) do not replace those dimensions.

Optical +Z passes through the globe center and corneal apex. Nominal gaze uses 64 degrees lateral azimuth and 22 degrees elevation relative to the horizon at 29 degrees nose-down lambda–bregma pitch. The transformation removes head pitch to express gaze in the skull frame. These are posture-dependent adult mouse values, not a universal resting pose or a measured axis of this specimen [@oommenStahl2008MouseOrientation].

## Evidence and limits

Review scope: source landmarks and meshes, six orthogonal tissue views, sparse boundary picks, fitted cross-sections, and the previously reviewed orientation paper. Tissue views and the marked fit are in `generated/eye-tracker/mouse/landmark-eyes-r04/`. These local observations extend the source review already recorded in the bibliography.

The independent sampled cranial surface residual is 0.063 mm median and 0.246 mm at the 95th percentile. This describes surface alignment, not eye-center accuracy. Boundary-point radial RMS is 0.118 and 0.103 mm. Changing registration trimming moves centers by at most 0.057 and 0.040 mm; 150 trials of independent ±0.15 mm point perturbations move them by at most 0.127 and 0.132 mm. These are local sensitivity checks, not confidence intervals. Inter-specimen anatomy, manual boundary interpretation and posture remain additional uncertainties. The atlas is not an adult-male population median.

Relative to R13, centers move 0.489 and 0.621 mm; optical axes rotate 23.19 and 19.92 degrees. `validation.json` checks the coordinate frame, unit axes and closed positive-volume eye meshes. Complete-assembly surface checks are recorded in R14. Physical fit and specimen-specific anatomy are not demonstrated.

## Files and reproduction

`review.json` identifies the frozen anatomy checkpoint and its hash. `fit.py` recomputes placement from preserved source assets and the generated detailed reference; `plot_fit.py` produces the marked tissue comparison. `build.FCMacro` creates the anatomy review in the existing FreeCAD session. Read `docs/development.md` before running CAD commands. These scripts write into generated output, not accepted source checkpoints. The complete assembly is [R14](../landmark-eye-placement-r14/README.md).
