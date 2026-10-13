# R08A - broad tapered arm root and outward band

Preview based on R07A. User requested root width matching the rear PCB opening,
tapering to existing arm width, and a fatter top-view curve with similar length
and clearance. Pending optional clarifications, the reference opening is the gap
between the camera-end retainer faces Y=9.568359 and Y=15.533175 mm (5.964816 mm).
The preview adds material outward rather than enlarging the ribbon cavity again.

## Construction

Root spans that opening behind the tray. Width reduces from 5.964816 mm to the
existing 3 mm body width. Extra root width fades smoothly over the first 45% of
the Bezier parameter; widening is one-sided, retaining the old lower root edge
to within the 0.00248 mm alignment correction. The broad root gets the same
R0.5 inner junction blends. No PCB-side slots or retaining lips are modified.

Reference Bezier centerline, tangents, frame twist branch and socket attachment
are unchanged from R07A; reference path length remains 33.609706 mm. Cross-section
centers shift to add material on one side, so this is a fixed guide curve, not
an assertion that the material centroid path is unchanged.

BandExtra=0.5 mm adds to the negative-h (outer) section face with sin(pi*u)^2
fade, zero at both ends. The positive-h boundary is retained at section stations
where root taper is complete. This preserves the intended inward boundary of the
middle loop; it is not a simulated flexible-ribbon clearance guarantee. Loft
interpolation and the broad root transition still require physical fit review.
No general full-motion or global minimum ribbon clearance is claimed.

## Checks and tradeoff

Carrier is one deep-valid solid, 1343.842917 mm3, +107.475585 mm3 relative to R07A.
Holder/baseplate overlap zero; joint gap unchanged at 0.331721863 mm. Existing
cap contact stays 0.001611788 mm3. Top/tray boundary containment samples pass.
Final native edit check and mesh checks are recorded with generated outputs.
The added root is substantial; this preview prioritizes the requested width match.

## Files and replay

Outputs: generated/mouse-hats/rear-arm-r08/ relative to playground.
- r08a-carrier.FCStd: source-backed carrier; RibbonClearanceCarrier is final.
- r08a-assembly.FCStd: full five-part assembly snapshot.
- rear-attachment-review.FCStd: display-only grey R07A / cyan R08A comparison.
- R08A-carrier-and-holder.stl: two-shell print-in-place unit; preserve placement.
- validation.json, edit-validation.json, mesh-validation.json: evidence.

Pinned FreeCAD Python runs build.py, verify_export.py, verify_edit.py; show.py runs
in GUI. settings.json holds mm/degree parameters. wide_sweep.py constructs the
one-sided section growth; wide_carrier_features.py exposes BandExtra. Root width
is stored in SweepJSON; arbitrary width changes require junction review.
Inspection arm/path objects are snapshots and do not update on native control edits.
Previous versions and release retained. No printer submission or commit.
