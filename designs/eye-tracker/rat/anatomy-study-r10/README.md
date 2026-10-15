# Rat anatomy study R10

Start with `open.FCMacro` in the existing FreeCAD session. This review contains the Ratlas-LH skull in millimeters, a bregma coordinate frame and named landmark candidates. The old skull and two threshold alternatives are hidden comparison objects. This is the anatomical review stage, not a replacement complete assembly or print release.

## What to review

- **Red: Bregma** is the published atlas origin, kept exactly at (0, 0, 0).
- **Amber: Lambda and nasion** are local surface-snapped estimates. They are not official author annotations. Confirm the intended sutures, or identify where the candidates should move.
- **Blue: lateral cheek-arch extremes** are geometric points from an orbital-region crop, proposed as bilateral reference features. They are not globe centers.

Review whether the visible features and English labels agree. Visual acceptance establishes a useful local modeling reference, not biological validation of a population template. No eye center, baseplate or camera has been moved in this stage.

## Source choice and audit

Ratlas-LH combines an adult male Lister hooded brain template and skull CT in a published bregma-based frame. It provides an anatomical average rather than a species median. The average skull can obscure sutures, especially lambda. [@prior2021Ratlas]

The downloaded combined and brain-only NIfTI volumes share a 0.075 mm grid and identical affine transforms. We subtract brain-only intensity, clamp at zero, and apply an Otsu threshold to the remaining positive intensities. These are distributed image intensities, not calibrated Hounsfield units. Variants at 80%, 100% and 120% of the threshold expose extraction sensitivity. Tiny disconnected components below 1,000 voxels are omitted from the display extraction. The 180,000-face review mesh uses five Taubin display-smoothing iterations and repaired normals; quantitative points use the unsmoothed extraction. It is a local derivative, not a publisher-provided STL. Anatomical interiors remain hollow; no print filling is applied. Some inferior features meet the image boundary, so completeness must be checked before using extrema as measurements. [@ratlasNITRC2021]

The data license is CC BY-NC-SA 4.0. Keep attribution, that license notice, original volumes and hashes with derivatives; these assets are not being relicensed under the repository's code license. Source URLs, download dates and hashes are in `sources.json`. The alternative Wilson lab SolidWorks model is a useful future cross-check with approximate bregma/lambda origins, but was not imported. [@wilsonRatSkullCAD]

`audit.json` verifies both the selected R01 checkpoint and newer R09 complete review. R09 is the working hardware candidate; it has the later eye envelopes, detailed camera and compact guard. Existing review records include a lens/holder overlap of 2.04 mm³ and a small carrier/ribbon overlap. These require separate resolution when rebuilding, regardless of anatomical improvements. The active selection remains R01.

The atlas skull spans approximately 42.08 × 21.98 × 16.61 mm in its AP/ML/DV frame. The old skull spans 46.55 × 23.30 × 24.16 mm and includes different anatomy, including mandible. These bounding boxes are not homologous measurements and do not justify a scale ratio.

## Eye evidence and next stages

Read [eye and scale evidence](eye-and-scale-evidence.md). Retain the Hughes eye envelope for the first fit comparison. Current rat eye origins (±8.35 mm lateral) and directions remain estimates. The downloaded Ratlas files supply brain and bone, not paired globes: fitting skull landmarks alone cannot identify a unique globe center or corneal axis.

After the landmark review, fit the old skull using corresponding points and compare independent dimensions. A paired skull/eye soft-tissue scan is preferred for eye centers. Otherwise build an explicitly estimated orbital placement with position/angle sensitivity, not a false measured rest pose. Then fit the baseplate surface and screw clearance, re-aim the camera, refit ribbon/supports, and create a separate solidified print derivative. Follow [the reusable procedure](../../../../docs/species-anatomy-workflow.md).

## Rebuild

Run `inspect_volumes.py`, `extract_skull.py` and `prepare_review.py` from the repository root with the CAD tools Python environment. These use the retained nibabel dependency directory from the mouse atlas study. Run `open.FCMacro` through the existing FreeCAD pipe; it builds the native review document under `generated/eye-tracker/rat/anatomy-study-r10`. Preserve sources and use a new revision for changed accepted coordinates.
