# USB path and cable audit

Input: R09 data1p trial 03. Four native net sections are connected. The zero-ohm series components bridge separate chip-side and connector-side nets; package travel is excluded from the measurements.

| Conductor | Chip to resistor (mm) | Resistor to connector (mm) | Total copper path (mm) |
| --- | ---: | ---: | ---: |
| DP through R110 | 1.652 | 10.829 | 12.481 |
| DM through R109 | 3.302 | 6.800 | 10.102 |

The planar length difference is **2.379 mm**. The reviewed P4 USB guidance requires equal-length parallel routing but does not specify a numeric length tolerance, so this is an observed mismatch requiring repair, not a claimed numerical USB compliance failure [@esp32P4PcbLayout].

## Board findings

- All four sections use 0.100 mm front-layer traces and no signal vias.
- Saved In1 ground-fill coverage has gaps beneath both conductors: approximately 2.081 mm on DP and 1.021 mm on DM. The exact intervals and UUIDs are in `usb.json`; a positive coverage sample does not certify a sufficient return corridor.
- On the connector-side DP route the median distance to the nearest DM centerline is 1.500 mm, with substantial variation. The traces require review as a pair; no 90 ohm impedance has been calculated.
- R109 and R110 are populated as zero-ohm links in the native design. Their positions, launch geometry and eventual values require device-specific review; this audit does not change them.
- U105 data pads 1/6 belong to DM and 3/4 to DP; each pad center lies on its through-route. Inventory length agrees with measured path length, so this model detects no extra copper branches on these four nets. Package capacitance and ESD performance remain unmodeled. ST lists USB high-speed application support for the device, which does not qualify this assembled PCB [@stUsblc6].

## Verified project connector mapping

| J101 contact | Function |
| --- | --- |
| 1 | VBUS |
| 2 | D− |
| 3 | D+ |
| 4 | GND |

This mapping is checked against native pads. It is not a claim of compatibility with a Pupil Labs cable, another JST cable, or an arbitrary hub pin header. The SH catalog does not establish the required high-speed channel performance [@jstShCatalog].

## Cable requirements and unresolved decisions

TI describes a high-speed USB cable as shielded twisted pair with 90 ohm differential characteristic impedance and ±15% tolerance [@tiUsb20Layout2013]. Retain the narrower ±10% P4 board target separately; do not apply a board target as a demonstrated cable measurement.

1. Specify a matched D+/D− twisted pair and its impedance, construction, length and tolerances; four independent hookup wires are not a qualified cable design.
2. Map both ends explicitly, including orientation, VBUS and ground; verify continuity and polarity before applying power.
3. Decide shield termination. J101 has four signal/power contacts and no dedicated shield contact. A separate termination feature or another explicitly qualified approach is needed; the ground conductor does not by itself specify a shield connection.
4. Size VBUS/GND conductors for the eventual measured load and permitted voltage drop. Connector family ratings do not establish the camera power budget.
5. Specify strain relief, minimum bend radius and where twisting/shielding stop near the connector; include those transitions in channel review.
6. Validate the assembled board, connector, cable and host connection for signal quality, enumeration, sustained transfer and ESD. Cable length and allowable untwisted launch length remain unset pending that design work.

## Evidence and limits

All four native signal sections, four connector pins and endpoint graph measurements were checked. `usb.json` contains coordinates, trace UUIDs, lengths, reference gaps and ESD-pad distances. No camera, cable or USB host hardware was tested; no waveform or impedance simulation was run.
