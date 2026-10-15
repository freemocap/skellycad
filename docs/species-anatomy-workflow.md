# Anatomical reference to species print pack

Use this procedure for a new species or a new anatomical reference. The first rat application is [anatomy study R10](../designs/eye-tracker/rat/anatomy-study-r10/README.md). Mouse named landmarks R03, landmark eyes R04, mount R18, targeted assembly R19 and solid print R22 are worked examples. This procedure records modeling decisions; it is not a surgical protocol.

## 1. Freeze the starting point

Read development.md, the species README, active-model.json and eye-tracker-targeting.md. Verify the selected checkpoint hash. Identify a newer complete review separately if it is the working candidate. Record source hashes, units, matched-part names, existing collisions and accepted user constraints. Never infer selection from the largest revision number.

## 2. Audit anatomy and evidence

Prefer a paired skull and soft-tissue dataset with physical units, specimen metadata and anatomical datums. Retain original assets and license. Record species, strain, sex, age, mass, sample size, preparation and acquisition resolution. Separate specimen, average template, mean, median and engineering estimate. Register sources in references.bib under CITATIONS.md; inspect corrections and supplements before extracting numbers.

Create an evidence table for skull dimensions, eye envelope, globe centers, corneal direction and posture. Every number needs endpoints, frame, cohort, uncertainty and citation. A retinal axial length is not external scleral length; an optic-nerve projection or visual field is not the corneal optical axis. Bone alone does not determine globe centers. The rat audit illustrates these distinctions. [@hughes1979RatEye; @lozanoTwa2013RatEye; @wallace2013RatEyes; @belli2018RatFace; @belli2024RatFaceCorrection]

## 3. Extract and name the reference

Preserve image affines and handedness. Record every image-to-mesh and mesh-to-CAD transform; use millimeters. Keep raw reference, display simplification and print solidification as separate derivatives. Check segmentation thresholds and field-of-view truncation. Grid spacing is not measured anatomical accuracy.

Store each landmark as an ID, English name, coordinates, coordinate frame, source, status and confidence. Distinguish author coordinates, locally identified anatomical points and geometric extrema. Show colored spheres, leaders and readable names. Keep estimates visibly marked. Ask the user to review the actual labeled model before promoting candidate locations to the working anatomical frame.

## 4. Register and check scale

Use named homologous correspondences, initially with a proper rigid transform. Allow one uniform scale only when the evidence supports it; record the scale independently of pose. Check determinant, left/right handedness, landmark residuals and withheld landmarks. ICP may refine a fit but cannot establish anatomical homology by itself. Do not derive scale from differently cropped bounding boxes or force unrelated cohort measurements to agree by anisotropic warping. [@lawrenceBernalWitzgall2019]

Compare at least three independent named distances where available. Preserve the original specimen and report representative scaling as a modeling choice. Define bregma origin, midsagittal plane, anterior and dorsal directions explicitly. A bregma-lambda leveling frame and a local skull-surface tangent are different quantities.

## 5. Place eyes and define optical datums

Fit outer-globe and corneal regions separately when paired tissue data exist. Record the center convention, sclera/cornea dimensions, symmetry assumptions and fit residuals. Otherwise use a literature-based envelope with explicitly estimated orbital placement. Run position and orientation sensitivity studies rather than hiding the uncertainty.

Each eye has a local +Z axis through the corneal apex and the selected globe/schematic center. Store center, axis and roll in the skull frame and show the axis through the globe and outward. Keep measured scan posture separate from a chosen neutral behavioral pose. Never claim a universal rest orientation from a head-position-dependent gaze study. [@wallace2013RatEyes]

## 6. Seat the baseplate

Keep the mounting interface dimensions fixed. Express placement relative to accepted landmarks; fit the local skull surface under the plate and orient its face approximately parallel to that surface. Measure actual rear screw/hole clearance against the skull. The current project request is at least 2 mm, preferably more; record which hardware envelope is tested. Preserve intentional tapered Boolean stock separately from collision-free fixtures. Report footprint, surface gaps and the tested screw geometry.

## 7. Reattach and aim the camera

Use the selected shared Pupil Core complete camera through shared.camera.add_camera with verified assets and optical datum. Follow eye-tracker-targeting.md. Move the matched cradle/holder/camera together, aim toward the anatomical eye target, and refit arms and ribbon around the fixed PCB/baseplate interfaces. Optimize both axis alignment and stand-off under clearance and ribbon constraints. Report aiming error, axis mismatch, fixed-interface changes, ribbon collision, arm seating and anatomy interference independently. Record inherited defects; do not silently accept them as new validation.

## 8. Make the print derivative

Preserve the hollow anatomical reference. Fill the braincase and simplify nasal/internal structures only in a separate printable skull. Prefer source cavity labels where supplied; otherwise document closure and fill parameters. Inspect sections and outer silhouette. Add an eye bridge with an explicit diameter and material; mouse R21/R22 uses 2.25 mm assigned to skull material.

Partition skull/bridge, sclera, cornea and baseplate into four non-overlapping volumes with common placement. Export a multipart U1 3MF with explicit tool assignments; STL alone carries no color. Export matched print-in-place hardware in one shared transform. Exclude reference axes and real electronics from printable solids. Check closed surfaces, connected anatomy, material overlaps, preserved mating gaps, archive hashes and profile assignments. Label unsliced and unprinted status truthfully.

## 9. Review and handoff

Provide the named-landmark scene, registration/eye comparison, complete assembly and print pack at the appropriate stages. Keep accepted checkpoints immutable. Select a new complete assembly only after its intended geometry checks and review pass. Physical fit remains a separate result from CAD validity. Update the species README, lineage, recipe, validation and bibliography checks so another session can reproduce the work without relying on chat history.
