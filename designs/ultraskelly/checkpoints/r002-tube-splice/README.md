# US-TUBE-SPLICE-R002: splice for two pieces of the square tube

**Print one splice U and one splice plate, both solid. They hold two pieces of
the square tube end to end with four M2.5 × 16 screws and four M2.5 nuts, the
same screw and nut as the neck mount.**

The splice is the neck clamp's U made 60 mm long, for a joint that flexes. The
two tube ends meet halfway along the U, and one plate covers both pieces, with
a screw at each corner. Its pocket is the fit-tested U1 of
US-NECK-MOUNT-R010: 18.9 mm wide, for a tube of about 18.0 to 18.6 mm per side.
No part needs supports.

R002 replaces R001 and keeps its length and width. These changes make the joint
stronger:

- **Thicker base and plate.** The U's base behind the tube is 8 mm thick
  instead of 4 mm. The plate is 8 mm thick, against 6 mm for R001's two bars.
  Its head recesses are 2 mm deeper, so the same M2.5 × 16 screws fit.
- **One plate across the joint.** R001's two bars stopped either side of the
  joint; R002's plate spans it.
- **No holes at the joint.** The four screws sit 6 mm from the U's ends. R001
  had screw rows and nut slots 5.25 mm either side of the joint.
- **Layers along the tube.** The U prints on its back, so bending at the joint
  runs along its layers instead of pulling them apart.
- **Solid print.** Both parts print at 100 % infill.

By the CAD cross-sections at the joint, the U is 1.78 times as stiff front to
back (bending toward the plate or the base) as R001's U, and a given bending
load stresses it 31 % less. Against R001's weakest section near the joint,
through its screw rows, it takes 53 % less stress front to back and 46 % less
sideways. These are geometry figures: the splice has not been load-tested.

Each piece is still gripped over 30 mm. Sideways, the pocket leaves 0.3 to
0.9 mm of play, so a piece can rock at most 0.57 to 1.72° before the arms stop
it. Each piece is clamped by the two screws at its end of the U, instead of
R001's four.

`manifest.json` records the source, file hashes, checks and the items that are
still unverified. Each part has an image with the same name as its STL file.

## Before printing: check the tube

1. **Tube size.** The splice fits a square tube from 18.0 to 18.6 mm per side,
   like the neck clamp's U1.
2. **Bare tube.** Each piece needs 30 mm of bare tube next to its end, with
   nothing fixed to any of its four faces.
3. **Tube ends.** Cut the ends square, so they meet flat inside the splice.

With its plate on, the splice is 60 mm long, 38.8 mm wide and 34.3 mm deep on
an 18.3 mm tube: 8 mm of U base behind the tube and 8 mm of plate in front of
it.

If the tube does not match, do not print. Send the measurement, and the CAD
will be changed to fit.

## Print

| # | File | Part | Qty | Orientation, as exported | Supports | Size (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `splice-u.stl` | Splice U: 18.9 mm pocket (U1), 8 mm base, four M2.5 nut slots | 1 | On its back, pocket open upward | None | 60 × 38.8 × 25 |
| 2 | `splice-plate.stl` | Splice plate with four corner M2.5 holes and head recesses | 1 | Flat, head recesses up | None | 60 × 38.8 × 8 |

The U and plate are a matched pair: print both from this checkpoint. Both fit
on a 120 × 120 mm bed. Use PETG with 0.2 mm layers, the default line width for
a 0.4 mm nozzle, 6 perimeters and 100 % infill for both parts.

The U and plate take about 71 g of PETG (48 g for the U and 23 g for the plate)
and about 1.6 to 2.6 hours on a fast printer such as the Snapmaker U1. These
figures are estimated from the models at the settings above, not sliced.

## Hardware

| Qty | Length | Item | Use |
| --- | --- | --- | --- |
| 4 | 16 mm | M2.5 socket-head cap screw | Plate to U, one at each corner, into the captured nuts |
| 4 | – | M2.5 hex nut, 5.0 mm across flats | In the U's four side slots |

Use plain hex nuts: the slots take nuts up to 2.6 mm thick, so thicker
nylon-insert lock nuts do not fit.

**Buy this:** M2.5 socket-head cap screws in 16 mm (at least 4) and M2.5 hex
nuts 5.0 mm across flats (at least 4). With the neck mount (R010), the robot
needs 13 screws of M2.5 × 16, 8 screws of M2.5 × 6, 8 nuts and 4 standoffs in
all.

## Assembly

1. Push one M2.5 nut into each of the four side slots near the U's corners.
2. Butt the two tube ends together.
3. Fit the U over the joint from one side: both tube pieces lie in its pocket,
   and the joint is halfway along the U, 30 mm from each end.
4. Lay the plate across both tube pieces, opposite the U's base, with its head
   recesses facing out. Put an M2.5 × 16 screw through each corner of the plate
   into its nut.
5. Tighten the four screws evenly, a little at a time and corner to opposite
   corner, until neither tube piece slides or turns in the U.

To take the splice off, remove the four screws.

## Design guidance used

1. **Layer direction.** FDM parts are strong in the print plane and weaker
   between layers, so structural parts should be oriented for their load
   [@prusaModelingFor3dPrinting; @hubsFdmDesign; @cncKitchenPrintsVsWood]. The
   U prints on its back and the plate prints flat, so bending at the joint runs
   along the layers of both. The screws' clamping force crosses the U's layers
   instead, between each nut slot and the base.
2. **Infill.** Strength comes mostly from perimeters; most parts need 10 to
   15 % infill and rarely more than 30 % [@prusaLayersAndPerimeters;
   @prusaInfill; @cncKitchenExtrusionWidth]. The splice is a joint that flexes,
   so both parts print solid. In CNC Kitchen's tests, a PETG hook printed at
   100 % infill held 110 kg, and one at 30 % infill with 3 perimeters held
   54 kg [@cncKitchenPrintsVsWood].
3. **Walls and fits, as on the neck clamp.**
   - A wall thinner than one perimeter, about 0.45 mm, cannot print
     [@prusaModelingFor3dPrinting]. Every screw feature keeps at least three
     perimeters (1.35 mm): 2.25 mm between each nut slot and the pocket,
     3.3 mm between the nut slots and the U's ends, 1.95 mm beside each head
     recess, 3.45 mm between the recesses and the plate's ends, and 3.3 mm of
     plate under each screw head.
   - Moving fits start at 0.3 mm of clearance, and vertical holes print
     undersized [@prusaModelingFor3dPrinting; @hubsFdmDesign]. The clearance
     holes are 2.9 mm, 0.4 mm over the screw, and all of them print vertical.
     U1's 18.9 mm pocket leaves 0.15 to 0.45 mm per side.
4. **Edges, overhangs and bridges.**
   - Chamfers rather than fillets should face the bed
     [@prusaModelingFor3dPrinting]. Rounded corners are only on edges that
     stand vertical as printed, and the edges on the bed stay square. Edges on
     the bed flare outward, which matters where a part fits [@hubsFdmDesign];
     here only the U's back and the plate's tube face touch the bed, and
     nothing fits to their edges.
   - Overhangs up to 45° print without supports, and bridges sag unless they
     are shorter than 5 mm [@hubsFdmDesign]. The U's only downward faces are
     the ceilings of its four nut slots: 5.4 mm bridges, so they may sag a
     little. Each slot is 0.6 mm taller than its nut. The plate has no
     downward faces.

The sources I read do not cover these points:

- **Base and plate thickness.** No source gives a thickness for a printed tube
  splice. The 8 mm base and plate follow from the cross-section figures above.
  They are `base` and `plate` in `src/splice.json`.
- **Grip length.** No source gives a length for a printed tube splice. The
  30 mm grip per piece follows from the pocket's play, as described above. It
  is `grip` in `src/splice.json`.
- **Nut slots.** The slots keep the neck clamp's allowance: 5.4 mm wide, 0.4 mm
  over the nut's 5.0 mm across flats and narrower than its 5.8 mm across
  corners, so the nut cannot turn; 2.6 mm thick for the 2.0 mm nut.

## Clearances

These are the fits:

- The pocket is 18.9 mm wide: 0.15 to 0.45 mm per side on an 18.0 to 18.6 mm
  tube.
- The arms stop 1 mm short of an 18.0 mm tube's front face, so the plate always
  bears on the tube. After tightening, the gap between the plate and the arms
  is 1 mm on an 18.0 mm tube, 1.3 mm on an 18.3 mm tube and 1.6 mm on an
  18.6 mm tube.
- The U takes M2.5 screws from 13.9 to 21.8 mm long. A 16 mm screw passes its
  nut by at least 3.6 mm and stops at least 7.3 mm short of the end of its
  hole, which ends 2 mm below the pocket floor and 6 mm before the back of the
  U.

## Not verified

- The splice is unprinted. Its pocket is U1's, which the user chose by hand on
  the tube, but the grip of two screws per tube piece and the joint's strength
  under the robot's loads are untested.
- The fit-tested U1 printed standing; this U prints on its back. The pocket
  width stays in the print plane, but its fit has not been printed in this
  orientation.
- Printed fits: the M2.5 nut slots and the clearance holes.
- The screws' clamping force crosses the U's layers.
- The cross-section figures come from the CAD; the splice has not been
  load-tested.
- The print time and filament figures are estimates, not sliced. The Snapmaker
  Orca command line crashed when it loaded the U1 profiles.
