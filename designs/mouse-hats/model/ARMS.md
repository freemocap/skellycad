# V5 arm reconstruction — active phase

User explicitly authorized the mesh phase. Priority: recover V5 camera-head pose
and top/rear arm paths, then parameterize their thickness, bends and junctions.
PCB groove thickening/deepening is deferred. Preserve current fit, lip trims and
filled tray notch. CURRENT remains the accepted working set; no mesh substitutes
or guessed arms have been added to it.

## First study

Source: old/df-hardware/camera-assembly/camera-assembly-2arm-v5.stl under mouse-hats.
SHA256: 1fce6b7931ccd03d27be857895ae4536ab6255d40d329f94bd0e128fbdd693df.
Exact-coordinate welding in memory yields six connected shells. Sorted by triangle
count: orange holder (3594), purple socket (3358), cyan tray (650), green rear arm
(292), pink top arm (196), loose two-triangle patch (hidden). Names are geometric
interpretations from the displayed study, not semantic metadata supplied by STL.
The loose patch is preserved in the export, not repaired or discarded from source.

export_arm_reference.py uses pinned CAD Python to tessellate the CURRENT tray.
register_v5.py uses tools/cad/.venv Python: proper PCA orientations and rigid ICP
on sampled tray surfaces, retaining closest 80% of pairs at each iteration.
No scaling, reflection or modification of supplied source meshes. STL coordinates
are provisionally interpreted in mm based on agreement with the CAD tray; this is
not an independent physical measurement.

Best alignment median/p80/p95 nearest-sample distances: 0.152/0.244/0.509 mm.
Alternative proper PCA orientations have p80 residuals 0.978 mm or worse.
These are sampling-dependent residuals, not surface-deviation bounds or fit accuracy.
Changed ribs, current cleanup and sampling density affect the score. Alignment is
PROVISIONAL; check stable vent axes, backing plane and mounting stem before adoption.

show_v5_study.py displays registered shells in a SEPARATE FreeCAD study. A hidden
fixed CURRENT tray reference can be toggled for comparison. Registration matrices,
all candidates, component bounds and transformed STL copies are under
 generated/mouse-hats/arms/ (disposable). Source STLs remain unchanged.

## Next bounded steps

1. Verify rigid tray alignment against stable geometric landmarks. Record residuals
   separately for unchanged surfaces and intentional mesh modifications.
2. Fit/recover the socket and holder poses relative to that tray. A nearly rotationally
   symmetric socket cannot determine rotation about its own axis alone; use arm
   junctions and holder/ribbon geometry as additional orientation evidence.
3. Extract section centers along each arm and fit a small, editable curve with
   meaningful endpoint/tangent controls. Do not treat mesh triangulation as design intent.
4. Rebuild arms from those paths and measured cross-sections, preserving the rear
   U-shaped ribbon space and the approximately perpendicular approaches to socket.
5. Compare surfaces and junctions before adding optional thickness/bend variants.
   Changes at arm roots may be needed to reproduce the strengthening tweaks; keep
   them explicit and separate from later PCB groove work.
6. Use printed variants to assess the actual flexible ribbon and retention. Geometry
   alone cannot establish ribbon spring forces or mechanical strength.

No parametric arms, recovered final camera placement, or strength claim yet.

## Recovered paths and landmark checks

recover_v5_paths.py recovers all arm vertices as four-point section rings: rear
37 sections (148 vertices), top 25 (100). Seed cap triangle indices are pinned to
the current processed exported meshes; graph traversal asserts four vertices at
every step. These are recovered geometric sections, not original Blender handles.
Measured sections/centers are preserved in v5-recovered-sections.json.

Vent circles fit radii 2.000000 mm and center spacing 24.999996 mm. Centers differ
from CAD by 0.020997 and 0.017638 mm. Backing X median differs by 0.002376 mm, with
0.021791 mm spread due to the small remaining registration rotation. This supports
orientation/scale correspondence but registration is not exact or manufacturing fit.
Socket spherical surfaces fit radii 2.100000 and 2.317308 mm with maximum inlier
radial residual below 0.000009 mm. Centers and inferred axis are recorded. Those
small residuals describe the sphere fit, not global alignment accuracy. Socket
axial roll and the holder's complete rigid pose remain unresolved.

Rear section nonplanarity reaches 0.124174 mm; top reaches 0.005730 mm. Do not silently
flatten these into planar loft profiles. Current yellow curves interpolate measured
centers: rear length 34.4016 mm, top 18.0493 mm. These are editable Part FeaturePython
paths (SectionCenters), not solid arms, original artist curves or compact semantic
controls. Independent saved-file reopen, 0.1 mm midpoint edit and restoration passed.
Load path_features before reopening; show_recovered_paths.py does so automatically.

Visible study: translucent source arms, yellow centerlines, white measured socket
axis. CURRENT is unchanged. Next simplify curves with measured deviation bounds,
recover cross-section orientation/thickness, rebuild solid arms and fit remaining
camera-holder pose. Do not describe this as a completed arm reconstruction.

## Smooth solid concept (user-authorized redesign)

User requests approximate V5 routing/volume without wiggles and with properly
aligned socket approaches. smooth-arms.json defines two cubic segments per arm
(root, bend, collar endpoint, tangent handles). Equal opposing bend handles give
a tangent-continuous join; curvature continuity is not claimed. Width is 4 mm,
thickness 2 mm. Ends approach the collar radially from directions 90 degrees
apart at axial height 3.5 mm and radial center distance 2.25 mm. These are explicit
concept choices, not recovered V5 intent. Socket axis/center come from V5 sphere
fitting; axial roll is selected arbitrarily for the near-axisymmetric socket.

SmoothArm exposes Width, Thickness, Root, Bend and AttachmentHeight. Parallel
transport plus smoothly distributed end rotation orients rectangular profiles,
then a solid loft passes through 25 planar sections. This is a loft approximation
to the path, not a mechanically validated constant-section sweep. JSON is the
reproducible build configuration; live edits do not automatically update JSON.

Run build_smooth_arms.py with pinned CAD Python; load smooth_arm_features before
opening generated/mouse-hats/arms/smooth/smooth-arm-concept.FCStd. The study contains
solid rear/top arms plus fixed tray/socket references. Socket moved to measured
V5 center/axis. CURRENT remains unchanged. No old arm or front extension added.

Checks: rear volume 241.183 mm3 (V5 261.077); top 135.408 mm3 (V5 141.468). Both
are valid single solids. Each overlaps tray and socket at its root/end, so the
combined tray+arms+socket Boolean is one valid solid. Each has zero overlap with
a radius-1.45 bore cylinder and radius-2.1 ball-seat sphere (0.001 mm Boolean
tolerance). Independent reopen, thickness 2 -> 1.9 -> 2 mm and restoration pass.
These tests do NOT establish holder motion clearance, thread/tool access, ribbon
clearance, root strength or printability. Reference copies are not live links.

Next: fit V5 holder pose, investigate/define the required movement envelope, check
new arms against it and the ribbon region, and refine junction transitions. Only
then propose substitution into CURRENT and printable variants.

## Planar revision — supersedes rejected twisted loft concept

User rejected sharp wiggles, cross-section twist and shallow top connection.
planar_arm_features.py replaces the two-segment loft with ONE planar cubic Bezier
and a constant 4x2 mm rectangular pipe per arm. The section's width is fixed along
the curve-plane normal. No transported/end-rolled loft frames. Controls: Root,
RootReach, SocketReach, Width, Thickness. Socket pose/end direction stay defined
in planar-arms.json; no new holder pose assumption. Root centers moved to X=4.5 mm
inside the tray backing. The prior smooth-arm concept is rejected history.

Build with build_planar_arms.py; output arms/planar/planar-arm-concept.FCStd under
generated/mouse-hats. Load planar_arm_features before reopening. Viewed in GUI
from isometric and rear directions. Each arm is one valid solid; the combined
tray/socket/arms union is one valid solid. Tray root overlaps rear 5.47836 mm3,
top 5.6454 mm3; socket overlaps 2.07168/2.64081 mm3. Both avoid bore and seat sphere.
Sampled curve turning has no sign reversal (101 points); saved reopen and +0.2 mm
RootReach edit/restoration pass. Root strength and full holder movement remain
unverified. CURRENT unchanged. This is the revision to review, not the older loft.

## Attachment-boundary revision (supersedes rejected planar-root concept)

User rejected overhanging root/socket corners. New attachment-arms.json defines
root sections from parent geometry rather than orienting oversized sections by
the curve plane. Top root: X=3.706774..5.287064 (backing thickness),
Y=14.591889..17.591889 (outer tray edge), exits +Z. Rear root: X rear face,
Y=6.565883..9.165883, Z=11.26..13.26, exits -X, clear of vent. Each embeds
0.4 mm and continues straight 1.5 mm beyond its parent face before the bend.

Both socket end sections are 2.4 mm tangential by 1.8 mm axial, centered at
collar height 3.9 mm and radial distance 2.25 mm, with a 1 mm straight approach.
The entire section is inside the collar wall; no endpoint corners project past
its height or circumference. Bore radius 1.45 and seat sphere 2.1 remain clear.

Body controls are separate: 3x1.8 mm at midspan, tapered smoothly to fixed ends.
The attachment frames differ in orientation; the loft uses an explicit gradual
33/45-degree section transition, choosing the minimum rectangle rotation modulo
180. This is NOT a zero-torsion planar sweep and not the rejected half-twist.
Single cubic routing with straight end leads replaces guessed tangent attachments.

Reproduce with build_attachment_arms.py and attachment_arm_features.py. Output:
generated/mouse-hats/arms/attachments/attachment-arm-concept.FCStd. CompleteCarrier
is the full fused solid (hidden while colored components are shown). JointInspection
TraySection is a hidden visual inspection aid, not changed design geometry.

Tests: both root end faces have zero area outside tray; both socket end faces zero
area outside collar. Each arm is valid; fused whole has one solid. Bore, seat and
cap overlaps are zero at 0.001 mm Boolean tolerance. Fresh reopen and body-thickness
1.8->1.9->1.8 edits preserve endpoint containment and restore volumes. Enlarged
rear/top/right joint screenshots were inspected. Quantified results in generated
validation.json, joint-validation.json and edit-validation.json in that folder.

Root/endpoint containment does not prove transition strength or moving holder
clearance. This revision is a review concept; CURRENT and the accepted tray are
unchanged. Previously rejected planar and twisted-loft versions are history only.

## Accepted checkpoint and strength finishing

User accepted the attachment-boundary revision and committed it as 832132f.
Targeted junction fillets are now a separate candidate; see ARM-FINISHING.md.
