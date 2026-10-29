# Controller routing checkpoint

Corrective checklist item 4 is complete. The selected working source is
`generated/ov9281-r10-controller-16/`, relative to the repository root. The saved
checkpoint is `checkpoints/2026-10-28-r10-controller/`, relative to this design.
Native KiCad reports zero violations and zero unconnected items. All 316
controller pad/net identities match the R09 source, and every net's pads are
connected. The verified sensor-head board is unchanged from item 3.

## Verified pair geometry

| Pair | P planar length, mm | N planar length, mm | Difference, mm | Layers | Vias per conductor |
| --- | ---: | ---: | ---: | --- | ---: |
| Data 0 | 19.631358 | 19.631358 | less than 0.000001 | F and B | 2 |
| Clock | 16.546709 | 16.546709 | less than 0.000001 | F | 0 |
| Data 1 | 18.046418 | 18.046418 | less than 0.000001 | F and B | 2 |

Lengths are measured from the saved native copper between U101 and J102. They
exclude package travel and via barrels. Pair differences satisfy the selected
0.254 mm geometric budget [@esp32P4PcbLayout]. Whole-link matching, including
the flex, remains item 5; matching this board alone does not close that budget.

The main runs use 0.100 mm tracks and a 0.350 mm edge gap. Short pad launches,
via tapers and compensation bends depart from the uniform cross section.
The clock has explicit ground guards at 0.101 mm edge clearance, including
around its local compensation bend. The guard calculation and its limits are
recorded in `clock-guard-sections.json` and `HEAD-ROUTING.md`.

Every signal transition has two ground return vias within the 1 mm screening
radius. In1 and In4 each retain one connected ground region, with a filled area
of 553.236273 mm². No signal tracks occupy those reference layers. Every sampled
reference void is within the documented 0.45 mm transition neighborhood; the
clock has no uncovered samples. These geometric checks do not replace a full
channel model, fabrication acceptance or hardware measurements.

## Support-component changes

The processor and connectors retain their original positions. Five support
components moved to make room for the coupled paths and viable pin escapes:

| Component | Position, mm | Side |
| --- | --- | --- |
| Q102 | 9.00, 2.50 | B |
| R112 | 24.00, 11.00 | B |
| R115 | 24.00, 12.00 | F |
| C131 | 16.50, 2.75 | B |
| C132 | 12.75, 4.25 | B |

R115 changed sides, and C131 changed orientation. Item 7 must regenerate their
mechanical representation from this native board. Support wiring was repaired
around the protected pairs, with reference clearance checked again after new
vias were added. A temporary USB chip-side repair maintains connectivity; the
complete controlled USB route is still item 6.

## Evidence and scope

`controller-routing-validation.json` contains native path measurements,
reference sampling, transition checks, source hashes and connectivity results.
`checks/controller-drc.json` is the final native DRC report. The nearest-point
search helper passed its exhaustive-distance comparison tests.

Review date: 2026-10-28. This review uses the source scope already recorded in
`STACKUP.md`. No hardware has been built or tested, and this checkpoint does not
authorize fabrication. The older assembly and FreeCAD R05 view are not matched
to these component moves; the matched review is scheduled for item 7.
