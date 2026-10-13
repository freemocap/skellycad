# R09 socket-body attachment study

The user asked to see both arms attached to the body of the ball/socket part instead of its narrow stem. Interpreted as the stationary outer socket housing, preserving the moving ball and holder. This is a visual candidate, not an adopted print revision; R08 remains selected.

Full source is hash-pinned R08 with B2 loop, flat top PCB ledge and vertical side ledge. Both socket endpoints move from axial height 3.9 mm/radius 2.65 mm to height 0.5 mm/radius 3.05 mm about the same socket center and axis. The added stem collar is removed; original socket geometry remains. Plate roots, camera pose and neutral ball clearance stay fixed. Rear root flare remains 25 degrees; rear handles remain 18 mm. The short upper arm handles become 3.5/2.5 mm to avoid self-intersection at the new endpoint. Rear curve length changes from 37.94 to 36.36 mm, so actual ribbon fit may differ.

One valid carrier solid; no holder, clip, PCB or baseplate interference in neutral position. Holder gap remains 0.333165 mm and inherited cap contact is unchanged. Both PCB ledges and raised cap rail retained. Full angular travel and physical strength/ribbon fit have not been checked. New body junctions have no added cosmetic fillets in this study.

Replay build.py in the pinned FreeCAD GUI runtime. settings.json records millimeters and lineage; body_geometry.py/flared_arm.py preserve construction. Open show.FCMacro through tools/cad/open_in_running.py on the desktop to add the candidate and comparison to the existing session without closing its history. Comparison: orange = R08 stem attachment, cyan = R09 body attachment, purple = same moving holder.

2026-10-12: User approved this version for a print-test STL. The unchanged native study checkpoint is now selected in the active manifest; exported through current/export_print.py. Watertight shell checks passed. The earlier non-adoption status above describes the initial comparison stage.
