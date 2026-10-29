# R10 corrective routing review

The approved routing corrections are saved as a matched KiCad and FreeCAD review.
All 21 original audit findings have an explicit disposition below. This is an
offline engineering checkpoint, not a functional or fabrication-ready camera.

Native checks pass: **471 schematic-to-pad comparisons, 24 flex paths, 24 XY
interface alignments, zero schematic ERC findings, and zero DRC violations or
unconnected items on all three boards**. Every inner rigid layer exceeds 60%
conservative copper-area retention; the lowest are head In2 at 63.28% and In3
at 65.46%. A local +1V8 fill and four ground stitches achieved this without
changing the verified signal routes.

The six-layer construction and compression assumptions come from the selected
catalog stackup [@pcbwayRigidStackups2026]. Nominal cross-section calculations,
tolerance corners, guard models and project matching budgets are in
[STACKUP.md](../../electronics/r10/STACKUP.md). A passing nominal section does
not qualify connectors, vias, meanders, packages or manufacturing variation.

| Finding | Disposition | Evidence/result |
| --- | --- | --- |
| M-CLK | Planar matching repaired | Complete-link P/N difference 0.000001591 mm; budget 0.254 mm. |
| M-D0 | Planar matching repaired | Complete-link P/N difference 0.000343493 mm; budget 0.254 mm. |
| M-D1 | Planar matching repaired | Complete-link P/N difference 0.000000440 mm; budget 0.254 mm. |
| M-SPREAD | Planar matching repaired | Pair-mean spread 0.000000800 mm; budget 0.762 mm. Barrel/contact/package delay is excluded; electrical delay is not matched or qualified. |
| L-head-D0 | Layer symmetry repaired | Both members use F.Cu with no signal vias. |
| L-head-D1 | Layer symmetry repaired | Both members use F/B with two matching through transitions each. |
| L-controller-D0 | Layer symmetry repaired | Both members use F/B with two matching through transitions each. |
| R-head | Reference routing repaired | Signal and power routes removed from In1/In4; reference gaps limited to the signal transitions themselves. |
| V-head | Return transitions repaired | Paired signal transitions have nearby ground-return stitches; native clearance checks pass. |
| Z-head | Nominal impedance design recorded | Six-layer catalog construction, explicit outer pair geometry and finite clock guards; tolerance corners and nonuniform launches remain unqualified. |
| G-head | Clock guard geometry repaired | Finite 0.100 mm ground guards and 0.101 mm edge clearance, with grounded connections. |
| R-flex-study | Reference routing repaired | F.Cu ground backs all measured MIPI paths; the outer 0.25 mm finger tips remain an explicit termination discontinuity. |
| Z-flex-study | Nominal impedance design recorded | Two-layer PI construction, 0.100/0.250 mm pair geometry and a separate clock-guard model; bend and termination qualification remain pending. |
| R-controller | Reference routing repaired | Signal and power routes removed from In1/In4; reference gaps limited to the signal transitions themselves. |
| V-controller | Return transitions repaired | Paired signal transitions have nearby ground-return stitches; native clearance checks pass. |
| Z-controller | Nominal impedance design recorded | Six-layer catalog construction and MIPI/USB cross-section models; manufacturing compensation and channel qualification remain pending. |
| G-controller | Clock guard geometry repaired | Finite 0.100 mm ground guards and 0.101 mm edge clearance, with grounded connections. |
| U-LENGTH | Planar matching repaired | Complete U101-to-J101 P/N difference 0.000000509 mm; project target 0.050 mm. |
| U-REF | Reference routing repaired | The sampled 0.450 mm reference corridor has no uncovered points. |
| U-PAIR | Pair routing repaired | Front-only paired routing, zero signal vias, all four ESD pads on the through paths, and 26 passing ground-guard probes; package launches remain nonuniform. |
| U-CABLE | Prototype cable specified | 50 mm shielded 90-ohm data pair; pin 1 VBUS, 2 Dâˆ’, 3 D+, 4 GND; explicit shield/drain splice and matching targets. No USB or Pupil compatibility certification. |

## Matched mechanical review

The model uses these exact board hashes and native STEP copper. It includes 106
component reservations: head 8 front/22 back, controller 17 front/59 back.
Courtyard XY and side come from KiCad; heights remain assumptions. The compact
CH2021A envelope remains 6 mm diameter by 2.65 mm long [@chuanganCh2021a]. The
8 mm holder clears the modeled head components after the retained LED/transistor
reliefs. Lens travel at 0, 0.5 and 1 mm clears the holder and filter reservation;
these checks do not establish focus or adequate thread engagement.

Separate coverlay/stiffener envelopes represent the proposed 0.168 mm flex span
and 0.300 mm tips. Native STEP mask thickness differs from that construction.
Flat assembly placement checks XY correspondence; contact heights, solder
thickness, connector engagement and physical fit remain unqualified.

## Remaining qualification

Manufacturing tolerances, complete channel timing and signal integrity, power
and illumination design, verified component bodies, final optics/mounting, and
hardware capture remain outside this routing phase. Planar lengths deliberately
exclude barrel, contact and package paths. The recorded illustrative clock and
data delays differ; this review does not claim electrical delay matching.

The proposed cable and shield termination are recorded in
[USB-ROUTING.md](../../electronics/r10/USB-ROUTING.md); its 50 mm length, untwist
limit and matching budget are project targets. The JST SH wire range and contact
family are manufacturer data [@jstShCatalog]. No USB compliance or compatibility
with an existing Pupil cable is claimed.
