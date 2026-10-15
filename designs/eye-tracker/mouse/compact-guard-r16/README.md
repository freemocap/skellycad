# Compact back loop — R16

R16 brings the R15 back loop inward. Its outer control point moves from X=-12 to X=-8 mm; the actual outer envelope moves inward 3.84 mm. The root, socket terminal, 2.6 x 1.8 mm body section, camera alignment, neutral joint, ribbon route, upper arm and anatomy are preserved.

The loop clears the ribbon by 0.69 mm and holder by 1.09 mm. Solid checks show no new interference, preserved protected attachment material and one valid finished carrier solid. The carrier mesh is closed with no detected self-intersections. Guard/anatomy surface checks pass. Static geometry validation does not establish full joint motion clearance or physical fit.

`recipe.json` pins the R15 source hash and parameters. Rebuild with the pinned FreeCAD Python runtime and `designs/eye-tracker/shared/compact-guard-r02/build.py`, passing this recipe. Follow `docs/development.md` for runtime setup and existing-window review. Run this directory's `check_anatomy.py mouse` after building, then open `open.FCMacro` through the verified desktop pipe. Freeze only after the final GUI save and passing checks. `review.json` identifies the frozen native checkpoint; the selected active model remains unchanged.
