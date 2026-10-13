# R05C: rear arm attachment around the socket collar

Candidate for physical review, based on R04B. The user requested moving the rear
arm attachment around the socket stem instead of forcing every route to meet the
same point. R04 and the frozen R02 release are preserved.

## Geometry and controls

- `AttachmentAngle`: 30 degrees about the existing socket axis, toward the lower
  ribbon loop (negative global Y). Only the rear attachment moves.
- `ExtraDrop`: 1.25 mm, inherited from R04B. This offsets interior control points;
  because the socket endpoint now moves too, it is not an absolute midpoint drop.
- First four quintic Bezier control points retain the R04B route. The last two
  move with the new attachment position and inward radial tangent. Socket-side
  handle length stays unchanged. No mesh wiggles are fitted into the curve.
- Collar R3.1 mm; rear terminal section 3.0 x 2.2 mm; existing R0.3 junction blend.
  Terminal section corners stay within the collar envelope.
- Top arm, socket pose/cavity, holder, clip, cap, baseplate and tray construction
  remain as in R03/R04. No change to the ball/neck or PCB seating geometry.

`attachment_sweep.py` computes the rotated radial vector and last two poles.
`sliding_attachment_features.py` exposes AttachmentAngle on the native feature.
`settings.json` stores units and the candidate controls. Tested angle edits are
25 and 30 degrees at ExtraDrop 1.25 mm; arbitrary combinations are not certified.
The inspection-only arm/path snapshots are build-time snapshots; after editing
native controls, use the final carrier feature to inspect the current geometry.

## Validation

Pinned FreeCAD 1.1.4 builds one valid carrier and passes the deep shape check.
Minimum carrier/holder gap remains 0.331721863 mm; holder and baseplate overlap
are zero. Top-arm and tray boundary samples remain contained. The inherited
0.001611788 mm3 cap contact remains unchanged. These are assembled-pose checks,
not a full camera motion or flexible-ribbon simulation.

Fresh reopen and angle edit 30 -> 25 -> 30 degrees passes and restores volume.
Carrier volume is 1225.096812 mm3, 4.280928 mm3 above R04B. The comparison shows a
more direct collar approach. Physical ribbon routing still needs a print check.
No claim of measured strength improvement or verified ribbon clearance is made.
Whole coincident-carrier Boolean differences were unreliable in the R04 study;
we use shared unchanged construction, sampled containment and local interference
checks instead of treating those differences as proof.

## Files and replay

Outputs: `generated/mouse-hats/rear-attachment-r05/` (relative to playground).
- `r05c-carrier.FCStd`: native source-backed candidate, final RibbonClearanceCarrier.
- `r05c-assembly.FCStd`: assembled snapshot of all five parts.
- `rear-attachment-review.FCStd`: grey R04B / cyan R05C display comparison only.
- `R05C-carrier-and-holder.stl`: print-in-place unit, two separate closed shells.
- `mouse-hats-r05c-print-test.zip`: unit, unchanged accessories, notes and evidence.

Run build.py, verify_export.py and verify_edit.py with the pinned FreeCAD Python
under `.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/` from the playground.
Run show.py inside the existing FreeCAD GUI. Run package.py with the analysis
Python at `tools/cad/.venv/Scripts/python.exe` after the comparison image exists.
No printer submission or frozen-release update is performed.
