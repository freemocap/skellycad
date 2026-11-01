# Orthogonal supports R42

R42 revises the support routing and carrier junctions of the hash-pinned R41
complete assembly. Each camera retains two supports. The camera poses, optical
axes, ribbons, matched holders and clips, socket interfaces, skull and baseplate
remain fixed. Dimensions are in millimetres. The historical species selection
remains unchanged.

The top supports follow planar curves close to the PCB-holder plane. Each rear
support follows a separate planar curve approximately perpendicular to that
plane. The two terminal approach directions at each socket are 90 degrees apart.
The rear routes differ because their fixed ribbons take different paths.

Rounded attachment areas extend the carrier stock at the four roots, within
the existing outer extent. They add 34.56 cubic millimetres and retain 0.35 mm
relief around the fixed ribbons. The top roots start within carrier stock
rather than crossing the top edge and small retention features. Root sections transition into the full beam section;
concave junction blends must pass solid, mesh and collision checks before this
revision can be released for review. Revision text remains within the existing
label rail and does not determine functional openings.

## Rebuild and review

Use the pinned FreeCAD Python for native geometry and tooling Python for numerical
screening and mesh audits. Start from the R41 native document and BREP inputs
identified by `recipe.json`; verify the native checkpoint hash before copying
inputs into `generated/eye-tracker/rat/orthogonal-arms-r42`. Preserve existing
working outputs before rebuilding. The arm builder resumes saved arm records; `prepare.py` creates the initial
working document and empty arm records.

1. Run `prepare.py`, then `candidates.py`, with tooling Python. `prepare.py`
   verifies the source hash and requires a fresh output directory.
2. Run `landings.py`, `arms.py`, then `finish.py`, with FreeCAD Python.
   `landings.py` requires the saved arm working document and preserves it before
   adding the attachment areas.
3. Run `label.py` with FreeCAD Python and `check_label.py` with tooling Python.
4. Run `validate.py` with FreeCAD Python, then `check_eyes.py` with tooling Python.
5. Stop on any failed check. Only after both final reports pass, run
   `open.FCMacro` in the existing FreeCAD desktop session. It saves and closes
   obsolete task-owned rat documents and opens the matched complete assembly.

The eye-view clearance check is inherited from R41. It checks a padded region
between the physical lens front and the eye, not a calibrated full-sensor field
of view. Numerical ribbon clearance and valid CAD solids do not demonstrate
physical ribbon handling, joint strength, adjustment travel or printed fit.
This revision does not release a new print pack.

## Validation result

The final native geometry, closed-mesh, camera symmetry, ribbon and camera-access
clearance, padded eye-view, skull-crossing and sampled eye-containment checks
passed. The arm planes are 86.63 and 88.11 degrees apart; both socket approach
angles are 90 degrees. Carrier roots have 0.4 to 1.0 mm concave fillets; all four
socket junctions have 0.6 mm concave fillets. The matched complete assembly is
identified and hash-pinned by `review.json`. Physical fit remains unverified.
