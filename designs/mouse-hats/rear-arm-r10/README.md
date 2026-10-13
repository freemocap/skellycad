# R10A - narrow centered root and straighter socket return

User feedback on R09: broad PCB-side root uses too much material; center a narrower
root in the opening, taper sooner, and move socket attachment back toward nine
o'clock with a longer straight departure before the return bend.

Trial settings: root width 3.0 mm (was 5.964816), centered at Y12.550767 mm;
body width 2.6 mm, root taper completed in first 20% of Bezier parameter (was45%).
Socket-side width transitions back to 3 mm. Root thickness 2 -> 1.8 mm also tapers over that first20%. Extra outer band removed
(BandExtra0 versus0.5). Root remains flush at leading edge Z17.76629685.
Socket attachment angle30->0 degrees relative to original radial datum (nine
o'clock in supplied view); radial straight departure1->4 mm. Return-side guide
poles share departure Y so the arm returns toward the socket without dipping down
below it. OuterBulge3.25 retained; actual ribbon gap changes with new route.

Upper arm, ball/socket cavity and hardware interfaces retain their source inputs.
Lower-root blend reduced locally to R0.2 while upper-root blend remains R0.5:
the narrowed root changes available blend space near the upper arm. Inherited
stem/retainer additions are fused into tray before attaching arms. Deep checks
at each build stage catch failed fillets/unions rather than exporting invalid CAD.

Outputs under generated/mouse-hats/rear-arm-r10/:
r10a-carrier.FCStd (RibbonClearanceCarrier final); r10a-assembly.FCStd snapshot;
rear-attachment-review.FCStd comparison; R10A-carrier-and-holder.stl print-in-place
unit; validation.json, mesh-validation.json, edit-validation.json for checks.
Relative carrier/holder placement must be preserved when slicing.

Pinned FreeCAD Python runs build.py, verify_export.py and verify_edit.py. show.py
runs in live GUI. settings.json records mm/degree controls; return_sweep.py is the
route/section construction, return_carrier_features.py the carrier feature, and
return_root_edges.py semantic blend selection. Arbitrary control values are not
certified. Inspection objects are build-time snapshots. Physical camera/ribbon
fit remains pending. Earlier candidates retained; no printer submission or commit.

Final validation: carrier1220.949317 mm3 versus R09A1354.725919 (9.87% less
carrier volume). Deep checks pass at each construction stage. Minimum joint gap
0.331721863 mm unchanged; holder/baseplate overlap0; inherited cap contact
0.001611788 mm3 unchanged. Top/tray boundary samples remain contained. Native
OuterBulge3.25->3.1->3.25 edit/restore passes. STL has two watertight consistently
wound shells. Root3.4 with old finishing was rejected after fillet checks; only
final root3.0 with R0.2 lower-root blends is exported.
