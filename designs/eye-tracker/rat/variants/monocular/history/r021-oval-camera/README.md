# Rat R21: level camera and oval supports

R21 prioritizes a horizontal **long edge of the camera PCB**. Its elevation in
the registered skull frame is -0.066 degrees, compared with approximately
-53.3 degrees in R20. The lower support now leaves the main PCB frame parallel
to the upper support (+Z in the hardware frame), forming a paired oval around
the ribbon instead of the backward loop. The arms retain their rectangular
sections and socket interfaces; their handle lengths are recorded in `arms.json`.

The lens still aims through the right-eye center (0.00018 mm numerical miss).
The changed pose is 20.916 degrees from the opposing neutral eye axis, at a
20.839 mm lens-to-eye-center distance. This is a tradeoff from R20's nearly
coaxial pose: leveling the PCB takes priority in this candidate. The bounded
local search does not establish that exact level/coaxial alignment is impossible.
The three-bend ribbon retains its original 32.85 × 4 × 0.25 mm dimensions.

## Validation

Both arms engage the tray and socket. Full-solid ribbon checks detect no
positive overlap with the checked fixtures or camera components. Ribbon-to-arm
clearances are 0.865 mm above and 1.264 mm below. The carrier is one valid solid;
its mesh is closed and has no detected self-intersections. Matched-part checks
pass, and the cap/connector overlaps inherited from R20 have not increased.

`r20-comparison.json` confirms unchanged main PCB, connector, tray, cap, baseplate
and anatomy, and rigid movement of the complete camera head and socket. The
baseplate also has zero Boolean difference from R17. No hardware/skull or
hardware/sclera surface crossings were detected; 6,600 sampled hardware points
lie outside each whole-eye envelope. The anatomical skull is open, so skull
containment is not asserted. Static checks do not demonstrate physical fit,
clearance through the full ball-joint range, or ribbon fatigue life.

## Rebuild and review

Read `docs/development.md` and `docs/eye-tracker-targeting.md`. Run `build.py`,
`compose.py`, `check_interfaces.py`, and `compare.py`, in order, with the pinned
FreeCAD Python runtime from the repository root. Run `check_containment.py`
with the tooling Python. Use the saved `solution.json`; the exploratory search
scripts are not part of reproduction. The four-zone trial was not selected.

Open `open.FCMacro` through the existing desktop listener; it reuses a matching
tab. `finish.FCMacro` shows the oblique review. `review.json` identifies the frozen
complete assembly; `candidate-manifest.json` records its matched parts. R20 is
preserved. Historical selected R01 still has the pre-existing hash mismatch
recorded in R19 and is not a geometry input here.
