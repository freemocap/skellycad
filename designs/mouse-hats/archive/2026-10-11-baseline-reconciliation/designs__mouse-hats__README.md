# Mouse hats: STEP-to-FreeCAD reconstruction

Current scope: faithfully rebuild the supplied 53nassembly.step as a clean,
editable, parametric FreeCAD project. Source:
old/df-hardware/camera-assembly/cad/53nassembly/53nassembly.step

Preserve that STEP unchanged. Its geometry is the baseline for this phase.
Higher-numbered STL files and two-arm variants are NOT part of this phase.
Do not inspect, align, compare or reconstruct them until the user explicitly
resumes that work. No STL scale or mesh-comparison question is pending.

Next: inspect the STEP's components, establish their feature structure and
interfaces, rebuild one component, and compare the rebuilt solid directly with
its STEP reference. Extend to the complete STEP assembly after the first part
has a verified reconstruction method. Importing STEP alone does not constitute
rebuilding its parametric history.

references.json is a preservation inventory of supplied files, not a declaration
that every listed file is a current design target. The earlier mesh-inspection
scripts/results are inactive and must not guide the STEP reconstruction.

User-described functions and uncertainties are recorded in
[docs/functional-map.md](docs/functional-map.md). Functional regions are not yet
assigned to STEP solid IDs; no external hardware sizes have been assumed.

See docs/decisions.md and docs/reconstruction-plan.md. No supplied geometry has
been edited. No replacement part, release, commit or push has been made.
