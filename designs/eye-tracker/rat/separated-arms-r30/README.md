# Rat R30: separated protective arms

R30 corrects the crossing arms in rejected R29. The upper tray root now routes to the corresponding upper-side socket attachment; the lower root uses the other side. Both supports stay outside the unchanged ribbon route. Camera placement, lens axis, skull, eyes, baseplate and C01 clip are preserved.

Unlike the R29 checks, the build checks the two individual arm solids before fusing them into the carrier. It requires zero arm-to-arm overlap and at least 0.3 mm clearance between free spans after excluding the tray and socket interiors. The measured free-span clearance is 0.560 mm. Ribbon gaps are 1.231 mm and 1.296 mm. Root width is 3 mm, tip width is 2.2 mm, and thickness is 1.8 mm. Both arms have positive engagement at the tray and collar.

Static checks also cover ribbon and camera-component intersections, valid single-solid carrier, closed export without self-intersections, skull surface crossings and sampled eye containment. They do not establish physical stiffness or full ball-joint travel. Inherited connector and cap contacts remain recorded in `recipe.json`.

Run `build.py` using the pinned FreeCAD Python, then `check_eyes.py` with the tooling Python. Submit `show.FCMacro` through the verified existing native CLI listener. The macro saves the current review, preserves its initial checkpoint, and saves and closes the superseded task-owned R29 view. R29 remains preserved as a rejected design record; it must not be reused as an approved support layout. The historical species selector still names R01; the verified source for this revision is explicitly recorded in `recipe.json`.
