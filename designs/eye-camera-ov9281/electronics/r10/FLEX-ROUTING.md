# Flex and complete-link routing checkpoint

Corrective checklist item 5 is complete. The selected working source is
`generated/ov9281-r10-flex-03/`, relative to the repository root. All 48 flex
pad/net identities, contact positions, contact sizes and contact sides are
unchanged. Native KiCad reports zero violations and zero unconnected items.
The verified head and controller boards are unchanged.

| Pair | Complete P planar length, mm | Complete N planar length, mm | Difference, mm |
| --- | ---: | ---: | ---: |
| Data 0 | 63.382424 | 63.382768 | 0.000344 |
| Clock | 63.382597 | 63.382596 | 0.000002 |
| Data 1 | 63.382597 | 63.382596 | less than 0.000001 |

The pair-mean planar spread is less than 0.000001 mm in the saved numerical
geometry. These results satisfy the selected 0.254 mm intra-pair and 0.762 mm
pair-mean geometric budgets [@esp32P4PcbLayout]. This numerical precision is not
a fabrication tolerance. Measurements follow the actual native copper paths;
they do not substitute total copper inventory for connected paths.

## Flex construction and terminations

The B.Cu pairs use 0.100 mm width and 0.250 mm edge spacing. Data 0 and clock
follow offset paths around shared, curved centerlines; Data 1 remains straight.
Contact launches taper from the retained 0.500 mm contact pitch. The F.Cu ground
plane extends beneath both terminations, with a 0.250 mm board-edge setback.
Centerline and 0.450 mm-wide reference-corridor sampling find no uncovered
samples. The exposed outermost 0.250 mm of each finger is outside that plane.

The body is 0.168 mm thick, including finished copper and both coverlays, on the
selected flex construction basis [@pcbwayFlexStackups2026]. The connector tip
remains 0.300 ± 0.030 mm [@hiroseFh34Drawing; @hiroseFh34Catalog]. Removing the
contact-side 0.0275 mm coverlay leaves a 0.1595 mm allocation for the opposite
side's stiffener and adhesive. This is a thickness allocation, not a qualified
stiffener recipe. Both 2.5 mm end regions are designated stiffened; every ground
via remains within those regions. There are no vias in the flexible span.

Clock guards are 0.100 mm wide with a 0.101 mm edge gap. The uniform finite-guard
cross-section calculation gives 96.902 ohms; its mesh results are retained in
`flex-clock-guard.json`. Guards connect to ground at the stiffened ends. Their
high-frequency behavior across the flexible span is not established by a
uniform cross-section solver that assumes equipotential ground.

## What matching does and does not establish

The approved matching budgets are planar. Data 0 has two through-vias per
conductor, Data 1 has four, and clock has none. Estimated barrel additions are
1.012, 2.024 and 0 mm respectively, using the nominal copper-center separation.
`flex-routing-validation.json` reports those additions and illustrative delay
estimates separately. Equal planar lengths do not establish equal electrical
delay. Packages, connector contacts, solder-lap travel, curved sections, actual
dielectrics and assembled bends still require channel and hardware validation.

Review date: 2026-10-28. Source review scope remains the construction and
connector scope recorded in `STACKUP.md`; no new vendor qualification is
claimed. This checkpoint is an offline routing result, not a fabrication
release. USB correction and the matched mechanical review remain items 6 and 7.
