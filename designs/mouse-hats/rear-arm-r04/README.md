# R04 rear ribbon-arm options

## Intent and physical feedback

The user supplied five photos (49608/49607/49609/49606/49603), including red
arrows showing the rear arm should sweep behind/below the ribbon as it exits the
sensor holder, then rise back to the PCB tray. Current rear arm crosses too high.
Top arm is to remain as-is. Flexible ribbon simulation is explicitly out of scope;
use physical fit tests. Source photos remain in the user's remote attachments.

## Two bounded options

- A: smooth V5-guided rear sweep. Centerline minimum Y approximately 1.897 mm.
- B: the same path with 1.25 mm additional downward displacement at its midpoint
  (assembly -Y). Centerline minimum Y approximately 0.671 mm.
- Same root/socket endpoints, end tangents and reinforced R03 sections for both.
- Top arm uses exactly the R03 builder/data. Socket collar, cavity, ball pose,
  holder, clip, baseplate and cap remain at R03. This is not a joint-fit experiment.

`settings.json` contains mm units, six Bezier poles and A/B settings.
`fit_guide.py` fits V5 section centers from model/v5-recovered-sections.json.
This is a single degree-5 Bezier, with constrained end tangents and a monotonic Z
control polygon to avoid an extra hump near the socket. It follows the broad
legacy route, not its individual wiggles. Fit RMS ~0.878 mm is relative to the
endpoint-corrected guide, not exact distance to the original mesh surface.

`rear_sweep.py` creates aligned rectangular sections along that curve, using
parallel transport and a smooth minimal end-frame rotation. Straight embedded
ends keep attachments aligned. `ribbon_carrier_features.py` deliberately retains
the R03 socket construction and substitutes only the rear-arm geometry call.

The ExtraDrop control moves only the two interior poles. Their combined weight
at the midpoint is 0.625, so a pole displacement of ExtraDrop/0.625 gives the
specified actual midpoint displacement. A uses 0; B uses 1.25 mm. A trial at
1.5 mm failed deep CAD validity and is not exported. Intermediate settings require
recompute/validation; do not export a failed or stale feature.

## Validation and limits

Both candidates: one valid solid, deep shape check pass, zero holder/baseplate
interference, minimum joint separation 0.331722 mm. Minimum rear-arm-to-holder
distance 1.643347 mm is dominated by fixed end geometry; it is not ribbon clearance.
Top-arm and tray boundary samples all remain contained in each carrier, using
0.001 mm classification tolerance. Shared construction preserves their inputs.
Whole-carrier coincident Boolean subtraction was unreliable and was not used as
proof of unchanged geometry. The validation report explicitly names sampled checks.
Tiny cap contact 0.001612 mm3 is unchanged from R03. No full motion sweep performed.

Each carrier+holder print STL contains two watertight, consistently wound shells.
Accessory STL files remain identical to R03. See validation.json and
mesh-validation.json under generated/mouse-hats/rear-arm-r04.
The separate edit-validation.json records a fresh reopen / A-to-B / restore test.

## Build and use

Run fit_guide.py with tools/cad/.venv Python when intentionally refitting the guide.
Run build.py and verify_export.py with the pinned FreeCAD Python. Optional A/B
argument to build.py builds one variant. Run verify_edit.py to check the control.
Run show.py in the FreeCAD GUI for the three-row comparison. The green V5 rear
mesh reference is hidden by default and can be toggled as an overlay on A.
Comparison offsets are presentation only; never export that display for printing.
Run package.py with the analysis Python after mesh validation.

Outputs: generated/mouse-hats/rear-arm-r04. Both STLs share their assembly origin;
arrange them as separate complete objects if printing both on one plate. Keep the
holder's relative position inside each socket. No printer job was submitted.

## Print-test questions

Use the same material/orientation/support settings for A and B if comparing them.
Check whether the ribbon naturally rests inside the loop, remains clear during
camera adjustment, and gains some protection without being pinched against an arm.
Also compare bulk and support-removal effort. Identify results by A or B filename;
there is no embossed variant mark on these tiny parts.

R03 and the R02 frozen release are retained unchanged. No selection of A/B is
final until the user evaluates the routing on the real hardware.
