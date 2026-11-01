# Refined rat supports R38

R38 preserves the complete R37 camera-head placement, matched holders, clips,
sockets, anatomy and skull baseplate. Each arm follows its own ribbon route;
arm symmetry is not a requirement. The selected historical species checkpoint
remains R01. `review.json` identifies this complete assembly review and its hash.

The upper arm centerlines are now 27.47 and 27.70 mm long, compared with 42.50 mm
in R37. The lower arms are 41.26 and 45.39 mm long, compared with 50.59 mm, and
follow their respective ribbon envelopes more closely in top view.

The central PCB-support plate is 1.8 mm thick, increased from 1.2 mm. Each main
PCB and its retaining geometry moved outward by 0.3 mm. The camera heads and
skull baseplate did not move. Both ribbon routes retain their 32.85 mm centerline
length and pass the finite-thickness clearance checks. These are relaxed geometric
ribbon models, not demonstrated physical fits or inextensible-sheet simulations.

The arms have gradual flared ends, roots 3.96 mm wide and 2.22 mm thick,
and socket ends 2.92 mm wide and 2.16 mm thick. The longitudinal edges
have 0.2 mm chamfers. All eight junctions have 0.4 mm native fillets and positive
engagement in a valid single carrier solid. The RAT R38 label fits the existing
rail with 0.75 mm edge/window margins; no functional geometry was enlarged for it.

`validation.json`, `containment.json` in the generated output, and the stage reports
record the checks. Camera symmetry, aim and matched head fixtures are retained.
There are no new solid interferences; inherited lens/holder and holder/clip overlaps
remain separately recorded. Meshes are closed without self-intersections. All
19 non-baseplate hardware parts have zero skull surface crossings and zero sampled
eye containment. These checks do not establish physical strength or full adjustment
travel. This revision is a review assembly, not a new print pack.

Rebuild stages with the pinned FreeCAD Python, in this order: `upper.py`, `lower.py`,
`plate.py`, `ribbons.py`, `plate_clearance.py`, `junctions.py`, `visual_route_fix.py`, `fillets.py`,
`finish_missing.py`, `label.py`, and `validate.py`. Run `check_eyes.py` with the CAD
tooling Python. After both final validation reports pass, submit `open.FCMacro`
through `open_in_running.py` with the verified desktop PID. The macro saves recovery
copies and closes obsolete rat task tabs, preserves unrelated work, and opens
the complete R38 skull-frame assembly. `show-top.FCMacro` supplies the settled top
view for routing review.
