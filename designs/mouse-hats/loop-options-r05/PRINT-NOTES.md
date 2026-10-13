# R05: three ribbon-loop space options

| Printed label | Version | Rearward reach from panel back | Curved route length |
|---|---|---:|---:|
| A | Compact, same route as R04 | 11.2 mm | 28.7 mm |
| B | Medium | 14.4 mm | 35.3 mm |
| C | Roomy | 17.6 mm | 42.1 mm |

These measurements describe the arm, not a guaranteed ribbon bend radius or
cable capacity. All three share the new root below the round hole, the same
socket/camera pose, arm sections, PCB catch, raised cap rail and matching cap.
Only the curve's two control-handle lengths differ (13, 18, 23 mm).

The old T +1.0 mm text has been removed from the carrier and common cap.
Carriers now have a single raised A, B or C label, 3.5 mm tall and 0.4 mm relief.

## What to print

- `R05-ABC-comparison-plate.stl`: all three carrier-and-holder pairs, spaced apart,
  with their lowest points at Z=0. Approximately 133 x 24 x 50 mm overall.
- Alternatively, print the three individually named carrier-and-holder STLs.
  Do not print both the plate and individual files unless duplicates are wanted.
- `R05-shared-matching-cap.stl`, `R05-shared-camera-clip.stl`, and
  `R05-shared-baseplate.stl` fit all variants. Print one set to reuse during the
  comparison, or three copies of each for three complete assemblies.

Use 100% scale. Each carrier-and-holder file contains two intentionally separate
watertight shells: the carrier and its ball-mounted holder. Keep their relative
positions; do not split and auto-arrange them separately. The combined plate has
six such shells. Use your established print-in-place settings and inspect support
placement, particularly around the ball/socket clearance. This is an STL pack;
printer, supports, materials and slicing settings are not embedded.

All exported shells pass watertightness, consistent winding and positive-volume
checks. All three carriers are single valid native solids and have no modeled
PCB, holder, clip or baseplate interference. Holder clearance stays 0.333165 mm;
matching-cap contact stays at the inherited baseline. Physical fit, ribbon bend
and movement are the purpose of this print comparison and remain unverified.

Baseline: hash-verified complete MH-T3-EYE-R04, not an older PCB carrier.
The source R04 remains selected until a winning option is chosen. These are
three test alternatives, not three successive revisions.
