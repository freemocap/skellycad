# R09A - opened underside ribbon gap

User marked the gap inside the outer arm in an underside screenshot. This trial
moves the two middle Bezier poles farther in -X: OuterBulge 2.25 -> 3.25 mm.
The guide moves 1 mm outward at u=0.5. This is a guide displacement, not a claim
of exactly 1 mm added minimum ribbon clearance. Root and socket endpoints stay
fixed. R08A's wide tapered root, section dimensions and 0.5mm outer band remain.
Top arm, ball/socket geometry, holder and accessories are unchanged.

Final carrier passes deep shape checks: one solid, 1354.725919 mm3 (+10.883002
mm3 versus R08A). Minimum joint gap stays 0.331721863 mm; holder/baseplate overlap
zero; inherited cap contact remains 0.001611788 mm3. Top/tray boundary samples
remain contained. Guide length 35.066748 mm, increased from 33.609706 by the bow.
Flexible ribbon fit and full camera movement still need physical review.

A trial native edit at OuterBulge=3.0 produced an Invalid feature state; do not
assume every intermediate parameter works. The exported 3.25 build passes deep
checks independently. Edit-validation.json records the R08/R09 endpoint replay.

Output: generated/mouse-hats/rear-arm-r09/ relative to playground.
- r09a-carrier.FCStd: source-backed carrier, RibbonClearanceCarrier final.
- r09a-assembly.FCStd: assembled snapshot.
- rear-attachment-review.FCStd: display-only grey R08A / cyan R09A comparison.
- R09A-carrier-and-holder.stl: two-shell print-in-place unit; preserve relative pose.
- validation.json, edit-validation.json, mesh-validation.json: check evidence.

Pinned FreeCAD Python runs build.py, verify_export.py, verify_edit.py; show.py
runs in GUI. settings.json holds dimensions; gap_sweep.py builds the widened path.
Inspection objects are build-time snapshots. Earlier candidates remain intact.
No printer submission or commit.
