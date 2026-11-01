# Open camera supports R40

R40 replaces R39's enclosing arm pairs with one wider rear cantilever per camera.
The camera poses, matched holders, clips, sockets, ribbon routes, skull, eyes,
forward baseplate placement and 1.8 mm PCB-support plate are preserved. R39 is
retained as the complete source assembly, selected and hash-verified through its
review manifest. The historical species selector remains unchanged.

Each cantilever attaches to the positive-X side of its socket in the corresponding
camera frame. A camera-access box extends from X -7.5 to +7.5 mm, Y -1.5 to
17.5 mm, and Z -6.8 to +8 mm. New support material must stay outside this box;
the pre-existing socket is excluded from that new-material check. This constraint
keeps the camera body and front access region out of the supporting structure.
The deleted lower arms are not present in the new native document.

The beam has a 3.4 by 2.3 mm nominal middle section, flaring to approximately
4.96 by 2.72 mm at the carrier and 4.12 by 2.66 mm at the socket. Root junctions
have 0.4 mm fillets; socket junctions have 0.2 mm chamfers. The RAT R40 label uses
the existing rail region. Functional openings are not changed for the label.

Run `arms.py`, `fillets.py`, `finish_missing.py`, and `label.py` with the pinned
FreeCAD Python from the repository root, after preparing the source document and
matched geometry from the hash-pinned R39 review. `check_label.py` uses tooling
Python to check the bounded engraving edit. `validate.py` uses FreeCAD Python
for camera symmetry, fixed interfaces, solid clearances, camera access, arm
engagement, mesh integrity and skull crossings. `check_eyes.py` uses tooling
Python for sampled eye containment. Reports are in
`generated/eye-tracker/rat/open-supports-r40/`.

`open.FCMacro` opens the complete validated assembly in the existing FreeCAD
session, saving and closing obsolete rat task documents. The result remains a
review candidate. Physical strength, ribbon handling and assembly access still
require a physical trial; no R40 print pack is released here.
