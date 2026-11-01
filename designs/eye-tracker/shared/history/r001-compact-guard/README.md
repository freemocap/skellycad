# Compact lower ribbon guards

Mouse R12 and rat R08 move the lower guard root from the rear plate face to the
front plate edge, below the ribbon. Both keep a broad rectangular guard section:
2.6 × 1.8 mm through the body, transitioning to the existing 3.0 × 2.2 mm socket
terminal. The front root matches the plate thickness, approximately 1.58 mm.

The mouse uses three Bezier spans to turn below its different ribbon route;
the rat uses two. Parallel-transported rectangular sections distribute the
terminal twist along the route. Each span is lofted separately to avoid an
interpolation artifact at span boundaries. Recipes contain the exact root,
turn points, handle lengths and inherited socket frame, all in millimetres.

The camera, ribbon, upper arm, skull, eyes and optical axes retain their poses.
The existing tray, socket and upper-arm material is protected when removing the
old guard. The finished carrier retains the existing junction finishing outside
the removed guard; the new root uses the constant-section lead, without an added
cosmetic fillet. The complete assemblies preserve their matched holder, cap,
clip and baseplate.

## Validation and limits

The guard is checked against the finite-thickness ribbon and camera hardware.
Root and socket engagement must have positive volume. The finished carrier must
be one valid solid. Mesh export requires a closed mesh with no detected
self-intersections. The rat passes that export check. The mouse native solid
is valid, but its tessellation has surface crossings around the curved guard;
its print export is withheld and it remains a CAD review candidate. Fixed interface material and unchanged part shapes are checked
separately. Guard/skull and guard/eye surface crossings are also checked.

Recorded static guard-to-ribbon gaps are approximately 0.82 mm for mouse and
1.28 mm for rat. The mouse target was reduced from an exploratory 1 mm to 0.75 mm
to keep the turn compact; its actual minimum is recorded in validation.json.
These are rest-position clearances, not demonstrated ribbon motion envelopes,
material flexibility, fatigue or physical fit. Guard-to-holder gaps are also
recorded because that moving interface must remain free.

Existing tray/ribbon, connector/carrier and lens-holder interference remains in
the source assembly. This revision introduces no new Boolean overlap with the
checked camera hardware; it does not release the whole assembly for printing.
The carrier STL is for geometric review, not a replacement matched print pack.

## Rebuild and inspect

Read `docs/development.md` before CAD operations. With the pinned FreeCAD Python,
run `build.py` with the mouse `compact-guard-r12/recipe.json` or rat
`compact-guard-r08/recipe.json`. Source and active-model hashes are verified before
changes. Outputs go to the corresponding folder under `generated/eye-tracker`.
Run `check_anatomy.py mouse` or `check_anatomy.py rat` with the same runtime.

For a fresh desktop review, copy the generated native file to the `-final.FCStd`
filename used by `open.FCMacro`, then send that macro through the existing-window
pipe. Do not overwrite a file still open in FreeCAD; use a fresh review filename
for another iteration. Save the reviewed document before freezing its native
checkpoint and SHA-256. Species `review.json` files identify the frozen complete
assemblies; active-model selections and accepted checkpoints are unchanged.

This change uses local geometry and the user's sketch; it introduces no external
engineering source. The separate mouse skull landmark study remains independent.
