> SUPERSEDED AS A COMPLETE MODEL: this study used the older PCB tray. Its camera/arm work is incorporated into [the current model](../current/README.md). Use the current manifest for edits and printing.

# Posterior joint / neutral eye alignment R01

2026-10-11. User requested moving the entire ball/socket posteriorly so the
holder sees the eye while centered in the socket. Separate candidate derived
from selected R11B. Accepted source files and the previous skull study remain intact.

The candidate is `generated/mouse-hats/skull-neutral-r01/neutral-joint-study.FCStd`.
The visible comparison is `before-after.FCStd` in the same output directory:
left = original location with holder tilted toward eye; right = translated joint
with centered holder. Comparison objects are static snapshots.

## Geometry and alignment

- Neutral means holder neck axis parallel to socket axis; original holder pose
  needed only 0.212212 degrees correction to satisfy this. Plate normal differs
  from neck axis by approximately 0.007 degrees.
- Solve the shortest joint translation that puts the marked plate-center normal
  through the existing eye-surface target. Translation in assembly coordinates:
  X -7.492981, Y +0.342848, Z -0.652235 mm; magnitude 7.529125 mm.
- Pure posterior displacement of 7.520265 mm would miss that target by 0.394752 mm.
  The candidate includes a small transverse correction to hit it exactly. Source
  skull +X points toward the broad posterior cranium; its transformed direction
  is recorded in settings.json. No change to skull or implant/baseplate placement.
- Translate the socket and its clearance sphere together, retain R11B sections,
  collar and bore dimensions, then rebuild both arms with fixed tray roots and
  moved socket endpoints. Rear arm retains its broad route and 45-degree return.
- Holder, clip, lens datum and optical guide follow JointShift via expressions.
  The eye target stays fixed. Off-design JointShift values need new clearance checks.

## Verification

One valid carrier solid; deep shape checks pass. Centered holder/carrier overlap
0 mm3; minimum separation 0.333165 mm. Carrier/clip, carrier/baseplate and
carrier/cap overlap each 0 mm3. Optical guide has no common edge length with
carrier, baseplate or cap. Neck/socket angle and optical target error are zero
within numerical precision. A +0.1 mm X joint edit, holder propagation, return to
baseline volume, save and fresh reopen passed. All saved objects report valid
document states. Validation records live in validation.json.

These checks cover the neutral pose, not the full motion cone, ribbon envelope,
strength, printing or anatomical suitability. The target is the previously
reviewed approximate pupil-area point; neither exact pupil position nor exact
lens center has been established. Preserve this distinction when refining aim.

## Controls and replay

Run open_model.py through synchronous execute_code in the pinned FreeCAD GUI to
load the feature module before opening the candidate. The candidate contains
local snapshots of construction inputs; changing NeutralCarrier.JointShift
rebuilds arms/socket and moves holder/clip/datum/guide. The external eye target
remains fixed. Other inherited controls retain their R11B meaning and limits.

build.py derives the initial shift from the prior skull placement and the marked
plate datum, then builds the candidate. It requires the established r11b_carrier,
print_in_place_review2 and tapered_baseplate source documents to be open. It writes
the derived settings.json; JSON and later GUI edits are not automatically synced.
compare.py creates the static before/after display from saved candidate geometry.
Use mm for vector coordinates. No STL/print release, commit or baseline promotion.
