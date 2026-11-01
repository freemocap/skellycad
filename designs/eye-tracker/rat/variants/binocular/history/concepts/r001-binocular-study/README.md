# Binocular rat concept study R01

Three FreeCAD mock-ups compare a back-to-back board layout. This is a concept
study, not a print revision. Monocular R03 and print pack R04 are preserved.

| Option | Bare-board back gap | Closure concept | Main tradeoff |
| --- | --- | --- | --- |
| A | 2 mm | Shared top-down clip bonnet | Compact; snap geometry and access need development |
| B | 3 mm | Shared bonnet with transverse bolt envelope | Initial recommendation; positive retention with extra hardware |
| C | 4 mm | Independent covers | Separate service access; more width and parts |

The original camera and cradle are retained on the right. The left lens position
and optical axis are exact reflections across the skull midplane, with a proper
rigid camera rotation. Both nominal optical rays meet their eye centers at
19.885 mm. No real camera or PCB mesh has been geometrically mirrored. The left
board is turned 180 degrees around its short in-plane axis, making the ribbon
exit from the opposite end. Its connector turns with it.

The left camera's handedness means that exact mirrored optical placement does
not imply exactly mirrored mechanical routing. The second cradle and socket
move together with the physical camera. Their local mating geometry is retained.
The support mock-ups use rectangular sections and connect toward these socket
locations. These paths are illustrative; junctions, rigidity, fixture clearance,
and preservation of the preferred monocular arm contours still need design work.

The center is an open edge frame, not two solid tray back walls. The stated gaps
are between the modeled bare PCB backs. Component protrusions, solder joints,
electrical insulation, cooling, and connector/cable access have not been qualified.
A larger gap alone does not demonstrate adequate cooling.

Orange lines are route guides, not fitted ribbons. They do not enforce the
32.85 mm free length, endpoint tangents, bend radius, width, twist, or collision
constraints. Do not infer feasibility from the line drawings. Existing measured
ribbon limits must gate the next design iteration.

The cover volumes indicate removal direction and overall envelope. The bolt is
a nominal 2 mm cylinder with a 2.3 mm concept bore, not a selected M2 fastener.
Head, nut pocket, wall strength, tool access, and tightening loads are unresolved.
Snap blocks indicate candidate latch locations; they are not working springs.
The open frame also needs a designed junction to the retained skull baseplate.

## Review and next iteration

Run `open.FCMacro` through the existing FreeCAD window workflow. Blue supports
belong to the right camera, orange supports to the left. The translucent covers
can be hidden to inspect the green boards and open center. Generated documents,
images, and `study.json` are under `generated/eye-tracker/rat/binocular-study-r01`.

Start detailed development with B: settle the board spacing and exposed connector
access, solve both full-width ribbons with both cameras constrained to these eye
poses, then adapt the accepted monocular arm curves around the routes. Design
the frame/baseplate junction and cover fastener only after this packaging works.
Use A or C if size or independent servicing becomes the stronger priority.

Rebuild with the pinned FreeCAD Python executable and this directory's `build.py`
from the repository root. It verifies the selected rat checkpoint and the R03
source hash. `study.json` records proper camera poses, optical aim, board gap,
and limitations. No collision-free assembly or printability is claimed.

The study uses existing local geometry and design assumptions, without new
external technical sources. Documentation follows the repository's technical
writing guidance.
