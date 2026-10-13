# Workflow cube

2026-10-08 — First learning checkpoint: a 20 × 20 × 20 mm parametric box,
with its bottom at Z = 0. Source: build.py and parameters.json.
Native source: 01-cube.FCStd. The script checks one valid solid and 8000 mm³ volume.
Blue is a viewport display color, not a filament assignment.

User has a Snapmaker U1 and Snapmaker Orca on this computer; printer is on the
same LAN. Use PLA for this experiment. Nozzle size, PLA tool assignment, and
slicer settings remain to be checked. Not yet sliced or sent to the printer.

Lesson 2 — 02-link-height.py, run after checkpoint 01, reads 02-parameters.json
and sets FreeCAD's native Height expression to Length * 1.5. Length and width
remain 20 mm; height becomes 30 mm. Saves 02-linked-height.FCStd, preserving 01.
Checks one valid solid, 30 mm height, and 12000 mm³ volume. Default navigation
is retained. Select the block and inspect its Data properties to see inputs
and the dependent Height. Reproduce from scratch by running build.py then
02-link-height.py. No export or print has been performed.

Lesson 3 — User manually changed Length to 24 mm and observed Height = 36 mm.
03-centered-hole.py folds that edit into the recipe using 03-parameters.json,
saves 03-resized-block.FCStd, then subtracts an 8 mm diameter cylinder.
The cylinder center follows Cube.Length / 2 and Cube.Width / 2; its height
follows Cube.Height + 2 mm, extending 1 mm beyond each end for a through cut.
04-centered-hole.FCStd retains the box, cylinder, and dependent Part::Cut.
Checks one valid solid and expected box-minus-cylinder volume. Reproduce by
running build.py, 02-link-height.py, then 03-centered-hole.py in order.

Print-loop lesson — export_mesh.py exports only BlockWithHole from the live
document after checking one valid solid and 24 × 20 × 36 mm bounds. Uses
0.05 mm absolute linear deflection and 0.15 rad angular deflection. Disposable
STL, source metadata/hash, and mesh audit are in generated/workflow-cube/.
Independent inspection found 536 triangles, one connected shell, watertight,
and 24 × 20 × 36 raw STL units (exported as mm). Orca import and printer settings
are not yet checked. No slicing or print was performed.
