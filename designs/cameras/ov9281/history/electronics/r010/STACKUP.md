# R10 interconnect construction and constraints

The selected design basis is PCBWay's **0.6 mm six-layer entry 21**, with two
dedicated ground planes. The earlier four-layer calculation remains in
`four-layer-screen.json`. Six layers let existing internal signal routes move
away from the reference planes while preserving the thin-board objective.
This selection is within the approved stackup task; it does not change the
sensor, board outline or connector interfaces.

## Rigid board

| Layer or dielectric | Thickness, mm | Use / relative permittivity |
| --- | ---: | --- |
| F.Cu | 0.035 | Components and paired signals |
| 1080 prepreg | 0.0705 | Er 4.21 |
| In1.Cu | 0.035 | Ground only |
| Core | 0.065 | Er 4.6 |
| In2.Cu | 0.035 | Slow signals and power |
| 1080 prepreg | 0.060 | Er 4.21 |
| In3.Cu | 0.035 | Slow signals and power |
| Core | 0.065 | Er 4.6 |
| In4.Cu | 0.035 | Ground only |
| 1080 prepreg | 0.0705 | Er 4.21 |
| B.Cu | 0.035 | Components and paired signals |

The copper/dielectric sum is 0.541 mm. The catalog lists a finished thickness
of 0.61 Â±0.10 mm, including manufacturing additions. Its compressed prepreg
values assume greater than 60% inner copper retention; final copper coverage
must be checked. Mask profile is not specified by this catalog
[@pcbwayRigidStackups2026].

Use 0.1 mm minimum track/clearance and 0.4 mm via diameter with 0.2 mm holes.
The 0.1 mm nominal annular ring requires the advanced process: the reviewed
roadmap lists 3 mil (0.0762 mm) retained rings. Through-vias only; no blind,
buried or via-in-pad process is assumed [@pcbwayAdvancedCapabilities2026].

## Flex

Use the published two-layer construction with a 25 micrometre PI core, 20
micrometre core adhesive on each face, 24 micrometre finished copper per face,
and 15 micrometre adhesive plus 12.5 micrometre PI coverlay per face
[@pcbwayFlexStackups2026]. Signals are on B, referenced to continuous F ground.

The finished-copper sum is **0.168 mm**, excluding local stiffeners and contact
finish. The table's 0.156 mm sum uses its 18 micrometre starting copper, despite
also specifying 24 micrometre finished copper. Preserve both figures; do not
silently label the finished construction 0.156 mm. The connector tip remains
0.30 Â±0.03 mm and needs a locally matched stiffener/adhesive construction.
The manufacturer's published flex thickness tolerance is a separate limit
[@pcbwayFlexCapabilities2026]. No vias in the flexible span.

## Calculated straight-pair geometry

| Interface | Width, mm | Edge gap, mm | Ground guard clearance, mm |
| --- | ---: | ---: | ---: |
| Rigid MIPI, F or B | 0.100 | 0.350 | 0.350 |
| Head and controller clock, finite 0.100 mm ground guards | 0.100 | 0.350 | 0.101 |
| Rigid USB, F, local ground fill | 0.100 | 0.150 | 0.101 |
| Flex MIPI, B | 0.100 | 0.250 | 0.350 |
| Flex clock, finite 0.100 mm ground guards | 0.100 | 0.250 | 0.101 |

The initial broad-guard calculations remain in `cross-sections.json`. Final
clock and USB guard variants are recorded separately in
`clock-guard-sections.json`, `flex-clock-guard.json` and
`usb-guard-sections.json`. The routing notes identify nonuniform launches and
compensation bends; uniform-section values do not qualify those regions.

`cross-sections.json` records nominal values, three mesh resolutions, domain
expansion and two sensitivity corners. The local finite-volume solver computes
odd-mode capacitance with the selected dielectric and again with vacuum, then
uses `Zdiff = 2 / (c * sqrt(Codd * Codd_vacuum))`. Residual checks, homogeneous
dielectric scaling, vacuum delay, width monotonicity and mesh refinement check
the calculation. These are quasi-static straight-section models, not full
channel simulations or certification of a manufactured board.

Rigid solder mask is modeled as a rectangular conformal coating, nominally
0.020 mm with assumed Er 3.8. That Er is a published JLCPCB example, **not a
PCBWay material guarantee** [@jlcImpedanceStackups2026]. Flex's core/adhesive and
coverlay are approximated by Er 3.4, within the published PI range; the adhesive
permittivity remains an explicit approximation [@pcbwayFlexStackups2026].

Sensitivity corners use width Â±0.010 mm with corresponding gap change, height
Â±10%, copper Â±0.005 mm, Er Â±0.2 and coating Â±0.010 mm. These are analysis
assumptions, not promised fabrication tolerances. Their impedance spread can
exceed the target band. Therefore production requires controlled impedance and
fabricator compensation, with geometry updates rechecked before release.
The selected dimensions are the offline routing basis, not permission to order.

## Matching and transition budgets

- MIPI: 100 ohm Â±10%; whole-link intra-pair planar difference â‰¤0.254 mm and
  pair-mean spread â‰¤0.762 mm, following the existing audit convention and
  Espressif guidance [@esp32P4PcbLayout]. Also report calculated delay and each
  conductor total so geometric matching cannot conceal unlike layers.
- USB: 90 ohm Â±10%; adopt a project copper-path matching target of 0.050 mm,
  including both resistor-side sections. This is a conservative project target
  informed by TI's 2 mil package-boundary recommendation; it does not include
  unknown package-internal skew [@tiUsb20Layout2013].
- Keep transition counts and used layer spans equal within each pair. Place
  two nearby ground return vias at each paired layer change. The 1 mm search
  radius remains a screening heuristic; inspect the actual ground corridor.
- Paired runs use the listed gap. Pad and via launches may taper locally;
  record every departure and keep uncoupled portions short. No arbitrary long
  independent routes count as a repaired pair merely because lengths match.
- Ground guard the clock and USB; keep unrelated fast traces at least three
  trace widths away. Check that each ground guard connects to a plane. All
  ground-plane crossings must be reviewed at corridor level, not only at the
  centerline [@esp32P4PcbLayout].

Source review date: 2026-10-28. No vendor was contacted and no order placed.
Public constructions establish a supported design basis; final manufacturing
acceptance and hardware validation remain later release gates.

## Final copper-area check

R10's native polygon-union check includes filled zones, tracks and pads and
subtracts via holes. All rigid inner layers exceed the catalog's 60% retention
assumption [@pcbwayRigidStackups2026]. Head In2/In3 measure 63.28%/65.46% after
four ground stitches and a local In2 +1V8 fill; their zone clearance and minimum
fill width are 0.100 mm. In1/In4 remain the reference layers. The final native
DRC and MIPI checks pass with the signal routes unchanged. This geometric
check does not replace the manufacturer's final stackup and impedance review.
