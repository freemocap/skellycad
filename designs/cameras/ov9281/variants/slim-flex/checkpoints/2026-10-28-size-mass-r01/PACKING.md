# Native packaging study

All dimensions are millimetres. The native FreeCAD document contains five rows:
the selected complete Pupil R08 model with supplemental photo-based electronics
blocks, the preserved R10 physical geometry, and three unrouted candidate packings.
The Pupil print-model thickness and plastic volumes are not actual camera mass.

The candidate dark blocks are courtyard prisms, not exact vendor component CAD.
They reserve assembly space on both board sides. Their solid volumes never feed
the package mass budget. All 106 current physical references appear in A; B/C
contain 105 after replacing J102 with integrated flex. Component identities and
conditional package changes are explicit in `options.json` and `packing.json`.
No changes have been made to the selected R10 schematic or PCB files.

- A: 32 x 16 controller, 14 x 14 head, 30.3 x 12.5 free neck; 76.3 mm flat span.
- B: 24 x 12 controller, 12 x 12 head, 32.85 x 8 free neck; 68.85 mm flat span.
- C: 26 x 12.5 controller, 12.5 x 12.5 head, 32.85 x 8 neck; 71.35 mm flat span.

Each board contains its package reservations without same-side overlap. The
front-side 8 x 8 support footprint clears all components except the intended
sensor inside its opening. Q201 is relocated to the underside in these studies.
C's underside stiffener plate and ring clear the package reservations. The
programming pads retain a 7.2 x 2.2 mm underside reservation. A also reserves
its 24-contact head solder-lap area. These are space checks, not electrical
placement, routing, pin-access or manufacturing validation.

B/C's hollow support occupies 48.24 mm3. The idealized geometry leaves 0.28 mm
from the sensor reservation to filter bottom and 0.35 mm from filter top to the
lens envelope. The filter seat overlaps the disk by 0.10 mm radially. These are
nominal geometry values without tolerance qualification. A retains the R10
holder geometry instead. No real thread has been specified. In B/C, the barrel's
axial overlap with the collar decreases from 1.47 mm to 0.47 mm with a 1 mm lens
extension; that travel is a reservation, not a focus or retention demonstration.
The CH2021A envelope does not establish 10–20 mm focus; its published minimum
object distance is 0.1 m [@chuanganCh2021a]. IR transmission and LED coverage are
also unqualified.

The tether exit is an 8 x 7.8 mm clearance guide beyond the controller edge.
It does not represent a selected mating plug, a safe bend radius or strain-relief
strength. Module-side retention remains in the mass allowance; external cable
and its cable-side plug remain outside the under-one-gram total. Cables of several
AWG sizes and lengths are estimated separately in `tether-budget.json`.

`geometry-validation.json` records valid shapes and zero component/support/optics
intersection volume in these nominal reservations. `packing.json` records the
plan-view checks and unresolved items. Save-file integrity and unchanged source
hashes establish artifact identity, not a functional camera or physical fit.
