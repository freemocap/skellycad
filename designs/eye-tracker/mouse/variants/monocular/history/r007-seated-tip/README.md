# R07 upper arm seating correction

R07 supersedes the R06 print-test candidate after desktop review identified an
upper-arm tip projecting above the stationary socket collar. R06 was a valid
fused solid, but that check did not establish correct seating.

The correction removes 6.068 mm³ from the upper terminal only. In the socket's
local frame, the collar top is at axial height 5.4 mm. The terminal now meets
that plane, with a taper rising from radial position 3.1 mm toward the existing
arm. The bore, moving ball, camera pose, ribbon route and other arm junctions
retain their R06 geometry. This is a local top trim; it reduces terminal
thickness from 2.2 mm to approximately 1.2 mm at the landing. Print testing must
establish whether that section has adequate strength.

## Complete assembly and matched parts

`print-test.json` identifies the frozen R07 complete assembly and its SHA-256.
The repository's selected checkpoint remains ET-MOUSE-MONO-R01. R07 is a separate
print-test candidate. Its source is the hash-verified R06 complete assembly;
`prepare.py` also verifies the selected R01 checkpoint before changing geometry.

Generated outputs are under `generated/eye-tracker/mouse/seated-tip-r07`.
The print package contains carrier-and-holder, matching cap, camera clip and
baseplate. Keep the carrier and holder in their exported relative positions.

## Validation and review

The carrier passes the detailed OpenCascade check as one solid. All four print
meshes are closed and have no detected self-intersections. Ribbon overlap is
zero; moving-holder clearance remains 0.333165 mm. The small inherited cap
intersection (0.002218 mm³) is unchanged. `junction.png` shows the corrected
landing in close-up. These checks do not establish physical fit or strength.

The geometry is based on local checkpoint inspection and the user's marked
screenshot; no new external technical sources were used.

## Reproduce

From the repository root, run `prepare.py` and then `export.py` with the pinned
FreeCAD Python runtime described in `docs/development.md`. The export retains
the R05 complete assembly's camera and matched-part placements. Its generated
R05 input must exist. Use `open.FCMacro` through the existing-window procedure
to review the complete assembly; use `closeup.FCMacro` while that R07 document
is active to inspect the landing. After the GUI save, run `package.py` using
the CAD tooling Python runtime to freeze the checkpoint and record its hash.

## Rejected by user

The user rejected the tapered terminal. R08 restores the full terminal thickness and moves its attachment inward, with a revised ribbon route. Do not use the R07 print package.
