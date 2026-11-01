# Restored historical arms R05

R05 replaces the rejected round-tube R04 study. It calls the existing
`designs/mouse-hats/b-flared-loop-r07/flared_arm.py` generator directly with its
historical settings. That source is unchanged. The camera, cradle, ball/socket
and fitted R03 ribbon remain at their existing placements.

## Changes from the historical arm recipe

| Parameter | Original | R05 |
| --- | --- | --- |
| Rear root and socket curve handles | 18 mm (B) | 23 mm (existing roomy C setting) |
| Upper root Y position | 16.091889 mm | 17.591889 mm |
| Upper attachment height along socket axis | 3.9 mm | 5.3 mm |

Everything else in the arm recipe is inherited: rear root position and 25-degree
plugward flare, rectangular sections, transported section orientation, tapered
ends, upper curve handles (5 and 4 mm), root leads and socket-side approach.
Rear body section is 2.6 x 1.8 mm; upper body section is 3 x 1.8 mm.
The upper attachment moves 1.4 mm farther up the stationary stem, and its root
moves sideways 1.5 mm on the printed tray. No round-tube geometry is reused.

The raw historical generator rebuilds the arms; this does not claim that every
post-fusion finishing fillet on the old carrier has been replayed. Root finishing
and physical strength remain review items before selecting a print checkpoint.

## Validation

The exact original arm solids were first recovered by subtracting the retained
R03 tray/socket from the hash-verified selected carrier. With the fitted ribbon,
the original upper and rear arms intersected it by approximately 1.271 and
0.152 mm3 respectively. Those contacts motivated the changes above.

The R05 carrier is one valid fused solid. Both arms have positive-volume overlap
with their tray and socket attachments. Full-solid checks find no intersection
between either arm and the modeled ribbon, holder, clip, cap, baseplate or camera
components. Minimum ribbon clearances are approximately 0.518 mm (upper) and
1.246 mm (rear). These are static geometric checks; physical strength and ribbon
clearance throughout adjustment are not established. R04 motion results do not
apply to R05.

## Rebuild and review

Use the pinned FreeCAD bundled Python from the repository root to run `build.py`
after generating the R03 fixed-cradle study. The build verifies the selected
checkpoint hash and records the R03 input hash. Outputs are under
`generated/eye-tracker/mouse/restored-arms-r05/`.

Open `open.FCMacro` through the existing FreeCAD listener described in
`docs/development.md`. It checks the static validation report before displaying
`mouse-restored-arms-r05.FCStd`. The fused `StemSupportedCarrier` is hidden in
the review because its component regions are shown separately; do not export
both as duplicate print geometry. The selected complete assembly and historical
matched parts remain unchanged.
