# High-speed interconnect audit requirements

Date: 2026-10-28. Input: R09 data1p trial 03, selected by `routing-review.json`.
This audit measures saved copper without changing the electrical checkpoint.
The selected R08 baseline and previous matched FreeCAD review remain unchanged.

## Published constraints

Espressif specifies MIPI differential impedance of 100 ohm ±10%, intra-pair
length difference within 10 mil (0.254 mm), and inter-pair difference within
30 mil (0.762 mm). Maintain consistent pair spacing and a continuous reference
plane. Keep pairs separated by at least 2W when ground guarding is unavailable;
separate other high-speed aggressors by 3W. Ground-guard the clock pair and
provide ground return vias at layer transitions. USB guidance calls for 90 ohm
±10%, parallel equal-length conductors, continuous reference copper, minimal
transitions and ground return vias. Its four-layer example reserves layer 2
for uninterrupted ground [@esp32P4PcbLayout].

These are the receiver manufacturer's layout recommendations, not a claim of
complete MIPI or USB standards compliance. The reviewed USB section gives no
numeric skew limit. This audit therefore reports USB length differences without
inventing a numerical pass threshold. The sensor's package timing, connector
models and assembled cable delay remain outside the measured PCB lengths.

## Candidate layer structures

| Candidate | Copper and dielectric structure | Status |
| --- | --- | --- |
| Existing rigid definition | F / 0.100 FR4 / In1 / 0.260 FR4 / In2 / 0.100 FR4 / B; each copper layer 0.035 mm; assumed Er 4.2 | 0.600 mm copper-plus-dielectric model; not supplier approved |
| A: four-layer repair | Keep high-speed pairs on F over uninterrupted In1 GND; use In2 for power/other routing and B for components/other routing | Proposed topology; escape feasibility and required trace geometry unproven |
| B: six-layer fallback | F signal / GND / signal-power / signal-power / GND / B signal | Alternative if four-layer fan-out cannot preserve reference planes; thickness, dielectric separations and via process unset |
| Existing flex / candidate repair | B signal over F continuous GND; 0.018 mm copper each side and 0.064 mm polyimide, assumed Er 3.4 | 0.100 mm copper-plus-dielectric model; coverlay, adhesive, finish and local stiffeners additional and unqualified |

Candidate A and B are project proposals, not manufacturer stackups. Do not
derive a fabrication trace width from nominal overall thickness alone. Obtain
actual dielectric heights, material properties, copper thickness/tolerance,
mask or coverlay and etch data before choosing impedance-controlled geometry.
Flex fabrication supports thin constructions and stiffeners, but a supplier's
general capability table does not approve this specific construction
[@epecFlexCapabilities]. Retain the documented 0.30 ±0.03 mm connector-tip
requirement separately from the 0.10 mm flex body model; the inherited interface
record supplies that requirement and its Hirose sources.

## Measurement contract and explicit assumptions

- Verify every input native hash against the routing checkpoint before and
  after the audit; never save modifications into that checkpoint.
- Trace each signal from its component pad to its connector pad. Report copper
  centerline lengths by layer, via positions, widths, branches and endpoints.
  Sum the three board sections for MIPI, preserving P/N identity and pin mapping.
- Compare geometric intra-pair differences with 0.254 mm. Compare pair mean
  lengths with 0.762 mm, explicitly identifying that mean as this audit's
  screening convention. Also retain individual conductor totals.
- These are planar lengths, not propagation delays. Exclude pad/package travel,
  connector contact lengths, solder laps and vertical via barrels; list vias
  separately. Different layers and materials prevent treating equal geometric
  length as equal electrical delay.
- Screen reference coverage against saved ground fill beneath sampled trace
  locations. For F on rigid use In1; for flex B use F. Other rigid routing
  layers require separate reference assessment. A point-in-copper result does
  not establish a sufficient return-current corridor or field-solver result.
- Report nearby ground vias using a 1 mm search radius as a project screening
  heuristic, not a published maximum spacing or proof of adequate return paths.
- Review pair proximity, branching, crossings, transitions and reference voids
  as geometric evidence; this audit does not compute impedance or eye diagrams.

## External USB boundary

The board's four contacts are a project pinout, not a standardized USB connector.
The JST SH catalog identifies the connector family and electrical ratings but
does not establish USB high-speed channel performance [@jstShCatalog]. The cable
must preserve D+/D− pairing, verified end-to-end pin mapping, a ground conductor,
power capacity and an explicit shield/return strategy. Cable length, construction,
impedance and connector discontinuities need qualification as one assembled
channel. No cable or hub compatibility is assumed from connector appearance.

## Reviewed evidence

- Espressif PCB layout page: layer strategy, USB and MIPI sections reviewed
  2026-10-28. Only those sections support the numerical constraints above.
- Epec flex roadmap: thickness/material/stiffener capability excerpts revisited;
  not a quotation or orderable stackup.
- JST SH product page: family/specification table reviewed; no high-speed
  qualification found in the reviewed table.
- Native board setup blocks and inherited interface record: local design
  assumptions and connector mapping, verified separately against native pads.
