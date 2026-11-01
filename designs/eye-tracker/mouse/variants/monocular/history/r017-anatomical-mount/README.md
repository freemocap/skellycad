# Anatomical mount placement comparison — R17

This is an annotated placement study, not a replacement complete assembly. R16 remains the complete hardware review. The blue candidate and gray existing baseplate are overlaid on the accepted detailed skull/eye reference. No hardware mating interfaces are changed in R16.

## What the literature supports

Headplate placement can be specified using both the skull midline and a named AP reference. Liu and colleagues aligned their headplate midline to the skull midline, aligned its front to the lambdoid sutures, and leveled bregma/lambda within 0.2 mm before fixation with C&B Metabond. That is a posterior, device-specific arrangement; it does not imply our camera mount belongs at lambda [@liu2025LandmarkHeadplate].

Miniscope guidance likewise uses bregma/lambda leveling and bilateral height checks. Baseplate placement follows optical alignment; it emphasizes a prepared bonding interface, dental cement and keeping the view stable during attachment. A suture is a registration reference, not evidence that it is the mechanically strongest bonding location [@miniscopeSurgeryBaseplating2026]. Neither source establishes a universal best site for our load and footprint.

Dental cement or dental adhesive is the relevant terminology. Adhesion to this printed material, footprint, load capacity and tissue clearance require their own validation. The CAD datum below is not a veterinary implantation protocol; material and surgical choices belong in the institutionally approved animal procedure.

## Current placement and nearby convention

The datum is defined from the existing horizontal mating face (face 32 of the frozen R16 baseplate), using its centroid AP coordinate and the baseplate symmetry plane. `placement.json` records its exact coordinates and the rigid candidate transform in millimeters.

In the accepted skull frame the current datum is AP -0.410 mm, ML +0.036 mm, DV +3.444 mm relative to bregma. Thus the lateral offset is negligible at the accuracy of this anatomical model. The more consequential difference is orientation: the existing baseplate axes differ from the accepted frame by 7.197 degrees, mainly pitch.

The proposed convention places this datum at AP -0.500 mm, ML 0 and preserves its current height. Align the plate AP axis with lambda-to-bregma and its lateral axis with the accepted bilateral reference direction. This moves the datum only 0.097 mm. The half-millimeter AP offset is a nearby chosen CAD convention, not a published optimum; the retained height is not a prescribed cement thickness.

Bregma and lambda establish the AP line and pitch, but do not alone determine roll. The accepted model uses paired orbital references for roll. A physical positioning jig would need a repeatable bilateral leveling reference and a visible midline/AP witness feature. The curved ventral baseplate remains inherited Boolean-cut stock; its contact surface has not been re-fitted in this comparison.

## Integration consequence

A rigid move of the entire R16 assembly would preserve its internal mating relationships but move the camera off its eye target. `placement.json` records that diagnostic miss distance. Moving the baseplate alone would break its mechanical interface. Therefore this study deliberately separates anatomical pose selection from the subsequent complete-assembly rebuild, arm/ribbon refit and contact-surface evaluation. The current aligned camera is preserved in R16.

## Review and provenance

Review scope: article metadata and relevant headplate Methods; Miniscope preparation/leveling, baseplating and troubleshooting sections; R16 baseplate faces; accepted R04 frame. Source coordinates and native checkpoints are not changed. `build.FCMacro` verifies the R04 native hash and constructs this comparison using the baseplate extracted from hash-verified R16 by `measure.py`. Follow `docs/development.md` for existing-window review. `view.FCMacro` uses an anatomical dorsal view. The candidate remains a geometric proposal, with no claim of physical fit or bonding strength.
