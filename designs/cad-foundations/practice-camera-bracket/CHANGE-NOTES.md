# Changes

Stack study — added pure-Python stack_study.py and separate hypothetical
stack-study.json assumptions. Evaluated 10/11/12 mm candidates against minimum
protrusion 0.5 mm. Verified extrema by enumerating 32 endpoint combinations each,
and verified nominal current-screw result against live geometry. Added selected
read-only StackStudy results snapshot; saved 13-screw-stack-study.FCStd. Current
screw remains 10 mm; no geometry changes or actual hardware recommendation.

Lesson 7 review — read current live dimensions and confirmed nominal screw
protrusion 0.5 mm, floor above strap recess 2.3 mm, and one solid per printable
part. Added requirement/evidence/open-work table to README. Introduced a clearly
hypothetical worst-case stack (four layers +0.1 mm each, screw -0.2 mm), yielding
-0.1 mm protrusion. No actual tolerance claims or geometry changes. Next is a
reusable stack parameter study, before choosing hardware dimensions.

Display correction — user's screenshot revealed doubled camera/lens geometry.
PreviouslyVisible had included containers; restoring them showed all their
children, including source parts and Boolean tools. Filter container entries
from new snapshots; show_assembled_view now applies explicit leaf visibility
after enabling groups, including on fresh access builds. Repeated restore and
motion/access checks passed; screenshot inspected. Saved
12-assembly-display-fix.FCStd. No shape or dimension changes.

Access stage — returned to assembled display and added NutToolEnvelope under
References, 10 mm diameter × 14 mm length with native expressions. Outer tool
clearance only: intentional inclusion of nut and screw; no real engagement
geometry or handle. Fresh rebuild and three slide/pivot poses passed support
and moving-component collision checks. A separate hypothetical blocking plate
overlapped the envelope as expected (not added to live design). Saved
11-nut-tool-access.FCStd. No printed-part shape changed.

Interactive explosion — separate ExplosionControls object drives each copy's
Z placement through BaseZ + Layer * ExplosionControls.SeparationStep. Kept the
controller outside ExplodedView to avoid the group's dependency cycle. Verified
6/3/0 mm against independently translated source shapes; zero closes to the
centered assembly. Saved 10-interactive-explosion.FCStd at 6 mm. Numeric property
control only, no custom slider, timer, contact simulation or path validation.

Exploded presentation — five centered source copies: support, nut, bracket,
washer and screw. Added reusable create_exploded_view/show_assembled_view to
assembly.py; separation step 6 mm recorded in parameters.json. Verified five
valid solids, preserved volumes and unchanged stored motion pose. Saved
09-exploded-clamp-stack.FCStd. No new mechanical feature, joint or simulated
clamp force. Curriculum consolidated to show current lesson 7 and deferred
physical validation; keep both slide and pivot for adjust-then-lock intent.

Motion stage — extended assembly.py with source-linked shape snapshots and
explicit apply_pose refresh. Slide in local Y, then pivot about fixed screw Z;
all seven moving components share the same rigid transform. Support/fasteners
stay fixed. Demonstrated 3 mm slide, then 15 degree pivot; saved
08-slide-and-pivot.FCStd with both. Fresh complete rebuild and nine combinations
(-4.3/0/+4.3 mm × -15/0/+15 degrees) passed shape validity, preserved volume,
fixed-component collision and mating-contact checks. Verified fixed bounds.
Motion inputs use explicit _mm and _deg keys in parameters.json. No continuous
sweep, automatic property callback or joint solver. Earlier source checks remain
in the centered design frame; motion validation checks the transformed copies.

Support stage — assembly.py adds a separate support plate and simplified nut
reference, using new mm inputs in parameters.json and the same staged build.py.
24 × 18 × 4 mm plate, 3.4 mm bore, 6 × 2 mm round nut envelope. Valid solids,
no volumetric clashes, positive tab/support and nut/support contact area, and
0.5 mm screw protrusion verified in live build and fresh complete rebuild.
Saved 07-support-assembly.FCStd. Bracket unchanged. No modeled threads,
wrench access, clamping mechanics or assembly joints. Centered configuration
only; do not use the earlier screw-only travel experiment on this assembly.

Interfaces stage — interfaces.py adds fictional lens, viewing cone, rear
connector and straight cable corridor. Native expressions follow camera size.
Rear stop initially intersects connector; 6 mm-wide notch resolves collision,
removes 36 mm³ and preserves floor. Fresh complete build and screw offsets
-4.3/0/+4.3 mm passed valid-single-solid and interface interference checks
against bracket, camera, strap, hardware and driver. Saved
06-lens-cable-access.FCStd. Final printable object is now AccessibleBracket.
Real optics, cable bending and insertion sweep remain undefined. Same build.py
entry point, new interfaces stage.

Retention stage — two low end stops added; cradle depth now includes two 2 mm
stop thicknesses. Existing rear tab/hardware move through their expressions.
Cut underside strap recess (8.6 mm wide × 0.7 mm deep), leaving 2.3 mm floor.
Added 8 × 0.5 mm strap reference route, with explicit regeneration function.
No closure or flexible mechanics modeled. Checked solid, analytical volume,
camera clearances, strap/mounting-plane clearance and hardware interference.
Fresh build, offsets -4.3/0/+4.3 mm and 34×28×17 mm camera variant passed.
Saved 05-retention.FCStd. Current printable final object is RetainedBracket.

Hardware lesson — simplified screw, washer and translucent driver approach
envelope added under References. All Y placements depend on SlotCenterY plus
ScrewOffset. Hardware dimensions are fictional, not standards or purchase specs.
Validated clean rebuild, zero volumetric interference, and positive washer/tab
face contact at offsets -4.3/0/+4.3 mm. Solid-common initially omitted touching
faces; support check corrected to intersect planar contact faces explicitly.
Saved 04-hardware-references.FCStd with screw centered; bracket shape unchanged.

Slotted-tab stage — rear tab 14 mm wide, 20 mm extension, 2 mm overlap;
thickness follows floor. Slot tool uses a rectangle and two radius-1.7 mm
cylinders, united then cut through the tab. Overall slot length = 12 mm.
Native expressions follow cradle depth, floor thickness and tab parameters.
Saved 03-slotted-tab.FCStd. Verified one solid, expected capsule dimensions and
removed volume, tab extent, and no camera volume interference. Fresh rebuild
plus depth 32 / extension 24 / slot length 16 / floor thickness 4 mm variant
passed. Fasteners, retention and cable routing not yet designed.

Cradle stage — same model.py/build.py extended with floor and two side walls.
Floor 3 mm, walls 2 mm thick and 6 mm above floor. Native expressions derive
inside/outside widths and depth from camera and clearance. Three overlapping
boxes fused to one valid solid; reference camera excluded from fusion.
Validated volume, support-plane Z, side gaps and zero volumetric interference.
Fresh rebuild plus 36 × 28 mm camera variant passed. Live camera remains
30 × 25 × 15 mm. Saved 02-cradle.FCStd; no fastening or adjustment feature yet.

2026-10-08 — Envelope stage: fictional camera 30 × 25 × 15 mm, translucent
blue reference box. Native expressions bind dimensions and centered XY placement
to a named Dimensions object. Bottom at Z = 0. Keep side clearance separate from
camera dimensions for the upcoming cradle. One model module and one staged build
entry point. Preserve earlier lesson documents. No actual bracket created yet.
