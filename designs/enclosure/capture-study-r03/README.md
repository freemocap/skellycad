# Capture study R03: elevated corner cameras

R03 preserves R02 and restricts the four corner optical centers to **250–300 mm
above the interior floor**, or 50–60% of the 500 mm clear height. The restriction
applies both to the initial sweep and independent pose refinement. The top
camera remains at 450 mm. Add 20 mm for coordinates in the original CAD frame.

The revised search selects all four corner cameras at 300 mm, aimed at
(250, 250, 260) mm. Under the existing idealized assumptions, qualifying pairs
cover 100% of sampled floor and lower-200-mm points, and approximately 99.19%
of full-cube points. Sampling does not prove continuous coverage or physical
tracking accuracy. Keep the acute ray-angle test: height alone does not guarantee
a well-conditioned camera pair.

The camera frustums have distinct colors: C1 blue, C2 orange, C3 purple,
C4 teal, and Top gold. The default FreeCAD view shows their translucent surfaces
and colored edges. Combined overlap objects are available but hidden initially
so their green overlay does not obscure individual colors.

The [R02 method](../capture-study-r02/README.md) and
[research](../capture-study-r02/RESEARCH.md) describe the unchanged mathematical
model, hardware limitations and validation scope. R03 uses the same scripts and
output names with `capture-study-r03` replacing `capture-study-r02`. Run
`optimize.py`, then `report.py`, then `build_cad.py` with the runtimes documented
there. `study.json` holds the height limits and search ranges. The native model
is `generated/enclosure/capture-study-r03/capture-study-r03.FCStd`.

`open.FCMacro` reuses an already-open copy of that exact file or opens it once,
then raises FreeCAD and records the visible review state in `desktop-review.json`.
The selected review remains open for the user; isolated build documents close
after successful saves. R01 and R02 outputs are preserved.
