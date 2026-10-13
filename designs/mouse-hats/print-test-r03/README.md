# R03 - first-print socket corrections

User's R02 print looked good overall. Ball/socket fused, and freeing the ball
broke its neck; arm/socket connections also need strengthening. These are physical
observations, superseding the R02 package's then-untested status. R02 stays frozen.

## Changes

- Socket arm ends: 2.4 x 1.8 -> 3.0 x 2.2 mm (53% more section area).
- Collar outer radius: 2.701637 -> 3.1 mm. Same 3 mm height and insert bore.
- Smooth lofts transition into the thicker ends; straight leads extend to the
  wider collar. Broad arm routing and flush tray-root dimensions are retained;
  the final routing control point shifts locally to accommodate the larger collar.
- R0.3 arm/collar concave blends retained; R0.2 collar/bowl concave blend added.
- Subtract R2.35 sphere at the existing ball center, for nominal 0.35 mm radial
  clearance to the unchanged R2 ball. Do not globally scale the socket or holder.
- Actual minimum holder/carrier gap: 0.121146 -> 0.331722 mm at assembled print pose.

Settings with mm units are in settings.json. StrongerClearanceCarrier exposes
SocketArmWidth, SocketArmThickness, CollarRadius and BallClearance. These are
coupled dimensions: failed recompute requires reviewing fit/fillets, not exporting
stale geometry. BallClearance is bounded 0.25-0.45 mm for this candidate.

## Checks

One valid carrier solid and deep shape check; zero holder and baseplate overlap.
No removal from the original tray. Lower neck opening and insert bore unchanged.
Sampled radial bowl-wall minimum 0.915 mm over 120 directions; not a global
minimum-thickness proof. Net added volume 43.979 mm3 (not a measured mass).
Fresh reopen, clearance edit to 0.30, restore to 0.35 all pass.

Isolated exact Boolean testing finds a tiny cap/carrier contact ~0.001612 mm3,
identical in R02 and R03. Earlier zero reports used different Boolean state/
tolerances; this check records the inherited contact rather than hiding it.
No new cap interference is introduced. Existing clip fit qualifications remain.

Mesh validation: carrier+holder STL = two closed, consistently wound shells;
accessories = one each. Clip, cap and baseplate STL hashes match R02 exactly.
The holder and neck are unchanged. Physical strength, release and full motion
still need the R03 print; these changes are not a guarantee against fusion.

## Run / output

Use pinned FreeCAD Python for build.py, verify.py, package.py in that order.
Use show.py in the FreeCAD GUI. Outputs: generated/mouse-hats/print-test/r03.
print-in-place-review.FCStd is the actual assembled unit; socket-section.FCStd
is a non-manufacturing inspection cut. The zip contains the four print inputs,
settings, hashes and notes. Material/nozzle/layer information was requested.

No geometry was changed in R02's frozen release. No print job was submitted.
