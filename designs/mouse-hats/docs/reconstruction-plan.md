# STEP reconstruction plan

## Current baseline — user accepted 58

The user confirmed the 58 assembly is the intended design and matches its
clipped-together appearance. old/58nassembly.step supersedes 53 as the working
baseline. Earlier source-recovery steps below are historical context.

First bounded part: RightCamClip (1). checks/prepare_clip58.py prepares an
unchanged source reference in local coordinates. Its broadest face defines the
base plane; that face's longest edge defines X. Original assembly placement is
retained as LocalToAssembly. The round-trip Boolean difference measured 0 mm3.
Local bounding dimensions are 8.737434 x 3.500648 x 3.997940 mm. These are measured
bounds, not rounded design parameters. The source includes taper and tiny sliver
faces; any simplification must be quantified, not silently called exact parity.

Next: model the clip's base, retaining walls and lips with named dimensions;
compare geometry and mating surfaces with the preserved reference. No replacement
clip was built at that preparation stage. Preserve the accepted assembly in its own document.

Progress: complete clip now built with constrained sketches and native lofts.
Whole-source comparison reports zero missing/excess volume. Thickness edit and
standalone saved-file reopen/edit passed. See reconstruction/camera_clip/README.md.
User requested finishing the entire clip before the next check-in; now ready for
that review. Nominal simplification and remaining assembly parts are not complete.

User accepted the clip and requested the next part. Camera holder is now a full
native candidate with a deliberately analytic root-blend approximation. Source
fails deeper BOP checks; Boolean comparisons are unreliable. Dense sampled
surface deviations reach 0.058823 mm. Candidate and saved-file edits pass deeper
checks. Review this candidate before promoting it or advancing to the socket.
See reconstruction/camera_holder/README.md for evidence and limitations.
User visually accepted the holder and requested continuing. Socket candidate is
now complete; see reconstruction/socket/README.md. Separate native collar height,
outside radius and bore radius controls passed saved-file edits. Source profile
is approximated by smooth cubic curves; sampled match is close, not proof of
global exact parity. Next planned part: main carrier.

User subsequently redirected the carrier pass: do not spend effort reproducing
the old arm or junction, because the arm will be replaced later. Priorities are
PCB tray, mounting stem and skull base plate. TrayMountRebuild58 now contains the
tray/stem candidate; see reconstruction/main_carrier/README.md. Its lower region
matches by Boolean checks at 0.001 mm tolerance; old arm is intentionally absent.
Fresh build, saved-file recompute and vent edits pass deeper geometry checks.
One Python tolerance-union feature supplements native sketches/lofts/cuts; use
open_model.py for its import path. Next: separate skull base plate and interface
checks. The later two-arm mesh phase remains deferred.

Latest completed candidate: uncut 58 baseplate, shown in BaseplateRebuild58.
Read reconstruction/baseplate/README.md: scripted construction, verified edits,
preserved mating planes and zero seated interference at 0.001 mm tolerance.
A source pocket-mouth cap is absent; sampled max deviation there is 0.200219 mm.
Source BOP errors prevent exact parity. Next visual interface review and PCB cap.

Latest: user visually accepted baseplate and requested continuing. Native cap is
now ready for review. See reconstruction/pcb_cap/README.md for tests and Boolean
comparison limitation. A three-part static assembly review shows cap, tray/stem
and baseplate; seated overlaps are zero at 0.001 mm tolerance. Next review and
consolidate the retained parts into an organized assembly. Mesh work stays deferred.

## Earlier plan (superseded source selection)

1. Use 53 STEP for the newer carrier and inspect older supplied STEP/F3D sources
   for missing components. Record identities and revision caveats in
   functional-map.md. Preserve source coordinates and generation per part.
2. Define a clean part/assembly structure with named parameters and constraints.
3. Start with the main carrier (solid 1), rebuilding manageable functional regions
   as native FreeCAD features. The skull-cut baseplate is an interface reference,
   not the preferred first target.
4. Compare it directly with the STEP reference: dimensions, placement, validity
   and geometric differences. Record tolerances and explain discrepancies.
5. Verify coverage of the intended STEP hardware. Keep the embedded skull as a
   reference, not a manufactured part to rebuild. The mating ball/lens holder is
   identified as 52-5. Cap and retaining clip still need CAD source recovery
   before claiming a complete camera assembly.

No STL, two-arm, mesh-registration or future-variation work is included.
The first deliverable is a clean editable reproduction of the STEP geometry.
Source/imported solids must remain distinguishable from rebuilt features.

Parity is evaluated per part against its named source, with assembly interface
checks when combining generations. Later baseplate height/insert-pocket changes
are explicit design revisions if their source cannot be recovered. Fewer source
faces alone is not success: preserve important dimensions and interfaces, expose
named editable parameters, and verify representative edits recompute correctly.
