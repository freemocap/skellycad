# Raised mount and re-aimed mouse camera — R19

R19 is the selected complete mouse assembly. It combines the accepted R18 surface-parallel raised baseplate with the R16 compact-loop hardware and R04 anatomical eyes. There is one eye camera in this monocular assembly.

The baseplate, main PCB, tray and cap follow the R18 transform. The camera, socket, holder and clip retain their validated skull-space pose, so the raised mount does not spoil the eye-center aim. Both arms and the ribbon are rebuilt between the relocated tray and the camera joint. This preserves the neutral joint relationship and the compact R16 lower-loop style.

## Validation

The camera ray misses the eye center by 0.000011 mm at 14.694 mm forward distance; the remaining opposing-axis difference is 12.724 degrees, as in R16. Exact coaxial alignment remains limited by the tray geometry; the earlier local pose exploration is documented in R15.

Full-solid ribbon checks pass. Clearances are 0.670 mm at the lower loop, 0.692 mm at the upper support and 2.538 mm at the socket. No new carrier overlap is introduced. The inherited cap overlap (0.002218 mm3) and connector overlap (0.059028 mm3) remain recorded. The carrier is one valid solid, with a closed mesh and no detected self-intersections. Changed hardware has no detected skull/eye surface crossings; 2,500 sampled hardware points show no containment within those anatomical meshes.

The baseplate reproduces R18 geometry and placement within Boolean tolerance. Its conservative rear-hole clearance remains 5.058 mm to the atlas mesh; this does not cover an unspecified protruding screw. The tapered underside remains stock for later contact-surface fitting. Anatomical estimates, static clearance and numerical aim are not demonstrated physical fit or full joint motion clearance.

`selection-validation.json` verifies the shared matched-part checks and R18 baseplate placement. The shared validation/export helpers now use global part placements, so nested camera components are evaluated in the assembly frame.

## Selected assembly and reproduction

`active-model.json` selects the frozen native checkpoint identified by `review.json`. `previous-active-model.json` preserves the former R01 selection; all historical checkpoints remain intact. The selected carrier role maps to `FinishedCarrier`, and the optical-axis role maps to `DetailedOpticalAxis`. The historical `assembly.json` and mouse `build.py` remain R01 replay inputs; the selected manifest points to this revision's build script.

Read `docs/development.md` and `docs/eye-tracker-targeting.md` before CAD work. Rebuild with the pinned FreeCAD Python runtime using this directory's `build.py`; it reads saved `solution.json`, verifies the input and active checkpoint hashes, and writes generated output. `solve.py` and `refine_ribbon.py` are exploratory and overwrite the saved solution if rerun. Run `check_anatomy.py` after rebuilding, then review through `open.FCMacro` in the existing desktop session. Freeze after final GUI save and passing checks. Do not treat a rebuilt file as the selected checkpoint until its hash and validation are recorded.

The standard mouse `open.FCMacro` and `export_print.py` consume the selected manifest and matched-part names. Print export is a separate action; no physical fit is claimed by selection.
