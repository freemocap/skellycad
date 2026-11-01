# USB routing and cable definition

Corrective checklist item 6 is complete. The selected working source is
`generated/ov9281-r10-usb-13/`, relative to the repository root. Native KiCad
reports zero violations and zero unconnected items. All 316 controller pad/net
identities are preserved. MIPI copper is unchanged and passes its checks again.

| Conductor | Processor to resistor, mm | Resistor to J101, mm | Total planar copper, mm |
| --- | ---: | ---: | ---: |
| D+ | 4.223775 | 6.351094 | 10.574869 |
| D− | 3.405624 | 7.169246 | 10.574869 |

The complete copper-path difference is less than 0.000001 mm, below the project
0.050 mm target. Both signals stay on F.Cu, with no signal vias. Each protection
pad lies directly on its conductor's through-path; there are no ESD branch
stubs. The retained USBLC6 pin mapping follows the device diagram [@stUsblc6].

Main paired runs use 0.100 mm width and 0.150 mm edge gap. The processor launch,
resistor lands, ESD package and JST lands necessarily depart from that section.
The ESD flow-through region has 1.075 mm center spacing across its 1.700 mm
package span; the JST launch expands to its 1.000 mm contact pitch. The short
D+ compensation bend also departs from uniform coupling. These departures are
recorded in the native paths and proximity measurements; length matching alone
does not qualify their impedance or the complete USB channel.

Local ground copper surrounds the main runs at 0.101 mm clearance. Uniform
models give 87.699 ohms for a 0.100 mm-wide guard and 87.682 ohms for broad ground,
within the selected 90 ohm ±10% design band. Actual launches and ground boundaries
are not uniform models. In1 ground clearance is now 0.100 mm, within the selected
fabrication rules. Sampling across a 0.450 mm-wide reference corridor finds no
uncovered points. Both reference planes retain one connected region.

R109 and R110 moved to (11.70, 2.40) and (11.70, 3.40) mm on F.Cu. Q102 moved to
(4.50, 2.50) mm on B.Cu to provide room for separate VBUS and ground vias beneath
the protection device. Item 7 must regenerate these placements in FreeCAD.

## Defined prototype cable

The cable is a proposed custom assembly, not an identified stocked product or
a USB-certified assembly. Use a USB 2.0 Type-A plug at the host and an SHR-04V-S-B
housing with compatible SH contacts at J101. The retained board header is
SM04B-SRSS-TB. SH's published wire range includes AWG 28 and 0.4–0.8 mm insulation
outside diameter [@jstShCatalog]. Choose AWG 28 conductors for this prototype.

| USB Type-A contact | Signal | J101 contact |
| --- | --- | --- |
| 1 | VBUS | 1 |
| 2 | D− | 2 |
| 3 | D+ | 3 |
| 4 | Ground return | 4 |

Use a shielded twisted data pair specified at 90 ohms ±15%, with separate VBUS
and ground-return conductors, following TI's cable guidance [@tiUsb20Layout2013].
The initial assembly target is 50 mm between terminations. Keep the data pair
twisted to within 3 mm of the contacts and match the two data conductor lengths
within 0.5 mm. Those lengths are project assembly targets, not quoted USB limits.

Bond the shield/drain to the Type-A shell at the host end. At the camera end,
join the drain to the ground-return wire in an insulated splice before the
single-wire J101 contact-4 crimp. Limit the drain branch to 3 mm. Do not put two
wires into a contact specified for a single conductor. This preserves the
four-contact interface, but its shield pigtail and the JST transition still
need signal-integrity, ESD and emissions testing. No chassis bond or Pupil Labs
cable compatibility is assumed.

Before applying power to a future cable, check all four numbered connections,
shield continuity and absence of shorts. Use contact numbers from the connector
drawings, not an assumed left-to-right view. That physical test remains future
work; the current result is a pin map and assembly specification.

Review date: 2026-10-28. Reviewed the JST product specification table and retained
the TI and ST review scopes in the bibliography. No cable, board or camera has
been built or electrically tested. This checkpoint is not a fabrication release.
