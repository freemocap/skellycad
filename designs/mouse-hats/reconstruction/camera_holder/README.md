# Camera holder reconstruction candidate

Source: 58nassembly.step, RightCamHolder (1), source hash and measured geometry
in parameters.json. The frame is aligned to the holder rail sides and plate;
assembly_to_holder_frame preserves the mapping back to the source assembly.

build.py creates a native PartDesign body: two plate lofts preserve the clip seat
bevel, six rail lofts form front/rear legs, two rear-return lofts preserve the
underside ramps, and a revolution forms the ball/neck/root profile. A side pocket
trims the root near the plate edge without truncating the exposed ball.

## Important qualification

This is a complete reconstruction candidate, NOT an accepted exact replacement.
The source passes basic isValid() but fails the deeper BOP check with C0 and
invalid-curve-on-surface errors. Full-source Boolean comparisons returned
inconsistent/invalid results and are not used to claim parity. Earlier source
clip/holder common-volume output is therefore only a diagnostic, not a verified
interference result.

The two source BSpline root patches are approximated by an analytic 1.25 mm
rounded profile. The torus major radius is nominalized from 3.999997858 mm to
4 mm to make the neck and 2 mm ball tangent. The root is trimmed to the side up
to the nominal blend transition. These are explicit deviations awaiting review;
the original source is preserved. Source tolerance/edge inconsistencies also
mean plane-derived contours need not reproduce every imported vertex.

The replacement passes the deeper BOP check. validate.py samples both surfaces
in both directions and records distance statistics, source diagnostic failures,
net volume difference and a plate-thickness edit. Sampling is an estimate, not a
certified maximum deviation or a fit test. Failed source-edge discretizations
are counted and fall back to endpoint samples.

## Editing and reproducing

## Recorded verification result

Complete visible model: generated/mouse-hats/reconstruction/camera-holder/
01-holder-candidate.FCStd. Dense validation.json sampled 19,328 source points
and 28,838 reconstruction points. Maximum sampled distances were 0.0454143 mm
source-to-rebuild and 0.0588230 mm rebuild-to-source; RMS distances were 0.0018620
and 0.0013337 mm respectively. These are finite samples, not certified bounds.
Each direction encountered one edge discretization failure and used its endpoints.
No acceptance tolerance has been agreed; candidate is NOT promoted to assembly.

Net volume difference is -0.00947504 mm3 (not symmetric difference). The source
has 37 faces and replacement 57. Plate thickness 1.0 -> 1.1 -> 1.0 mm passed deeper
geometry checks. verify_headless.py independently rebuilt from parameters, saved,
reopened, and edited the file successfully. Its bounded 240-point sampling is a
speed check, not a replacement for the denser recorded results. Dense validation
initially occupied the GUI beyond the RPC timeout but finished successfully;
perform future expensive measurements in a separate pinned-runtime process.

## Editing and reproducing the candidate

Dimensions.PlateThickness changes the upper plate and moves the ball/root with
it. Rail and clip-seat geometry stays fixed. Planar sketches are constrained by
measured corner coordinates. The curved profile currently uses fixed arcs;
ball/root dimensions are JSON build inputs, not live independent UI controls.
Changing such inputs requires a fresh build and revalidation; do not confuse
stored measurements with fully developed semantic parameter controls.

Run build.py main() in the pinned FreeCAD GUI. It only needs parameters.json and
the shared camera_clip/build_base.py profile helper; no imported solid is a
modeling dependency. validate.py needs the source transformed into holder-local
coordinates. Native output is under generated/mouse-hats/reconstruction/
camera-holder. Source displayed alongside the replacement has a display-only
14 mm X offset. User subsequently authorized the first-pass linked assembly. Manufacturing and
physical-fit acceptance remain pending; recorded deviations still apply.
