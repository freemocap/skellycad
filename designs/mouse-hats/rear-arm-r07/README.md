# R07A - raised rear root and wider ribbon loop

User requested moving the rear arm root upward behind the ribbon exit while
keeping most of R06A's loop. This trial raises the root 3 mm along global +Y at
the same leading-edge Z datum. Exact ribbon alignment is estimated from photos.
OuterBulge increases from 1.5 to 2.25 mm: the centerline midpoint moves an extra
0.75 mm in -X. Cross-section dimensions remain unchanged. First two Bezier poles
follow the raised root; the two middle poles move outward; socket poles stay fixed.

The rectangular sweep retains R06's negative twist branch, preventing the
symmetric end section from flipping its intermediate orientation across the
90-degree nearest-angle boundary. Three interior root edges receive R0.5 blends;
the forward boundary remains flush. The top arm, socket attachment at 30 degrees,
ball cavity, holder and accessory parts remain unchanged.

Scripts: build.py constructs source-backed carrier; raised_sweep.py constructs
route/frame; raised_carrier_features.py exposes RootUp and OuterBulge in FreeCAD;
raised_root_edges.py selects junctions geometrically. Native root forward datum
is fixed for this edge scheme. Arbitrary root shifts require junction review.
Inspection arm/path objects are build-time snapshots, not live after edits.

Outputs under generated/mouse-hats/rear-arm-r07/:
r07a-carrier.FCStd (final RibbonClearanceCarrier), r07a-assembly.FCStd,
rear-attachment-review.FCStd (display offsets only), and
R07A-carrier-and-holder.stl (two-shell print-in-place unit).
Keep the carrier and holder's supplied relative placement when slicing.

Run build.py, verify_export.py, verify_edit.py with pinned FreeCAD Python;
show.py runs in the GUI. settings.json records mm and degree controls.
Validation reports accompany outputs. Physical ribbon fit and full camera-motion
clearance are not simulated; a print check is still required. Prior candidates
and frozen release retained. No printer submission.

Final checks: carrier volume 1236.367332 mm3, deep-valid single solid; joint gap
0.331721863 mm. Zero holder/baseplate overlap, unchanged inherited cap contact
0.001611788 mm3. Top/tray boundary samples contained. Fresh bulge edit 2.25 ->
2.0 -> 2.25 mm passes after retaining the R06 twist branch. STL has two watertight,
consistently wound shells. The earlier nearest-angle frame choice was discarded.
