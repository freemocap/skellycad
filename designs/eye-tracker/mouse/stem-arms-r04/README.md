# Stem-supported mouse carrier R04

**Rejected by the user:** the generic round arms discarded the developed arm
design. Use [R05](../restored-arms-r05/README.md), which reuses the historical
rectangular arm generator and makes targeted changes. R04 is not selected.

R04 reconnects the accepted R03 fixed cradle and socket to the PCB tray with two
new arms. The camera PCB, cradle, ball, socket and ribbon retain their R03 poses.
The selected complete assembly remains ET-MOUSE-MONO-R01; R04 is a separate
review revision, not a replacement print checkpoint.

## Design choices

Both arms attach to the stationary cylindrical socket stem, above the ball
housing. They do not attach to the moving ball or cradle. A cylindrical cut
preserves the existing 1.45 mm radius axial bore through the attachment region.

- Upper support: 2.7 mm circular diameter, from the top of the printed PCB tray,
  rising above the ribbon and returning to the socket stem. It supports position.
- Rear ribbon guard: 2.3 mm circular diameter, from the back of the printed tray,
  sweeping behind the ribbon and returning to the stem. Its larger loop leaves
  room around the ribbon rather than clamping it.

The PCB is not a structural attachment. Both arm roots embed into the printed
tray. Cubic Bezier control points and radii are explicit in `build.py` and copied
to `validation.json`. These dimensions are initial geometric choices. Stiffness,
fatigue, print strength, root finishing and snag protection have not been tested.

## Geometry verification

The tray, retained socket and new arms fuse into one valid solid. Each arm has
positive-volume overlap with both its tray root and stem attachment. Full-solid
checks find no new-arm overlap with the modeled ribbon, moving holder, clip,
cap, baseplate or camera components. Minimum modeled ribbon clearance is
approximately 0.873 mm at the upper support and 1.399 mm at the rear guard.

`check_motion.py` rotates the cradle, clip and sensor assembly together about
the inherited ball center. Six independent samples (+/-10 degrees about each
world axis) have no intersection with the new arms. This is not a continuous
motion envelope or a verified adjustment range. The ribbon remains in its
reference shape during these rigid checks and must be re-solved for moving
poses before checking cable clearance throughout adjustment. Existing socket
limits and other retained-part contacts are outside this motion test's scope.

## Rebuild and review

Follow `docs/development.md` and the R03 study's build instructions first.
From the repository root, use the pinned FreeCAD bundled Python to run this
folder's `build.py`, then `check_motion.py`. The build verifies the selected
checkpoint SHA-256 and records the R03 native input hash.

Outputs are in `generated/eye-tracker/mouse/stem-arms-r04/`:
`mouse-stem-arms-r04.FCStd`, `validation.json`, and `motion-samples.json`.
`StemSupportedCarrier` is the fused carrier. The separately colored arm, tray
and socket objects are review components of that same carrier, not additional
parts to print together with it. The review macro hides the fused duplicate.

Open `open.FCMacro` through the existing FreeCAD listener. It checks static
validation before displaying the model. Review arm bulk, ribbon access and
attachment shape before selecting a printable complete assembly with its
matched holder, clip, cap and baseplate.
