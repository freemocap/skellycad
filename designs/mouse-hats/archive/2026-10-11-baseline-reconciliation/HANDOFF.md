Latest ribbon-space R02 (2026-10-11): designs/mouse-hats/skull-neutral-r02/README.md.
User requested preserving ribbon bend room after posterior joint relocation.
R02 rigidly translates the entire original R11B rear arm with the joint and adds
7.649934mm smooth tray connection, keeping original straight root lead/blends.
R01 eye aim, neutral holder, top arm and socket unchanged. One deep-valid solid,
holder gap0.333165mm; holder/clip/baseplate/cap overlap0. Save/reopen passes.
GUI RibbonSpaceComparison: R01 gray left, R02 cyan right. Native output
 generated/mouse-hats/skull-neutral-r02/ribbon-space-study.FCStd.
Use open_model.py to load neutral_r02_features. Original R11B/R01 preserved.
Physical ribbon dimensions/bend radius and full motion/strength remain unverified.
No print release, source replacement, commit or push.

Latest neutral eye alignment R01 (2026-10-11): designs/mouse-hats/skull-neutral-r01/README.md.
User requested posterior joint relocation instead of tilted holder. Separate R11B
candidate translates socket/ball ~7.5 mm posterior with ~0.4 mm transverse correction;
holder neck centered on socket axis, same provisional pupil-area target as prior study.
Both arms regenerated, tray roots preserved. One deep-valid carrier; holder overlap0,
gap0.333165mm; clip/baseplate/cap overlap0; optical line unobstructed by those parts.
JointShift expressions move holder/clip/guide; +0.1mm edit, restore and reopen pass.
GUI before/after comparison open. Native generated/mouse-hats/skull-neutral-r01/
neutral-joint-study.FCStd; open with source open_model.py for feature module loading.
Original R11B and old tilted study preserved. Target/lens datum provisional; motion,
ribbon, print and anatomical placement remain unverified. No commit or print release.

Latest skull/eye placement study (2026-10-11): designs/mouse-hats/skull-placement/README.md.
Supplied skull repaired separately: 0.04 mm voxel + decimation, one watertight shell,
zero detected non-neighbor intersections; sampled max surface change 0.01945 mm.
Original sources unchanged. FreeCAD SkullPlacementStudy shows R11B, repaired skull,
separate eyes, provisional Blender-derived mount placement and red plate-normal aim.
User clarified aim through marked flat lens/sensor region toward pupil area.
20.41885-degree holder pose hits an eye-surface proxy, NOT a verified pupil landmark.
Small holder/carrier contact 0.0024977 mm3; not a cleared neutral joint or print release.
Next review pupil target and seating, then socket neutral orientation and clearances.
Native generated/mouse-hats/skull-placement/skull-placement-study.FCStd.
No accepted carrier/baseplate changes, source writes, staging, commit or printing.

SELECTED BASELINE: R11B (B as in Buffalo), chosen by user 2026-10-10.
Record: designs/mouse-hats/rear-arm-r11/selection.json (paths, parameters, STL hash).
Use B for subsequent rear-arm work; keep A/C/D/E as references. No geometry changed.
Native generated/mouse-hats/rear-arm-r11/r11b-carrier.FCStd.
Print generated/mouse-hats/rear-arm-r11/labeled/R11B-labeled-carrier-and-holder.stl.
User selected winner; no additional physical test claims inferred.

R11 labeled print bundle ready: designs/mouse-hats/rear-arm-r11/print-labels/README.md.
A-E embossed on exterior tray backs,3.5mm tall/0.4mm relief, away from PCB seat.
Five labeled native snapshots and separate two-shell watertight STLs; letters
visually checked, solid/interference checks pass, jointgap0.331722 unchanged.
ZIP generated/mouse-hats/rear-arm-r11/labeled/R11-A-E-labeled-STLs.zip.
Import as5separate objects, auto-arrange in slicer; keep each carrier/holder pair.
GUI R11EmbossedLabels displays backs with permanent letters. Prior unlabeled
files preserved. No printer submission or commit.

Active R11 five-option route study: designs/mouse-hats/rear-arm-r11/README.md.
User asked >3 variants near7:30 with smoother returns. A35deg/7:50, B45/7:30,
C40/7:40; balanced2.5mm leads. D45/1.5mm broad early bend; E45/3.5mm longer lead.
All retain R10 centered3mm root ->2.6mm body, upper arm and joint geometry.
All five deep-valid carriers; holder/baseplate overlap0, jointgap0.331722 unchanged,
inherited cap contact unchanged, top/tray boundary samples contained. Mesh report
checks each two-shell STL. Physical ribbon/motion fit pending; user chooses subset.
GUI LowerDepartureOptions: labeled A/B/C top row, D/E bottom. Comparison inspected.
Separate files generated/mouse-hats/rear-arm-r11/R11[A-E]-carrier-and-holder.stl.
Rejected steeper55/50deg guides not exported. Per-option loft counts/degrees recorded.
No printer submission or commit; all prior work retained.

Active R10A slim centered root/straight socket return: designs/mouse-hats/rear-arm-r10/README.md.
User marked nine-o-clock departure and requested much narrower centered root.
Root3mm centeredY12.550767, taper to2.6mm over first20% guide; BandExtra0.
Socket angle30->0, straight departure1->4mm; return guide poles at departureY.
Root blendR0.2 (upper staysR0.5); source stem/tabs fused to tray before arms.
Final deep checks pass, volume1220.949317 (9.87% belowR09). Gap0.331722 unchanged;
zero holder/baseplate overlap; inherited cap contact unchanged. Reopen/edit/restore
passes; STL2watertight shells. Physical ribbon/motion fit pending.
GUI StraightReturnReview grey R09A / cyan R10A.
STL generated/mouse-hats/rear-arm-r10/R10A-carrier-and-holder.stl.
Earlier work retained. No commit/printer submission.

Active R09A opened underside gap: designs/mouse-hats/rear-arm-r09/README.md.
User marked inner ribbon gap. OuterBulge2.25->3.25 opens guide midpoint1mm in -X.
Root/section/socket attachment unchanged. Deep-valid carrier; gap0.331722 and
inherited cap contact unchanged; holder/baseplate overlap0; STL2watertight shells.
Fresh3.25->2.25->3.25 replay passes. Intermediate3.0 edit yielded Invalid state;
not all parameter values reliable. Physical ribbon fit remains unverified.
GUI RibbonGapReview compares grey R08A / cyan R09A; bottom view inspected.
STL generated/mouse-hats/rear-arm-r09/R09A-carrier-and-holder.stl.
Earlier work preserved; no commit or printer submission.

Active R08A broad tapered root/outward band: designs/mouse-hats/rear-arm-r08/README.md.
User wants root matching PCB opening and fatter curve without sacrificing space.
Optional clarification pending: assumed retainer gap Y9.568359..15.533175 (5.964816mm)
and outward material addition, not more cavity enlargement. Root tapers to3mm;
BandExtra0.5mm negative-h side at middle, fades at ends. R07 guide curve unchanged.
Single deep-valid carrier, volume1343.842917 (+107.475585mm3). Gap0.331722 unchanged,
no holder/baseplate overlap; inherited cap contact unchanged. Fresh band edit .5->
.4->.5 passes. STL2watertight shells. Flexible ribbon fit still unverified.
GUI WideBandReview grey R07A above / cyan R08A below.
Direct STL generated/mouse-hats/rear-arm-r08/R08A-carrier-and-holder.stl.
Prior candidates preserved. No commit or printer submission.

Active R07A raised root / wider loop: designs/mouse-hats/rear-arm-r07/README.md.
User requests root behind ribbon exit. Trial RootUp +3mm Y from R06A at same
leading edge; OuterBulge2.25 (midpoint0.75mm farther -X than R06). Section unchanged.
Keep negative R06 sweep twist branch to avoid frame flip. Root three inside R0.5
blends; socket attachment/top arm unchanged. Gap0.331722, deep-valid carrier,
zero holder/baseplate overlap; inherited cap contact unchanged. Reopen/edit/restore
passes and STL2watertight shells. Ribbon alignment estimated; physical test pending.
GUI RaisedRibbonRootReview grey R06A above / cyan R07A below.
Direct STL generated/mouse-hats/rear-arm-r07/R07A-carrier-and-holder.stl.
Previous candidates retained. No commit or printer submission.

Active R06A leading-edge rear root / wider ribbon loop: designs/mouse-hats/rear-arm-r06/README.md.
R05C printed and improved; user requests more ribbon spring room and root closer
to camera-facing tray edge. Root +4.5063 mm Z, front flush; midpoint 1.5 mm farther
out in -X. R05C 30-degree collar attachment and upper arm/ball fit unchanged.
Deep-valid carrier; gap0.331722 mm, zero holder/baseplate overlap, inherited cap
contact unchanged. Fresh bulge1.5->1.25->1.5 edit passes. STL two watertight shells.
GUI ForwardRootReview grey R05C above / cyan R06A below. Top/side visually checked.
Direct STL: generated/mouse-hats/rear-arm-r06/R06A-carrier-and-holder.stl.
Root datum changes require root-edge blend review; physical ribbon fit pending.
No commit/printer submission. Previous candidates and frozen R02 retained.

Active R05C rear collar attachment study: designs/mouse-hats/rear-attachment-r05/README.md.
User requested sliding rear arm attachment around socket collar, especially R04B.
New candidate rotates attachment 30 degrees toward lower loop; first four R04B
Bezier poles retained, last two follow rotated endpoint and inward radial tangent.
Top arm/socket fit unchanged. Deep-valid one-solid carrier, min joint gap0.331722,
zero holder/baseplate overlap, unchanged tiny cap contact. Fresh 30->25->30 edit
passes. Print unit two watertight shells; accessory hashes unchanged.
GUI RearAttachmentReview: grey R04B above / cyan R05C below. Physical review pending.
Output generated/mouse-hats/rear-attachment-r05/mouse-hats-r05c-print-test.zip.
R04 options and frozen R02 preserved. No commit or printer submission.

Active R04 A/B rear-arm routing study: designs/mouse-hats/rear-arm-r04/README.md.
User photos/red arrows show rear arm too high/tight around ribbon; wants sweep
behind ribbon exit from sensor holder and back up to tray. Top arm fixed.
A uses smooth quintic guide fitted to stored V5 section centers, with fixed R03
endpoints/tangents. B drops midpoint 1.25 mm more; 1.5 trial failed CAD validity
and was not exported. Both one valid carrier/deep check, joint gap0.331722 mm,
zero holder/baseplate overlap, unchanged tiny cap contact. Top/tray boundary
samples remain contained; whole-coincident Boolean difference unreliable, not
used as proof. Shared R03 construction preserves upper arm/socket dimensions.
Fresh reopen A->B->A passes. STLs each2watertight shells; accessories unchanged.
Output generated/mouse-hats/rear-arm-r04/mouse-hats-r04-rear-arm-options.zip.
GUI RearRibbonOptions: grey R03 / cyan A / gold B; V5 rear mesh optional hidden.
No ribbon model/full-motion clearance claim: user should physically compare A/B.
R03 and frozen R02 retained. No printer submission or commit.

Active R03 print candidate: designs/mouse-hats/print-test-r03/README.md.
User physically printed R02: overall good, ball fused to socket and neck broke
while freeing it; requested stronger arm/socket joins and larger ball clearance.
R03 arm ends 3.0x2.2 mm (was2.4x1.8), collar R3.1 (was2.701637), R0.3 junction
blends plus R0.2 collar/bowl blend. Cavity cut R2.35 at existing R2 ball center.
Measured min holder gap 0.331722 mm vs0.121146. Holder/neck unchanged. One valid
carrier; no holder/baseplate overlap, tray material/neck opening/bore preserved.
Unchanged tiny cap contact0.001612 mm3 documented. Reopen/edit/restore pass;
net+43.979 mm3, sampled bowl wall min0.915 mm (not global proof).
R03 two-shell STL and unchanged accessory STLs in generated/mouse-hats/print-test/r03;
zip ready, GUI assembled unit and separate socket-section inspection tab.
R02 frozen release remains unchanged. R03 needs physical test; material/nozzle/layer
question remains unanswered. No print job or commit performed.

Release checkpoint created: releases/mouse-hats-r02/README.md is the current
sharing entry point; MouseHats_R02-release.zip is the bundle. Five named AP242
parts, native assembly, numbered exploded view, four-page guide, print inputs,
editable source checkpoint, rebuild/open tools, validation, hashes and change log.
No geometry changed; all prior work preserved. Snapshot rebuild passes and four
print STL hashes match R02 exactly. STEP names/colors/solids/placement pass;
deep BOP InvalidCurveOnSurface warnings on four imported parts are disclosed
(native deep checks pass). No second-application or physical print validation.
No commit/staging performed. Tooling: designs/mouse-hats/release.

Latest: Print Test R02 changes only baseplate lower exterior to an inward taper.
Reference tall_tapered_53n_baseplate.stl measured bottom scale 0.57004. Native
baseplate tapered from pocket floor Y1.5 to bottom Y-5 mm; full mount region
at/above Y1.5 unchanged. Bottom area 67.483 -> 21.928 mm2. Valid one solid,
watertight one-shell STL, zero seated carrier overlap, reopen/edit/restore pass.
R02 other three STL hashes identical to R01; R01 preserved. See
 designs/mouse-hats/baseplate-taper/README.md (folder: designs/mouse-hats/baseplate-taper).
R02 zip: generated/mouse-hats/print-test/r02/mouse-hats-r02-print-test.zip.
Print fit/strength/release still untested. Larger ball/neck and weight holes pending.

Latest print-test R01: user accepted R3 stem blend, requested longer PCB tabs
and thicker holder walls. Tabs +1.5 mm at arm end, +0.7 mm lower (user chose cap
preservation). Holder walls +0.5 mm outward; user explicitly required clip
extension rather than thinning/removing material to fit old clip. Clip crosspiece
+1 mm, intact arms shifted outward 0.5 mm. See designs/mouse-hats/print-test/README.md.
V5 holder pose fitted and ball-center anchored. Print-in-place carrier/holder STL
has two watertight shells, zero overlap, min modeled gap 0.121 mm. Separate revised
clip plus unchanged cap/baseplate exported. Zip in generated/mouse-hats/print-test/r01.
Controls reopen/edit/restore pass. Tiny clip contact (~0.0045 mm3) documented; fit,
full motion, supports/ribbon/strength unvalidated. No printing or slicing performed.
GUI PRINT TEST R01 shows cyan carrier, purple holder, gold installed clip reference.

Latest correction: user rejected the raised stem pad. Replacement is a direct
R3 mm tangent fillet on the original stem/tray junction: build_stem_blend.py,
stem_blend_features.py, stem-blend.json. Added 0.913429 mm3, no removal; seated
fit, cap, PCB side and arm geometry preserved. Reopen/R2 edit/R3 restore and
main transition tangency checks pass. GUI Stem Blend candidate open; old pad
labeled REJECTED. See model/REINFORCEMENT-PLAN.md under mouse-hats.

Latest: stem failures occurred during support removal; user wants reinforcement.
Separate stem-reinforced carrier adds a tapered 0.6 mm rear backing patch at the
stem junction. Added 10.161 mm3; cap/baseplate fit and PCB side preserved; valid
solid and reopen/edit/restore pass. See model/REINFORCEMENT-PLAN.md under mouse-hats.
Holder walls, coupled ball/neck/socket enlargement and weight openings pending.

Latest (2026-10-09): user accepted/committed attachment arms (832132f) and authorized
strength finishing. See designs/mouse-hats/model/ARM-FINISHING.md. Separate finished
candidate adds tray-root R0.5 and socket-junction R0.3 mm internal fillets. One valid
solid; added ~0.731 mm3, no removed material or added cap/bore/seat interference.
Reopen and radius disable/edit/restore pass. Cyan whole carrier, gold fillet faces.
Checkpoint and CURRENT unchanged. Await user's other reinforcement observations;
full holder motion/ribbon/print evaluation still pending.
# CAD playground handoff â€” course preserved, 2026-10-08

## Current real-part work (supersedes the pending-folder notes below)

Latest: user REJECTED planar arm endpoints/overhangs. AttachmentArmConcept open:
face-aligned straight roots sized to tray and endcaps contained in socket collar.
model/build_attachment_arms.py, attachment_arm_features.py, attachment-arms.json.
Both root/socket end faces have zero outside-parent area; bore/seat/cap clear.
One fused solid, reopen/body-dimension edits pass; enlarged three-angle joints
inspected. Full colored concept visible; inspection slice hidden. CURRENT unchanged.
See ARMS.md for section dimensions and remaining movement/strength limitations.


Latest: user REJECTED prior twisted smooth-arm lofts. PlanarArmConcept now open.
model/planar_arm_features.py: one planar cubic + rectangular pipe per arm, no twist,
deeper tray roots. build_planar_arms.py and planar-arms.json reproduce. Multi-angle
visual inspection, solid/connection/bore/seat checks and reopen/reach edits pass.
CURRENT unchanged; holder movement and root strength still unverified.


Latest: user authorized smoother redesigned arms and corrected socket approaches.
Solid concept open: smooth-arm-concept.FCStd (green rear, pink top, purple socket).
model/smooth-arms.json + smooth_arm_features.py + build_smooth_arms.py reproduce it.
4x2 mm sections, two cubic bends, radial approaches 90 degrees apart at collar.
Valid solids, joins to tray/socket, bore/seat nonoverlap and reopen/edit tests pass.
CURRENT unchanged. Holder motion, ribbon clearance and root strength unverified;
next fit holder pose and check movement envelope before adopting. See ARMS.md.


Latest arms study: yellow editable centerlines recovered from 37 rear/25 top
four-vertex rings; raw sections saved in model/v5-recovered-sections.json. Vents
verify 25 mm spacing and <0.021 mm center discrepancy. Socket spheres/axis fitted;
axial roll and full holder pose unresolved. Paths reopen/edit/restore passed.
Rear rings have up to 0.124 mm warp; do not assume planar sections. See ARMS.md.
No solid arms or CURRENT changes yet; next curve simplification and arm solids.


ACTIVE: user authorized V5 mesh phase, arms and camera pose first; grooves later.
Read designs/mouse-hats/model/ARMS.md. Separate V5ArmsStudy visible: green rear arm,
pink top arm, purple socket, orange holder, cyan tray. Provisional rigid tray
registration completed; needs landmark verification (sample median 0.152 mm).
CURRENT remains unchanged. No parametric arms or final adopted camera pose yet.


Latest: user requested filling vestigial tray end notch to restore straight edge.
model/build_notch_cleanup.py creates CleanedTrayAndMount; CURRENT part 02 now
links to model/tray-cleanup/cleaned-tray.FCStd. Lip trims retained, no extension
or added clearance. One valid solid; adds 7.142446 mm3, removes zero, cap overlap
zero at 0.001 mm tolerance; GUI reopen/recompute passed.


CURRENT working entry: designs/mouse-hats/model/CURRENT.md. New canonical
CURRENT.FCStd has numbered whole parts and assembled views, switched by
ViewSelector.Layout. current-parts.json selects all six final features, including
TrimmedTrayAndMount (corner trims only). No nose extension or pocket allowance.
Six solids and 15 pair checks passed after reopen. Old views are historical.


Latest correction: user canceled ALL front extension. Only the two confirmed lip
corner trims remain. Extension solid, fusion and green highlight removed from the
saved visible candidate and builder. Front geometry and stem fit remain unchanged.


User explicitly authorized lip corner snips and a 2 mm nose extension normal to
the PCB plate. Candidate implemented in model/build_lip_trim.py; see model/README.md.
trimmed-mount.FCStd is visible with cyan section and green extension. Validity,
seated-stem preservation, baseplate overlap and reopen checks pass. Nominal fit
retained; original assembly unchanged. Next review this intended geometry edit.


User confirms the current design already fits nicely. Preserve nominal geometry
and fit while improving organization/controls. No geometry changes without an
explicit functional reason. Review is reset to zero added clearance; nonzero
clearance values are isolated test probes, not design recommendations.


Mount interface candidate implemented under designs/mouse-hats/model; read README.md.
Shared bearing planes feed stem profiles and pocket. PocketClearance adds normal
allowance to bearing and entry faces, keeping stem/floor fixed. Geometry probes
0/0.025/0.05/0.075/0.1 mm, baseline differences, restore and edited reopen pass.
Separate mount-fit-review.FCStd is visible at 0.05 mm; Baseplate selected. All six
checkpoint hashes unchanged. Not integrated into assembly; slopes are fixed build
inputs, not validated live controls. Next review then variant persistence/integration.


Checkpoint 8709351 is committed and visually accepted. Current phase: improve
controllability before later mesh fixes. Read designs/mouse-hats/reconstruction/
DEVELOPMENT.md. Saved-file audit records 12 existing length controls and six FCStd
hashes in assembly/control-inventory-baseline.json. Assembly verification rerun
passed. No geometry changed: next implement shared stem/pocket interface geometry
with default-shape regression and explicit clearance behavior in separate candidate
outputs, then tray/cap controls. Audit and roadmap additions are uncommitted.


Latest: User accepted the cap visually and authorized assembly consolidation.
Six-part live linked assembly is now open: generated/mouse-hats/reconstruction/
assembly/02-linked-assembly.FCStd. Use designs/mouse-hats/reconstruction/assembly/
open_model.py to load proxy modules. Links reference editable final features with
measured assembly transforms; no mating solver. All six reopen/placement/validity
checks and cap/baseplate edit propagation tests pass. All 15 pairs have valid zero
common volume at 0.001 mm tolerance. Ball/socket centers retain an approximately
0.3 mm offset also present in original 58; do not describe radius difference as
uniform clearance. Read assembly/README.md and validation-baseline.json. Old arm
omitted; mesh phase deferred. Next: assembly review and functional parameter/interface
planning. All individual source-parity limitations remain; physical fit unverified.

User-supplied files are in designs/mouse-hats. User accepted old/58nassembly.step
as the reconstruction baseline after inspecting the assembled reference. Read
designs/mouse-hats/AGENTS.md and docs/reconstruction-plan.md there. First bounded
part is the camera clip; its whole native reconstruction is complete and verified.
See designs/mouse-hats/reconstruction/camera_clip/README.md for the current stage.
Next part, the camera holder, is now a complete native reconstruction candidate
open beside its source in CameraHolderRebuild58. It is NOT accepted parity:
source BOP errors preclude trustworthy Boolean comparison; dense sampling reports
up to 0.058823 mm deviation after an explicit analytic root-blend approximation.
See reconstruction/camera_holder/README.md under mouse-hats. Saved/reopened
candidate and plate-thickness edit pass deeper geometry checks. Next review the
candidate and differences before promoting it to the assembly.
User visually accepted the holder and requested the next part. SocketRebuild58
now contains a complete socket candidate, cyan beside gold source. Native revolve
plus parameterized collar pad; saved/reopened and all three collar controls tested.
Bounded sampling maximum ~0.0000231 mm; no exact Boolean parity claim due source
BOP errors. See designs/mouse-hats/reconstruction/socket/README.md. Next carrier.
No STL comparisons or later two-arm mesh work. Fusion is installed but currently
unneeded because 58 STEP contains the required cap and clip geometry.

Latest: user explicitly deprioritized the old arm/junction because it will be
replaced later. TrayMountRebuild58 now shows cyan rebuilt PCB tray + mounting stem
and gold source region (+26 mm Y), which still includes old arm-root remnants.
One solid, deeper BOP check passes; native reopen and vent radius/spacing edits
tested. Lower region Z<=10 mm has zero Boolean missing/excess at 0.001 mm tolerance,
not exact identity. Read reconstruction/main_carrier/README.md under mouse-hats.
This model uses native sketches/lofts/cuts plus ONE custom tolerance-union feature;
use its open_model.py loader for reliable later recomputation. Old arm omitted;
no whole-carrier parity claim. Next separate part is the skull base plate, then
check its mating interface with this stem. Do not resume arm/mesh work yet.

## Current task and boundary

Latest continuation: BaseplateRebuild58 now shows cyan rebuilt uncut Baseplate
beside gold 58 source (+18 mm X). Read reconstruction/baseplate/README.md under
mouse-hats. Scripted parametric feature: open_model.py loads its module for edits.
Independent rebuild/reopen, bore/stock-depth edits and display stages pass.
Source BOP errors prevent exact Boolean parity. Source-to-candidate sampled max
0.200219 mm occurs on a small source cap at the pocket mouth (face 32), absent
from the valid candidate. Critical mating planes preserved; rebuilt base/tray
seated interference volume zero at 0.001 mm tolerance. Review before PCB cap.
No physical fit proof. Keep old arm and skull mesh work deferred.

The introductory course is finished enough to move to real-part work. It is
preserved in [designs/cad-foundations](designs/cad-foundations/README.md).
The user will create a new folder with new source files in THIS workspace,
then discuss requirements before reconstruction begins. Do not create another
chat or access the old DF client checkout. New user-supplied files can be handled
within the scope they subsequently authorize here; the earlier plan to return
to another project context has been superseded by this plan.

Read [TRANSFER-STATUS.md](TRANSFER-STATUS.md) for setup and verification status.
No client models were imported during the course or cleanup.

## Working style

The user knows Python, Blender and computational geometry and interacts through
voice transcription. Explain design intent with short, concrete code excerpts,
verified current line links, and visible FreeCAD results. Do not invent line
numbers. Move at a useful pace; pause for conceptual questions without losing
the task. Avoid repeated permission requests for authorized reversible work.
When asked to change UI settings, use the UI/settings route, not custom controls.

Navigation is now Blender style with the user's G HUB FreeCAD-specific profile
(G502 HERO; rear thumb mapped to middle click). Do not change it. User already
knows STL slicing/printing and explicitly skipped print onboarding. Printer:
Snapmaker U1, PLA, Snapmaker Orca. No print was performed or requested.

## Runtime and safety

Use the local pinned FreeCAD 1.1.4 runtime and `cad_playground_freecad` MCP.
Check `CAD_PLAYGROUND_ROOT`, endpoint ownership and document list before editing.
RPC is localhost port 9875; do not kill another process to claim the port.
`./tools/cad/cad.ps1 test-mcp` / `show-freecad` operate the existing session;
`start-freecad` creates it if absent. Save before `stop-freecad`.
Run document mutations through synchronous execute_code on the GUI thread.

Runtime setup stays in tools/cad and .cad-tools; it was not moved with lessons.
The parent directory is the Git repository. Scope staging and commits to this
playground. No commit/push or new chat is implied by cleanup.

## Reproducibility

Save source, units, parameters and concise notes under designs. Native FCStd
checkpoints retain editable feature graphs. generated is disposable. Use the
course replay.py to make fresh examples without overwriting preserved lessons.
JSON is not automatically synchronized with manual edits; reconcile explicitly.
Strap shapes, motion copies, embossed text and analysis snapshots have documented
refresh limits. An exploded-view control is a native expression, not a joint
solver. Shape validity does not establish printability, load capacity or fit.

Five live documents were captured before relocation in the course's
session-snapshots directory. They preserve interactive state separately from
historical checkpoints. Inspect active files before changing or closing them.

## Next project approach (not started)

After the user supplies files and scope: preserve baseline, inventory components
and formats, identify critical interfaces, choose one bounded part to rebuild,
then compare geometry and intent before extending the reconstruction. Avoid
copying unexplained inherited complexity or discarding it without investigation.
No additional fictional exercises are prerequisites.

The previous handoff and accumulated documentation are preserved in
designs/cad-foundations/history/documentation-before-cleanup.zip.
