# Rat R14: eye geometry and registered neutral pose

This anatomy review adds both eyes and optical axes to the accepted R13 working
skull. It preserves the R12 skull registration and R13 landmarks. It does not
select a new complete mechanical assembly or move the camera.

## Exterior shape

The existing shared adult rat eye already matches the coherent Hughes-based
exterior below, so R14 retains it [@hughes1979RatEye]. These are representative
schematic dimensions, not a measured median adult male population.

| Exterior quantity | mm |
| --- | ---: |
| Maximum globe width | 6.410 |
| Posterior exterior pole to anterior corneal apex | 6.291 |
| Corneal rim diameter | 5.640 |
| Anterior corneal apical curvature radius | 2.965 |
| Posterior apical curvature radius | 3.230 |
| Corneal cap axial height | 2.110 |

The cornea is an oblate cap; the sclera uses a smooth interpolated radial profile
between the specified poles, equator and limbus. Intermediate scleral contours
are CAD interpolation, not a scanned biological surface. The solid sclera and
cornea components partition the exterior for CAD/printing; they do not model
tissue-wall thickness. The generated `eye-profile.png` shows the actual mesh
section. All three input eye meshes are closed positive volumes; the component
volumes sum to the whole-eye volume (130.001 mm³). Width, length and rim diameter
were checked from mesh bounds, and the corneal apical radius from its analytic
ellipsoid parameters.

The literature audit also records older male Brown Norway axial measurements
with different endpoints (cornea to retina). Those values are not interchangeable
with the exterior pole-to-apex length above [@lozanoTwa2013RatEye]. See
[the evidence audit](../anatomy-study-r10/eye-and-scale-evidence.md) for cohorts
and reviewed source scope. R14 reuses that documented extraction; it does not
claim a fresh inspection of the original Hughes tables.

## Orbital location and orientation

Coordinates are millimeters in the accepted atlas frame: X anterior, Y animal
left, Z superior, bregma at the origin. R12 registered the existing skull by a
rigid fit to the atlas; R13 added working-surface landmarks. The atlas supplies
the anatomical reference frame, not paired soft-tissue eye centers
[@prior2021Ratlas; @ratlasNITRC2021].

| Eye | Eye-frame origin X, Y, Z | Outward optical unit vector |
| --- | --- | --- |
| Left | 8.264, 8.285, −6.338 | 0.330366, 0.907673, 0.258819 |
| Right | 8.264, −8.285, −6.338 | 0.330366, −0.907673, 0.258819 |

The eye-frame origin is the inherited schematic datum, not a newly measured
globe center of mass. `placement.json` includes the complete transforms and
corneal apex positions for camera targeting.

Placement starts with the previous visual orbital estimate transformed through
R12, enforces bilateral symmetry, and minimizes displacement with a penalty for
nearby bone inside the radial eye envelope plus a 0.10 mm radial margin. The
result moves the left origin 0.314 mm and the right origin 0.179 mm from their
individual transformed prior positions. Skull landmarks constrain the frame;
they do not uniquely determine this eye location. No globe segmentation or
soft-tissue registration is available for this specimen.

Neutral optical axes use azimuth ±70° from anterior toward the corresponding
side and elevation +15° above the transverse plane. This is an engineering
neutral near the inherited lateral/forward/upward pose, not a published mean
rest angle. Rat eye orientation varies with head pose [@wallace2013RatEyes].
Hughes's optic-nerve-head projection angles must not be used as gaze angles.

## Placement checks and sensitivity

Independent barycentric sampling of nearby skull triangles checked 269,906
left and 344,890 right surface locations. Neither eye had sampled radial
penetration at the nominal pose. The right side falls 0.036 mm short of the
chosen 0.10 mm radial margin at its tightest sample. This is not a Euclidean
minimum-distance result or a continuous collision proof.

Separate ±10° azimuth/elevation trials had no sampled penetration at fixed
centers. Separate ±0.5 mm coordinate trials exposed right-side sensitivity:
moving anterior, lateral or inferior produced maximum sampled radial penetration
of 0.159, 0.189 and 0.362 mm respectively. Left-side trials had none. These
chosen perturbations are scenario tests, not statistical confidence intervals.
The selected pose is suitable as a documented initial camera target, with less
confidence in location and gaze than in the specified exterior dimensions.

## Reproduce and review

1. From the repository root, run
   `tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/registered-eyes-r14/place.py`.
   It verifies the selected assembly and R13 checkpoint hashes, checks eye meshes,
   exports both eyes, and writes placement and sensitivity results.
2. Verify the current desktop FreeCAD listener PID, then submit `open.FCMacro`
   with `tools/cad/open_in_running.py --expected-pid <PID>`. It verifies and opens
   the R13 checkpoint, adds eyes and axes, and saves a separate R14 document.
3. Submit `capture.FCMacro` after the view updates. Compare the saved review
   image with the accepted landmarks and inspect the native document from
   additional angles. Keep the frozen checkpoint identified in `review.json`.

For subsequent camera aiming, use the corneal apex as the visible target and
the outward eye axis as the anatomical reference. An opposing camera looks
toward the eye along approximately the negative eye axis. Revalidate the full
camera, ribbon, arms and skull separately as required by the targeting workflow.
