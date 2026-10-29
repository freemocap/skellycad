# Sensor-head routing checkpoint

The R10 head routing passes native KiCad checks with zero violations and zero
unconnected items. The checkpoint is
`checkpoints/2026-10-28-r10-head/`, relative to this design directory.
Its working source is `generated/ov9281-r10-head-17/`, relative to the repository
root. This is completion of corrective checklist item 3, not a fabrication release.

## Verified copper

| Pair | P planar length, mm | N planar length, mm | Difference, mm | Layers | Vias per conductor |
| --- | ---: | ---: | ---: | --- | ---: |
| Data 0 | 8.146649 | 8.146992 | 0.000344 | F | 0 |
| Clock | 8.100381 | 8.100381 | less than 0.000001 | F | 0 |
| Data 1 | 11.531682 | 11.531682 | less than 0.000001 | F and B | 2 |

These lengths come from native pad-to-pad centerline paths. They exclude via
barrels, sensor/package travel and solder contacts. Whole-link matching remains
checklist item 5. Each head pair meets the 0.254 mm geometric difference budget
used for this review [@esp32P4PcbLayout].

All 149 pad-to-net identities match the R09 routing checkpoint, and every net's
pads form one connected group. The sensor position, optical datum and flex-pad
mapping remain unchanged. L1, L2, R9 and C20 moved on the back to provide routing
space. Their mechanical representation must be updated in item 7.

Both dedicated reference planes remain single connected copper regions, with
no signal tracks on In1 or In4. Data 0 and clock have complete sampled reference
coverage. Data 1 crosses reference voids at its through-via transitions; every
uncovered centerline sample lies within 0.45 mm of its own transition. This is
an explicit geometric neighborhood screen, not proof of a broadband return path.
Each signal transition has at least two ground vias within the project's 1 mm
search radius. The nearest return planes are In1 for F and In4 for B.

## Pairing and guards

The normal paired runs use 0.100 mm tracks and a 0.350 mm edge gap. Sensor
escapes, connector tapers and short length adjustments depart from that uniform
cross section. Data 1 uses matched front-to-back transitions and a short back
escape. Its adjustment is outside the neighboring supply-via clearance region.
Clock matching occurs near the connector, away from the crowded sensor escape.

The clock has explicit 0.100 mm ground guards along both sides of its main run,
connected to ground planes through stitches and the grounded flex pads. Their
nominal edge clearance is 0.101 mm. The finite-width straight-section model gives
94.729 ohm at the finest grid, within the selected 100 ohm +/-10% target
[@esp32P4PcbLayout]. `clock-guard-sections.json` records the three grid sizes and
comparison cases. This supplements the 0.350 mm guard-clearance case in
`STACKUP.md`; it does not change track width, pair gap or construction.

The solver does not simulate the complete channel, bends, pads, transitions or
fabrication variation. Manufacturer impedance control and physical channel
testing remain separate requirements. Native DRC and five cross-section solver
tests pass; no camera hardware has been tested.

## Review scope

The saved native boards and original source hashes were checked on 2026-10-28.
The published layout and stackup sources retain the review scopes recorded in
`STACKUP.md` and the preceding interconnect audit. Freerouting was also tried
for support wiring [@freerouting250]; those experimental outputs were not selected.
The selected checkpoint uses native-geometry routing and local connection repairs.

The controller and flex still need their scheduled corrective routing. The
existing FreeCAD R05 assembly contains older copper and remains a separate
mechanical reference until item 7 produces a new matched assembly.
