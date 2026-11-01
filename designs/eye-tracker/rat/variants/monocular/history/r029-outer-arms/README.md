# Rat R29: outer protective supports

**Rejected on 2026-10-28:** The two arms cross. R29 did not check pairwise arm interference before fusion. Use R30 for the corrected, explicitly separated supports.

R29 reroutes both supports outside the existing ribbon curve. R28 had clearance but put the supports inside that curve, leaving the ribbon exposed behind them. R29 uses the rearward R27 routing principle with two separated tray roots and socket attachments. Camera position, optical axis, ribbon, anatomical model, baseplate and C01 clip are retained from R28.

The two smooth Bezier lofts have chamfered rectangular sections, 3.0 mm wide at their roots, tapering to 2.6 mm, with 1.8 mm thickness. They embed into the tray and collar. Their exact control points and static checks are in `recipe.json`. The single-arm R27 and two-arm R28 checkpoints remain unchanged. The historical species selector still points to R01; it is not the geometry input for this revision.

Minimum individual arm/ribbon gaps are 1.231 mm and 1.305 mm. The finished carrier has zero positive intersection with the ribbon, holder, clip, sensor PCB or lens. Connector and cap contacts are inherited. The carrier is one valid solid and its exported mesh is closed without detected self-intersections. No skull surface crossings were detected; 3,000 carrier samples are outside each eye envelope. These are static checks, not a full motion sweep or physical stiffness test.

Run `build.py` with the pinned FreeCAD Python from the repository root, then `check_eyes.py` with the tooling Python. Use the CLI native listener to submit `show.FCMacro`. The current review is **Rat R29 - outer protective arms**. The macro saves the review, preserves a frozen checkpoint on first review, and saves then closes superseded task-owned R28 comparison tabs. Unrelated documents remain open. The accepted checkpoint and hash are in `review.json`.
