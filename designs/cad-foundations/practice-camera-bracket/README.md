# 4. Fictional camera bracket and assembly

Latest reviewed checkpoint: **checkpoints/13-screw-stack-study.FCStd**.
Intent: position/aim a fictional camera, then lock the mount. No client geometry,
real hardware specifications, physical fits, strength or thread engagement are
claimed. Camera is 30 × 25 × 15 mm, centered XY, bottom Z=0, front along -Y.

## Source map

| File | Responsibility |
| --- | --- |
| parameters.json | Nominal dimensions in mm; angle/pose keys explicitly suffixed |
| model.py | Envelope, cradle, tab/slot, hardware and retention; staged dispatch |
| interfaces.py | Lens, viewing space, connector notch and cable corridor |
| assembly.py | Support/nut, motion copies, explosion control, visibility, tool access |
| build.py | Original staged GUI entry point; refuses checkpoint overwrite |
| stack-study.json / stack_study.py | Hypothetical tolerance bounds and pure-Python analysis |
| CHANGE-NOTES.md | Chronological decisions, checks and corrections |

## Checkpoints and replay stages

| Checkpoint | Topic | ../replay.py stage |
| --- | --- | --- |
| 01-camera-envelope | Reference component and coordinates | envelope |
| 02-cradle | Floor, walls, 0.3 mm per-side gap | cradle |
| 03-slotted-tab | 14 mm-wide rear tab, 12 × 3.4 mm capsule slot | slotted-tab |
| 04-hardware-references | Simplified screw/washer, upper driver corridor | hardware |
| 05-retention | End stops, strap route and recess | retention |
| 06-lens-cable-access | Lens/view space, rear notch and cable corridor | interfaces |
| 07-support-assembly | Separate 24 × 18 × 4 mm support and nut | support |
| 08-slide-and-pivot | 3 mm slide, 15 degree pivot | motion |
| 09-exploded-clamp-stack | Static presentation copies (historical) | exploded uses corrected live control |
| 10-interactive-explosion | Native separation expression | exploded |
| 11-nut-tool-access | Lower tool clearance (historical display bug) | access uses corrected visibility |
| 12-assembly-display-fix | Hide originals/tools while showing moving copies | access |
| 13-screw-stack-study | Read-only current screw analysis snapshot | complete |

All checkpoint filenames end in .FCStd. Checkpoint 11 preserves the historical
duplicate-display bug; use 12/13 or replay for the corrected view. Replay `complete`
rebuilds the final geometry, motion, explosion control, access and stack report
without touching originals. Early stages are teaching steps, not final products.
The original build.py supports envelope through access. For example
main(stage='access', checkpoint='my-new-checkpoint.FCStd') creates a fresh design;
it requires PracticeCameraBracket not already open. Prefer the course replay.

## Current dimensions and interfaces

- Floor 3 mm; side walls 2 mm thick, rising 6 mm above the camera bottom.
- Inside width 30.6 mm; outside width 34.6 mm; depth 29.6 mm after end stops.
- Stops 2 mm thick and 3 mm high; side/end camera clearance 0.3 mm.
- Strap reference 8 × 0.5 mm; recess 8.6 mm wide × 0.7 mm deep; floor left 2.3 mm.
- Fictional screw shaft 3 mm, under-head length 10 mm; washer 0.5 mm thick;
  support 4 mm, simplified round nut 2 mm. Nominal tip protrusion 0.5 mm.
- Lens radius 4 mm, projection 5 mm; blue cone is illustrative, not calibrated optics.
- Rear connector 5 × 8 × 4 mm; notch width 6 mm with 0.5 mm side clearance.
- Purple upper driver envelope and pink lower tool envelope reserve space only.
  Lower envelope is 10 mm diameter × 14 mm; neither models real tool engagement.

## Live relationships versus snapshots

Native dimensional expressions update basic shapes on recompute. JSON is a build
input, not a live binding to the GUI. Reconcile manual changes before rebuilding.

| Item | How to update |
| --- | --- |
| StrapReference | model.update_strap_reference(doc), then validate_retention |
| MotionStudy | assembly.apply_pose(doc, slide_mm, pivot_deg); Slide/Pivot fields record the pose only |
| ExplosionControls.SeparationStep | Edit in Data: 6 mm separates, 0 mm closes to CENTERED sources; native expressions persist |
| Exploded shape snapshots | Recreate after source geometry edits; separation expression alone does not refresh shape |
| StackStudy | stack_study.attach_current_report(doc, params, assumptions); read-only snapshot |

Motion moves copies of bracket, camera, strap and interfaces; screw/support/nut
remain fixed. Original shapes stay in their design frame. No joint solver or
continuous collision sweep is present. ScrewOffset must stay zero in the full
assembly; the earlier screw-only travel exercise applied before the support.

Use assembly.show_assembled_view(doc) to restore explicit visible leaf objects.
Do not restore visibility by toggling entire groups: that can expose hidden
source shapes and cutting tools. To see the explosion, hide assembled shape
leaves first and show only ExplodedView's five members. This is presentation,
not an assembly path or tightening simulation.

## Analysis and validation

Geometry checks cover valid solids, expected volumes, intended gaps, mating
contact areas and interference against specified reference objects. Prior motion
checks sampled a 3 × 3 grid at slides -4.3/0/+4.3 mm and angles -15/0/+15 degrees.
Access checks sampled three poses. They are not a guarantee for arbitrary inputs.

Run stack_study.py with the workspace tooling Python (it needs no FreeCAD).
Hypothetical four-layer ±0.1 mm and screw ±0.2 mm bounds give protrusion ranges:
10 mm screw -0.1..1.1 mm, 11 mm 0.9..2.1 mm, 12 mm 1.9..3.1 mm. Only 11/12 pass
the teaching minimum 0.5 mm. All 32 endpoint combinations per candidate are
enumerated to check the arithmetic. These are not available-size recommendations.
Global Z measurement assumes the modeled screw is aligned with Z.

Still undefined: strap closure/material, mounting of the support to an external
structure, actual optics/connectors, nut flats/threads, tool handles and hand
space, allowed loads, physical fit, print orientation and strength. Preserve
these open requirements when moving to real hardware; do not infer readiness.

For fabrication exports select **AccessibleBracket** and **SupportPlate** as
separate parts. Do not export entire groups, tool envelopes, motion duplicates,
or explosion copies. Bracket design bottom is Z=-3; seat exported parts on the
bed in the slicer. No print was performed in this course.
