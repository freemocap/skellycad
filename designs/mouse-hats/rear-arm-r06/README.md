# R06A - leading-edge rear root and wider ribbon loop

R05C printed feedback: improvement, but ribbon spring needs more outer space and
rear arm root can move to the camera-facing end of the PCB tray.

## Change

Root moves +4.50629685 mm along global Z. Its front boundary is now flush with
tray Z=17.76629685 mm. Root section stays 2.6 x 2 mm and leaves along -X,
perpendicular to the tray back. The two internal root edges receive R0.5 blends;
the lower and front boundaries remain flush. RootForward is a leading-edge datum,
not a freely tested adjustment: moving it also requires reviewing root fillet edges.

First two Bezier poles move with the root. Interior poles 2 and 3 move -2.4 mm
along X, giving an additional 1.5 mm outward reach at the curve midpoint. The
loop compresses along board length while opening outward. OuterBulge is editable;
1.25 and 1.5 mm were tested through fresh reopen/edit/restore.

R05C's 30 degree socket attachment, socket/ball fit, upper arm and other parts
are unchanged. No ribbon model or measured ribbon clearance is claimed.

## Validation

One carrier solid passes deep FreeCAD checks. Minimum holder gap: 0.331721863 mm.
Zero holder/baseplate overlap. Top arm and tray boundary samples remain inside.
Inherited cap contact stays 0.001611788 mm3. Volume: 1221.825214 mm3, down 3.271598
mm3 from R05C. No strength claim is inferred from these geometry checks.
Top and side comparisons visually inspected; physical ribbon fit is pending.

## Files and replay

Outputs: generated/mouse-hats/rear-arm-r06/ relative to the playground.
- r06a-carrier.FCStd: native source-backed carrier, RibbonClearanceCarrier final.
- r06a-assembly.FCStd: five-part assembly snapshot.
- rear-attachment-review.FCStd: display-only grey R05C / cyan R06A comparison.
- R06A-carrier-and-holder.stl: two-shell print-in-place unit; keep relative placement.
- validation.json, edit-validation.json, mesh-validation.json: check evidence.

Run build.py, verify_export.py and verify_edit.py using the pinned FreeCAD Python.
Run show.py in the live FreeCAD GUI. Parameters have mm and degree units in
settings.json. forward_sweep.py constructs the route; forward_carrier_features.py
builds the carrier; forward_root_edges.py selects the leading-edge root blends.
Inspection arm/path objects are build-time snapshots, not live after control edits.
Prior candidates and frozen release remain intact. Accessories are unchanged.
No printer submission is performed.
