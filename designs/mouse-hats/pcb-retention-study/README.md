> T3 is the PCB baseline incorporated into [the current complete model](../current/README.md). This folder records PCB development history.

## T3 tray-side cap rail - 2026-10-10

User clarified the long tray-side upper rail must be taller; the cap hook slides past it. Section at Z=0 confirmed old rail top Y17.591889 below T2 hook tip Y17.742359. `build_t3_rim.py` raises the rail 0.7 mm to Y18.291889; its rear engagement face X4.587064 clears hook X4.437064 by 0.15 mm. 0.15 mm entry chamfer. Engagement height 0.549530 mm, roof gap 0.300470 mm. Added volume 8.313520 mm3.

T2 cap geometry retained. T2 PCB catch/seat, arms and joint retained. Zero PCB overlap, existing 0.002218 mm3 cap contact unchanged. Simulated 0.3 mm +X cap pull: upper-hook region old interference 0, new 0.925334 mm3, confirming capture rather than bypass. This is NOT elastic snap/insertion validation. Physical testing required.

Output `generated/mouse-hats/pcb-retention-study/height-geometry/t3-rim/`; ZIP `R11B-T3-raised-rim-print-pack.zip`. Native model, validation and two validated watertight STLs included in output. Print ZIP includes carrier/holder, matching cap and notes. Labels still T +1.0 mm; filename identifies T3. `show_t3_rim.py` opens comparison. Earlier revisions preserved.

## T2 selected +1 mm revision - 2026-10-10

User selected +1 mm tray and requested a JST-ward, wider, shorter PCB catch plus deeper cap engagement. `build_t2_grip.py`, `t2-grip-settings.json`, and `show_t2_grip.py` implement/display this isolated revision. Output/print ZIP: `generated/mouse-hats/pcb-retention-study/height-geometry/t2-grip/R11B-T2-plus-1mm-grip-print-pack.zip`.

Catch moves 1.5 mm toward JST, grows 2 to 3 mm along edge, roof 0.6 to 1.0 mm, overlap 0.38 to 0.18 mm. Upper cap long hook deepens 0.35 mm and tip reaches 0.15 mm farther. Relocated catch requires a local recess in the secondary upper locating tab: 4.126 mm3 removed, plus a detached 0.091 mm3 corner removed to avoid loose geometry. Remaining cap is one valid solid. Use matched T2 cap/carrier. Physical emboss retains T +1.0 mm; revision identified in filenames.

Deep checks pass; zero PCB interference and catch/cap overlap; 0.15 mm catch/cap distance, inherited 0.002218 mm3 total cap contact unchanged, 0.331722 mm ball gap unchanged. Translated PCB checks still show upward/outward capture. Two-shell carrier/holder and one-shell cap meshes watertight with consistent winding. Functional insertion and grip require printing. Print notes in ZIP. Prior variants retained; no commits or printer submission.

## Numeric-label print pack - 2026-10-10

Current ZIP: `generated/mouse-hats/pcb-retention-study/height-geometry/with-catch/numeric-labels/R11B-PCB-catch-tests-0p5-and-1p0mm.zip`. Four STLs: H +0.5 mm and T +1.0 mm carriers/holders and matching caps. Both upper catches included. Numeric labels and mm embossed 0.4 mm on exterior faces; numbers denote added tray height. Functional geometry unchanged, corrected PCB reference retained. Build with `build_numeric_catch_labels.py`; view with `show_numeric_catch_labels.py`. Deep solid and independent watertight/winding/shell checks pass. All labels visually inspected. Prior packs preserved.

## Corrected PCB reference from proven catches — 2026-10-10

User confirms actual PCB fits unchanged lens-end catches. Their slot boundaries are Y=8.168359 and 17.392359 mm, opening 9.224 mm. Current shared `pcb-reference.json` / `pcb_reference.py` uses width 9.2 mm, Y=8.18..17.38, thickness 0.25 mm. Length remains approximate 30 mm at Z=-14..16; do not claim a measured outline.

Rebuilt current H/T native catch models and visible comparison with this envelope. Both have zero seated board/carrier and board/cap overlap. Catch upward/outward blocking checks pass. Upper-edge room becomes H=0.162 / T=0.662 mm. Existing catches, new lips, arms, cap and all printed geometry are unchanged: all four STL SHA256 hashes match the previous validated exports. ZIP refreshed only for corrected print notes; existing downloaded complete-catch STLs remain current. Older historical screenshots/models retain their original approximate PCB and are superseded by this reference. Future height builds also use the shared reference.

## COMPLETE upper-catch print trials â€” 2026-10-10

The previous H/T height-only exports missed the requested upper PCB catch and are superseded for testing. New complete files are under `generated/mouse-hats/pcb-retention-study/height-geometry/with-catch/`; ZIP `R11B-H-T-COMPLETE-with-PCB-catches.zip` contains four labeled STLs and print notes.

Both heights now include a fused 2 mm long rigid L-shaped upper-edge catch, with 0.4 mm nominal overlap onto the PCB edge, 0.6 mm roof thickness and 0.35 mm clearance above the bare 0.25 mm board. A beveled mouth eases entry. H provides 0.142 mm edge-to-post room, T 0.642 mm. Catch sits 0.15 mm inside its matching cap wall. The previously approved tiny stem nose is trimmed flush to the seating plane. No arm or joint dimensions changed.

`build_catch_print_tests.py` builds from preserved labeled height tests; `catch-print-settings.json` records dimensions; `show_catch_print_tests.py` displays gold catches with green approximate boards. Deep-valid single-solid carriers, zero added catch/cap or seated-board intersection, and unchanged 0.331722 mm holder gap. Translated board-envelope checks verify the lip blocks upward and outward escape. STL independent checks pass: watertight, consistent winding, two carrier/holder shells, one cap shell. Reports and inspected comparison PNG are beside exports.

Physical insertion and electronics clearance remain unverified: the simplified seated PCB envelope already overlaps existing retainers by 1.651 mmÂ³, unchanged by the new catch. No claim of collision-free full insertion is made. Compare both prints without forcing the board. All earlier source/output files are retained.

## Labeled R11B height print tests â€” 2026-10-10

Requested test exports are in `generated/mouse-hats/pcb-retention-study/height-geometry/labeled/`:

- **H:** +0.5 mm upper tray edge, matching cap.
- **T:** +1.0 mm upper tray edge, matching cap.
- Each carrier and cap has its matching letter embossed 0.4 mm outward, 3.5 mm tall. Carrier label is on the backing exterior; cap label is on the connector-cover exterior.
- Carrier-and-holder STLs preserve the print-in-place ball holder as a separate shell. Caps are separate STL files. Units are millimeters.

These are height-fit trials, not final PCB spring-catch designs: no new upper catch is included. The previously studied local stem-nose flush trim has not been merged into this R11B baseline. Existing R11B arms, socket clearance, and lower interfaces are preserved.

Rebuild with the pinned FreeCAD Python runtime and `export_labeled_height_tests.py`. Parameters are in `height-print-labels.json`. Label BREP checks, source hashes and independent STL checks are stored beside the exports in `label-validation.json` and `mesh-validation.json`. All four meshes are watertight with consistent winding: two shells for each carrier/holder, one for each cap. Both pairs of embossed letters were visually inspected in `labels-review.png`. Existing tiny carrier/cap contact volume (0.002218 mmÂ³) is unchanged; physical fit remains a print-test question.

# Visible height geometry now built â€” 2026-10-10

Current GUI: PCBHeightComparison, three rows 0 / +0.5 / +1 mm with matching caps
shifted aside for display only. Native variants: generated/mouse-hats/
pcb-retention-study/height-geometry/height-0.FCStd, height-0p5.FCStd,
height-1p0.FCStd. Comparison saved separately as height-comparison.FCStd.

This is actual solid CAD, replacing the earlier datum-only stage described below.
height_features.py exposes HeightCarrier.TrayUpperEdgeOffset; HeightCap follows
that property. Build with build_height_geometry.py; show with show_height_geometry.py.
The frozen R11B and active selected print outputs remain unchanged.

Prototype policy: grow the original backing profile upward using its upper vertices
(Y>=15 mm), and fuse only added backing material into R11B. Existing retainers,
arm paths, socket, lower mount and PCB pose stay fixed. Cap upper wall/cover edges,
upper features and side-hole coordinates follow the same offset; lower profiles
stay fixed. The Y>=15 threshold classifies this recovered source geometry and is
NOT a general production modeling rule. Semantic per-feature datums are the next
refinement. The former datum-only upper_edge.py is not the CAD proxy implementation.

Zero offset copies the exact R11B carrier BREP; rebuilt cap volume matches the
reference. All offsets produce one deep-valid carrier and one deep-valid cap.
Holder gap stays 0.331721863 mm. Current Boolean cap overlap is 0.002218226 mm3
at all three offsets, including zero; use that same-run baseline instead of mixing
it with older isolated-check results. Native reload and 1 -> 0.5 -> 1 edits restore
both volumes correctly. Added volumes:
- +0.5: carrier 21.115592 mm3, cap 18.230000 mm3, total 39.345592 mm3.
- +1.0: carrier 42.231208 mm3, cap 36.460000 mm3, total 78.691208 mm3.

These studies do NOT yet establish cap latch engagement, insertion-path clearance,
full PCB fit or structural performance. The board remains an approximate envelope.
The top spring catch is not included, and the isolated nose trim has not been ported
into R11B here; preserve the zero-offset reproduction milestone before those edits.
No STL was exported, no selected revision was overwritten, and no geometry was adopted.

---

# Current baseline and upper-edge functionality â€” 2026-10-10

R11B is now the selected baseline, confirmed by the user's message and the arm
study's selection.json. New work uses the frozen R11B assembly identified by
r11b-reference-manifest.json. Do not integrate against the earlier R06 snapshot.
The old mockups and nose trim remain historical studies, not an R11B print revision.

## What has been implemented here

upper_edge.py is an isolated shared-datum prototype, not a CAD feature yet.
preflight_upper_edge.py pins R11B and checks offsets 0, 0.5 and 1.0 mm:
tray upper edge and matching cap wall move together; the PCB edge, catch tip,
seat-to-catch gap and PCB thickness stay fixed. Tests pass. No active native file,
arm builder, selected STL or GUI view was changed. No CAD refactor is claimed.

With the provisional PCB pose, side room to the cap is respectively 0.192359,
0.692359 and 1.192359 mm. These are datum calculations, not collision-tested revised
assemblies. The physical PCB seating position still needs reconciliation.

## Implementation assessment

Moderate, bounded refactor: the arithmetic/control is simple; geometry propagation
and preserving mating details require most of the work. R11B's carrier builder
(options_carrier_features.py, lines 45-51) fuses a referenced tray with saved
reinforcement additions, then adds the arms and blends. It does not construct the
tray from a live shared height. The cap builder (reconstruction/pcb_cap/build.py,
lines 30-36) extrudes independently recovered profile coordinates. Thus adding a
property to the final shape alone would not create reliable parametric behavior.

Recommended contract:
- TrayUpperEdgeOffset is relative to the current tray top, default zero.
- PCB measured dimensions/pose remain separate; no scaling of the electronics.
- CatchOverlap and CatchGap are referenced to the PCB, not the rising tray edge.
- Keep lower catches, board seat, stem, ball/socket and R11B arm paths fixed.
- Move the upper tray/cap interface together; regenerate their mating profiles.
- Preserve the upper-arm root if the extended tray can still meet it correctly;
  re-check that blend. Do not silently move it with the upper edge.
- Port the isolated nose trim explicitly, as a separate named feature, after
  comparing its region on R11B. Do not assume the correction is already applied.

First geometry milestone: zero-offset reproduction of selected R11B plus existing
cap, before adopting a height or catch. Compare functional regions and volumes,
using methods robust to the known coincident-surface Boolean limitations. Then
build 0.5 and 1.0 mm geometry probes and verify carrier/cap solids, cap insertion,
full-board insertion and protected interfaces. Compare actual added CAD volumes
only after both parts exist. The unit test is not a substitute for those checks.

## Material-conscious alternatives

1. Full upper-edge growth: clean shared dimension and predictable cap boundary,
   but a continuous strip adds material along the full tray and matching cover.
2. Local raised catch support plus local cap clearance: potentially less material;
   still use the shared datum to define the allowed envelope, with explicit catch
   location/length. Review cap wall thickness and transitions; do not automatically
   fill the entire strip up to the datum.
3. Current-height lip plus cap relief: smallest envelope change, but current
   side room is insufficient for the earlier proposed upright without a relief.

A dimension defines an interface/envelope, not an obligation to fill it with
plastic. Explore full-height probes to establish feasibility, then compare a local
support using the same controls. No flexible latch, separate keeper or new loose
part. No final choice of extent, height or catch geometry has been made.

---

# Latest: nose flush correction and upper-lip clearance study

User accepted the whole-board direction view, authorized trimming the circled stem
nose flush with the board backing, and requested options for a +1 mm taller tray.
No height or lip decision has been adopted.

Current GUI: PCBTopLipOptions; generated file top-lip-clearance-study.FCStd.
The nose correction removes 1.402543 mm3 within a small bounded region above
Y=6 mm, leaving all geometry below that plane unchanged. The forward face is
flush at X=5.287064 mm; maximum removed protrusion 0.766638 mm. One valid carrier
passes the deep shape check. This correction exists only in the study and has
NOT been merged into the independently evolving arm source or print outputs.

Gold is a 2 mm-long top lip concept, with 0.6 mm roof gap, 0.4 mm overlap and
0.5 mm upright. It is correctly above the PCB and points downward. It clears the
assumed board but clashes with the existing cap by 2.266722 mm3. Do not print it
as a solved assembly. CapConflict can be toggled to inspect that intersection.

The long orange line is the optional +1 mm upper-edge target, NOT a rebuilt tray.
At the assumed board pose, current side room is 0.192359 mm; shifting the matching
cap wall up 1 mm would make that 1.192359 mm. This is a local clearance calculation,
not verification of a revised cap or insertion sequence. Whole-board placement
still has other inherited-geometry overlaps (1.650859 mm3 after nose trimming).

Design check-in: current tray/cap construction contains recovered profile
coordinates; upper-arm root and blend selection use separate datums. There is
no single shared height parameter propagating correctly through the assembly.
A disciplined height change needs a shared upper-edge datum and explicit rules:
keep PCB seat, lower catches and stem fixed; extend tray upward; update the cap
wall/retention interfaces; then decide whether the upper-arm root stays fixed or
moves. Do not globally scale the assembly or move the ball/socket to get headroom.

Alternatives: (A) current-height local lip plus a matching cap relief, subject to
remaining wall thickness; (B) +1 mm upper-edge growth plus revised cap interfaces.
Recommend exploring B as a shared-datum refactor if the extra envelope is acceptable,
but coordinate its integration only after the active arm candidate is selected.
The arm source and global handoff files are untouched by this study.

Build/show: build_top_lip_options.py / show_top_lip_options.py. Trial dimensions
are recorded in top-lip-options.json; some recovered diagnostic profile coordinates
remain explicit in the builder, so this is not yet the proposed shared-height API.

---

# Current review: whole PCB and correct escape direction

The user REJECTED both cropped-corner R1/R2 mockups: they restrain the wrong
edges and duplicate existing bottom/side retention. Do not reuse them as accepted
candidates. R3 is also rejected. All remain below solely as historical records.

Current GUI: PCBWholeBoardReview. Current file:
`generated/mouse-hats/pcb-retention-study/whole-board-review.FCStd`.
Build with build_whole_board_review.py; show with show_whole_board_review.py.

The review shows the whole approximate 30 x 10 x 0.25 mm PCB on the unchanged
full R06A carrier. Camera left, connector right, red arrows +Y/upward along the
tray, orange annotation on the TOP LONG EDGE near the connector. That is the edge
an eventual downward-facing integral cup/lip must capture. Orange is an annotation,
not plastic. No additional catch has been built in this corrected review.

Board dimensions are user measurements; its placement is approximate. With this
assumed pose the board intersects the carrier by 1.912168 mm3 and seated cap by
0.586789 mm3. Consequently this is NOT a verified fitted electronics model or a
print candidate. Component/connector footprints are illustrative. Do not hide these
uncertainties by replacing the board with a small corner sample again.

Next geometry must follow a reconciled full-board seating pose and top-edge contact
region, permit rigid-board insertion, and clear the cap. Keep all arm work unchanged.
The frozen carrier shape was verified unchanged in the corrected review.

---

# PCB retention study â€” assembly catch proposals

Status: R1/R2 local CAD mockups created, 2026-10-09. Neither is adopted or print-ready.
Independent of the active R06A arm-placement work. User rejected R3: no flexible
latch and no additional separate part.

## Purpose

The ribbon weakly lifts the connector end of the PCB out of its existing catches
while the user installs the cap. The cap retains the PCB adequately once fitted.
Replace temporary tape with a minimal integral tray catch. No extra loose part;
do not bend the PCB, clamp components, or redesign the cap as the first approach.

User measurements: PCB approximately 30 x 10 mm; bare board approximately
0.25 mm thick. Tallest ordinary component is 1 mm from the underside (about
0.75 mm above the board); connector 1.7 mm from the underside (about 1.45 mm
above the board). Full extended camera assembly approximately 80 mm. These are
approximate user measurements, not manufacturer drawings. Lens thread unverified.

## Isolate this work

- Work only within this study folder and generated/mouse-hats/pcb-retention-study/.
- The generated reference is a frozen copy of R06A's five-part assembly. See
  reference-manifest.json for its original path and SHA-256. It is a comparison
  reference, not an instruction to rebuild or replace the arm candidate.
- Use PCB-R1/R2/R3 names so the study does not consume arm revision numbers.
- Do not edit shared arm builders, global handoffs, release files, active print
  outputs or another study's parameters. Do not change the live FreeCAD view
  without a reason to interrupt the arm review.
- Later implement the catch as a small optional feature taking the current
  carrier as input plus explicit tray-local datums. Default off. Do not copy an
  entire arm-generation chain or identify placement by numbered faces/edges.
- At integration time explicitly select the then-current carrier and repeat
  checks there. A saved R06A snapshot is not a merge destination or latest pointer.

## Proposals

### PCB-R1 â€” one short side lip near the connector end (first choice to explore)

A small roof over a clear strip of the PCB's long edge restrains lift near the
connector end. An upright grows from existing tray material; the roof overlaps
only a bare edge. Use a lead-in chamfer and a supported, blended root.

Hypothetical insertion: tuck that edge under the roof, then settle the opposite
edge into the existing catches. Hypothetical removal reverses that motion.
This must be checked with a rigid board envelope: existing catches may prevent
the necessary tilt or lateral motion. Do not solve that failure by flexing the PCB.

Benefits: smallest local change; avoids making a new end wall around the plug.
Risks: little bare edge beside components; a single catch may allow pivoting;
insufficient tilt clearance could make insertion impossible.

### PCB-R2 â€” short connector-end hood / corner pocket

A shallow hood captures a clear corner near the board's connector end, leaving
the plug and cable exit open. It acts more like the user's downward-facing cup.

Hypothetical insertion: translate the rigid PCB a short distance lengthwise
under the hood, then seat its other end. Explicitly check available lengthwise
travel and ribbon movement; this may be blocked by the existing end stops.

Benefits: captures the end with the largest observed lift. Risks: connector/cable
and cap interference; more constrained insertion; no proven free corner yet.

### PCB-R3 â€” REJECTED by user; retained only as proposal history

A small tray latch is held out of the way while the PCB is seated, then released
over its edge. It should not require pressing the board against a stiff hook.

Benefits: less reliance on sliding travel. Risks: tiny printable flexure, access
for release, fatigue and layer-direction sensitivity. More development than R1;
avoid unless rigid-lip insertion paths fail. No material-specific strength claim.

## Initial experimental controls (not fit specifications)

- Roof underside: 0.60 mm above the local PCB seating surface. With a 0.25 mm
  board this allows 0.35 mm lift; check that existing catches still engage.
- Edge overlap: explore 0.30 and 0.50 mm, only where a clear edge strip exists.
- Length along edge: initially explore 2 and 3 mm.
- Root/roof thickness, exact location and chamfer: undecided until cap and edge
  clearance are inspected. No arbitrary final print thickness is assigned here.

Change one control at a time. Keep gap fixed while comparing overlap first.
If 0.35 mm lift allows escape, reduce the gap based on insertion and print results;
more clearance is not automatically better retention.

## Evaluation sequence

1. Make a clearly labeled approximate rigid PCB envelope with separate component
   and connector keep-outs. Photograph-derived outlines are not precision CAD.
   Identify a genuinely bare edge; aggregate component heights alone do not do so.
2. Show R1 and R2 as local colored proposals over the frozen tray; include section
   views showing roof, board and seat. Keep the rest of the assembly as context.
3. Check explicit insertion/removal poses and a sampled rigid-body path against
   existing catches and the cap installation path. Report sampling limits.
4. Check carrier validity, added material bounds, cap clearance and unchanged
   mating regions. Preserve/document the baseline's tiny cap intersection rather
   than treating it as a new catch defect. No new cap interference is acceptable.
5. If useful, print tray-only fit coupons preserving all relevant catches and
   enough space for the actual attached ribbon/holder. A disconnected board-shaped
   gauge alone cannot test the ribbon spring problem.
6. Physical pass: board seats without forced bending; stays caught hands-free
   through ordinary cap fitting; cap seats normally; board can be intentionally
   removed without prying against components. Inspect for edge damage.
7. Apply the selected optional feature to the then-current arm candidate and
   repeat whole-assembly checks before exporting a combined print candidate.

## Public references already checked

- https://github.com/pupil-labs/pupil-geometry â€” mounting interface CAD, not a
  verified bare-board model for this camera.
- https://docs.pupil-labs.com/core/hardware/ â€” camera-generation documentation.
  No matching dimensioned bare PCB/ribbon drawing was found in the prior search.

No messages have been sent to other chats or external parties. The study's local
documents are its handoff; the independent arm work remains authoritative for arms.


## First R1/R2 mockups

Run `build_mockups.py` with the pinned FreeCAD Python, then run `show_mockups.py`
in the existing GUI. This creates a separate PCBRetentionConcepts review tab.
All outputs are confined to generated/mouse-hats/pcb-retention-study/.

Actual trial inputs are in mockup-settings.json: 0.60 mm roof gap, 0.60 mm roof
thickness, 0.40 mm nominal overlap, 2 mm catch length, 0.10 mm edge-side clearance,
0.70 mm upright thickness and 0.15 mm underside lead-in chamfer. The overlap is
a midpoint trial, not a fit result. Seat X=5.287064 is the inherited tray plane;
board edge Y=8.168359 and connector end Z=-14 are provisional placements.

R1 overlaps a long edge; R2 overlaps an end edge. The green 3.5 x 6 x 0.25 mm
sample represents ONLY a local board corner, not a complete PCB. No component
keep-out map is implied. The photos/measurements do not yet establish a verified
bare contact strip or precise seating pose.

Both full carriers pass deep validity checks as one solid. Added volumes are
1.969050 mm3 (R1) and 2.268721 mm3 (R2). Each proposed addition has zero overlap
with the seated cap and local board sample. A 0.8 mm local slide was checked at
21 poses against the new catch only. This does NOT validate whole-board assembly,
the pre-existing catches, ribbon motion, cap installation motion or components.
No print STL was exported. The blue cropped tray is inspection-only.

In the review tree, toggle the hidden purple InsertionStart sample for a local
slide illustration, CapReference for the seated cap, or CandidateCarrier for the
complete carrier context. Turn off TrayDetail/Catch when viewing CandidateCarrier
to avoid overlapping display surfaces. R1/R2 concepts retain the unchanged frozen
R06A arm geometry; they do not update active R06 files or shared handoffs.
