# MIPI audit — R09 data1p trial 03

All 18 board-level paths pass native connectivity and the centerline graph. All 24 MIPI connector-pin comparisons preserve polarity. This does not qualify signal integrity.

## Whole-link planar lengths

Lengths sum head, flex and controller; connector/package delays and via barrels are excluded. The geometric budget comes from Espressif layout guidance [@esp32P4PcbLayout].

| Pair | P (mm) | N (mm) | Difference (mm) | Within 0.254 mm |
| --- | ---: | ---: | ---: | --- |
| CLK | 56.180 | 57.364 | 1.184 | No |
| D0 | 56.056 | 58.270 | 2.214 | No |
| D1 | 71.236 | 69.853 | 1.384 | No |

The spread of pair mean lengths is **13.772 mm**, exceeding the 0.762 mm inter-pair screening budget. Mean length is our explicitly declared screening convention; neither this number nor individual lengths are simulated delays.

## Board-level evidence

| Board / conductor | Path (mm) | Layers (mm) | Via count | Sampled reference gap (mm) |
| --- | ---: | --- | ---: | ---: |
| head / CLK_P | 6.482 | F.Cu: 6.482 | 0 | 4.410 |
| head / CLK_N | 7.047 | F.Cu: 7.047 | 0 | 3.364 |
| head / D0_P | 7.235 | F.Cu: 7.235 | 0 | 1.792 |
| head / D0_N | 8.554 | F.Cu: 1.783, In2.Cu: 6.771 | 2 | 2.995 |
| head / D1_P | 18.636 | F.Cu: 2.297, In1.Cu: 16.339 | 2 | 17.549 |
| head / D1_N | 19.457 | F.Cu: 8.003, In2.Cu: 11.453 | 2 | 6.108 |
| flex-study / CLK_P | 33.800 | B.Cu: 33.800 | 0 | 1.500 |
| flex-study / CLK_N | 33.800 | B.Cu: 33.800 | 0 | 1.500 |
| flex-study / D0_P | 33.800 | B.Cu: 33.800 | 0 | 1.500 |
| flex-study / D0_N | 33.800 | B.Cu: 33.800 | 0 | 1.500 |
| flex-study / D1_P | 33.800 | B.Cu: 33.800 | 0 | 1.500 |
| flex-study / D1_N | 33.800 | B.Cu: 33.800 | 0 | 1.500 |
| controller / CLK_P | 15.898 | F.Cu: 3.213, In2.Cu: 12.685 | 2 | 3.931 |
| controller / CLK_N | 16.517 | F.Cu: 2.574, In2.Cu: 13.943 | 2 | 7.151 |
| controller / D0_P | 15.021 | F.Cu: 5.280, In2.Cu: 9.740 | 2 | 3.922 |
| controller / D0_N | 15.916 | F.Cu: 15.916 | 0 | 2.834 |
| controller / D1_P | 18.800 | F.Cu: 3.644, In2.Cu: 15.156 | 2 | 4.927 |
| controller / D1_N | 16.596 | F.Cu: 4.551, In2.Cu: 12.045 | 2 | 5.043 |

Every measured attachment coincides with its native pad center to within 2 nm. Inventory lengths agree with shortest-path lengths within 0.00001 mm, providing an independent cross-check against branch inflation. The path graph has unit checks for branches, crossings, overlaps, vias and disconnected layers.

## Findings

- All three complete pairs exceed the intra-pair geometric budget; data lane 1 is substantially longer than the other lanes.
- Head D0 uses a different layer sequence for P and N. Head D1 uses In1 for P and In2 for N; its P conductor has 16.339 mm on a layer without an adjacent ground plane in this design. Controller D0 also uses asymmetric layers.
- Every conductor has sampled gaps in its candidate reference plane. The flex has 1.500 mm total uncovered centerline at the two termination regions on each conductor; this is not a gap through its entire central plane.
- Of 16 MIPI signal vias, 14 have no GND via within the 1 mm screening radius; two have only one. That radius is a heuristic, not a published limit. A nearby via would still need the correct return connection and geometry.
- Pair spacing varies on the rigid boards. The flex pairs remain at 0.500 mm centerline separation; that is a measured spacing, not proof of 100 ohm impedance.
- The rigid signal layers used by the clock do not contain a ground pour providing continuous same-layer guarding. Ground traces, aggressors, power switching and the full return-current corridor require review during repair.

## Locations and reproducibility

`mipi.json` retains every trace and via UUID, board-coordinate endpoint, layer, reference-gap interval and nearest-ground-via distance. `board-geometry.json` provides the native geometry for the annotated review. Coordinates are in millimetres in each separate board, not the combined assembly frame.

Run `audit_interconnect.py --kind mipi` with KiCad Python from the repository root. The tool verifies `routing-review.json` hashes before and after inspection and does not save the boards. It samples saved ground-fill polygons at intervals no longer than 0.05 mm. Point coverage is a screening test; it does not establish field confinement, impedance or hardware operation.
