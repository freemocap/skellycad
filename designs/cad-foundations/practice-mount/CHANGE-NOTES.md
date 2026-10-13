# Changes

Fillet comparison — Added top_fillet_radius = 0.5 mm and add_top_fillet() in
model.py. fillet_comparison.py rebuilds the plate in PracticeMountFillet and
rounds the original Pocket top edges, preserving the existing chamfer document.
Saved 08-top-fillet.FCStd. Checks valid single solid, unchanged bounds/underside,
four unchanged hole bores, and four 0.5 mm radius cylindrical edge surfaces.
Camera copied from the chamfer document for comparison by switching tabs.

Chamfer lesson — parameters.top_chamfer = 0.5 mm. Select straight edges at
MountingPocket's maximum Z, asserting exactly four; current references Edge4,
Edge7, Edge10, Edge16. Native equal-distance PartDesign::Chamfer creates a 45°
top perimeter bevel. Saved 07-top-chamfer.FCStd. Verified valid single solid,
analytical removed volume, unchanged bounds/underside and four hole radii.
Full model rebuilt in a temporary document and checked at 40×24×3 and 50×32×5 mm;
temporary document closed and original live plate preserved. Selection by geometry
occurs during creation; stored references still need checking after topology edits.

Four-hole lesson — add_opposite_row() adds two equal-radius circles vertically
aligned with the lower circles. UpperLeftY and UpperRightY both follow
PlateOutline.Constraints.PlateWidth - Constraints.CenterY. Existing ThroughAll
Pocket cuts all four. Checked fully constrained sketch, expected centers/radii,
valid single solid, plane height, and analytical removed volume at 40×24×3,
50×24×3, 40×32×3, and 50×32×5 mm. Restored 40×24×3 and saved
06-four-holes.FCStd. Source is model.py; lesson runner is opposite_row_step.py.

Opposite hole — Added a second circle to MountingHole and reused MountingPocket.
Equal radii, horizontal center alignment, and native OppositeX expression keep
matching left/right margins. Validated fully constrained sketch, valid single
solid, equal radii, margins and removed volume at 40 and 50 mm lengths. Restored
40 mm and saved 05-opposite-hole.FCStd. No four-hole pattern yet.

Pocket lesson — add_mounting_pocket() creates PartDesign::Pocket linked to
MountingHole with Type = ThroughAll. pocket_step.py executes just this operation
and saves checkpoints/04-through-hole.FCStd. Checked one valid solid and volume
equal to Pad volume minus pi × radius² × thickness. Previous Pad and sketch
remain editable but hidden; Body Tip is the Pocket. No other features added.

2026-10-08 — Begin sketch lesson with a 40 × 24 mm fully constrained rectangle.
Fix the lower-left corner to make the growth direction easy to predict.
Separate native construction (model.py), input values (parameters.json), and
GUI/save entry point (build.py). Preserve the cube exercise in its own document.

Pad lesson — Added plate_thickness = 3 mm and add_plate_pad() in model.py.
pad_step.py invokes that function on the existing sketch after exiting edit mode.
Native PartDesign::Pad links Profile to PlateOutline; saved checkpoint 02.
Verified one valid solid, 3 mm Z extent, and 2880 mm³ volume. Geometry code shown
and explained before execution; no holes or further features added.

Repair — Restored missing add_plate_pad() to model.py. Rebuilt the sketch and
Pad in a temporary FreeCAD document and verified valid solid, dimensions,
volume, and agreement with the live plate; closed the temporary document.
The existing model and checkpoint were preserved.
