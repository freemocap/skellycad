# Clear eye views and paired rear supports R41

R41 corrects the rejected R40 review. It requires two supports per camera and
keeps ribbons and printed supports out of each lens-to-eye viewing region.
R40 remains the hash-pinned source complete assembly; the historical species
selector remains unchanged. Dimensions are in millimetres.

The camera search preserves symmetric lens locations and viewing directions,
while permitting opposite camera roll. The selected route uses the existing
32.85 by 4 by 0.25 mm cylindrical-bend ribbon model, with a minimum 3.5 mm inside
radius. An alternate half-turn roll search was also attempted; that attempt did
not satisfy the aim constraints. This does not prove that all such alternatives
are infeasible.

The left printed holder, clip and retained socket are mirrored together across
the camera's longitudinal centre plane, placing the stem on the other side.
Camera electronics are rigidly repositioned, never reflected. The board mounts,
skull baseplate, skull and eyes are unchanged. The PCB-support thickness remains
1.8 mm. Functional openings are not changed for revision text.

The viewing check starts just beyond the physical lens front. Its truncated cone
runs from a 1.5 mm aperture radius to a 5 mm radius at the eye centre, with an
additional 0.75 mm clearance used for acceptance. This explicitly checks the eye
viewing region; it is not a calibrated full-sensor field of view. The original
R40 left ribbon intersects the unpadded region, while the revised ribbons do not.
`view-comparison.json` records this comparison. Hidden native clearance objects
allow the checked regions to be inspected in FreeCAD.

Both supports approach each socket from behind the camera. A separate camera
access box excludes support material from the body and front-access region.
The left lower root moves 1.5 mm outward along existing carrier stock to clear
the PCB edge. The four roots and socket ends have flared sections and finished
junctions.
Geometry checks do not establish physical ribbon handling, joint strength or
assembly fit; those remain untested.

Build from the repository root with the pinned FreeCAD Python: `place.py`,
`arms.py`, `fillets.py`, `finish_missing.py`, and `label.py`. `place.py` reads the
recorded numerical search candidates; it does not rerun search. `arms.py` resumes
its working document and arm records when present, so preserve prior output and
use a fresh output directory for a complete rebuild. Run `check_label.py` with
tooling Python, `validate.py` with FreeCAD Python, and `check_eyes.py` with tooling
Python. Stop on any failed check. `open.FCMacro` requires the final validation
reports and opens the matched complete assembly, saving and closing obsolete
rat task documents. No print pack is released by this revision.
