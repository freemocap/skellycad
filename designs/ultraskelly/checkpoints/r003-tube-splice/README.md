# US-TUBE-SPLICE-R003: splice for two pieces of the square tube

**Print one splice U and one splice plate, both solid. They hold two pieces of
the square tube end to end with four M2.5 × 16 screws and four M2.5 nuts, the
same screw and nut as the neck mount.**

The splice is the neck clamp's U made 70 mm long, for a joint that flexes. The
two tube ends meet halfway along the U, and one plate covers both pieces, with
a screw at each corner. A tongue along the middle of the plate reaches between
the U's arms and presses on the tube. The pocket is the fit-tested U1 of
US-NECK-MOUNT-R010: 18.9 mm wide, for a tube of about 18.0 to 18.6 mm per side.
No part needs supports.

R003 replaces R002. It keeps R002's 8 mm base, 8 mm plate, corner screws and
width, with these changes:

- **Longer.** The splice is 70 mm long instead of 60 mm, so each tube piece is
  gripped over 35 mm instead of 30 mm.
- **Tongue on the plate.** A rib 3 mm tall and 18.3 mm wide runs the length of
  the plate's tube face. It fits between the arms with 0.3 mm each side and
  bears on both tube pieces.
- **Taller arms.** The arms rise 3 mm, to 20 mm above the pocket floor. They
  stand past the tube's front face, so the tongue sits inside the channel and
  the arms cover the tube's sides. The nut slots rise with the arms, so the
  same M2.5 × 16 screws fit.
- **Plate prints tongue up.** The plate prints with its head recesses on the
  bed, so the tongue needs no support.

## How the tongue presses the tube

When you tighten the screws, the tongue bears on the tube and pushes it
against the U's base. The plate stays clear of the arms: the gap between the
plate and the arms is 1 mm on an 18.0 mm tube, 1.3 mm on an 18.3 mm tube and
1.6 mm on an 18.6 mm tube. The plate cannot bottom out on the arms before the
tongue presses the tube, so more torque on the screws gives more clamping
force on the tube.

The tongue reaches 2 mm into the channel on an 18.0 mm tube and 1.4 mm on an
18.6 mm tube. It does not change the sideways fit: the pocket leaves 0.3 to
0.9 mm of sideways play, so a piece can rock at most 0.49 to 1.47° before the
arms stop it. Each piece is clamped by the two screws at its end of the U.

By the CAD cross-sections at the joint, the U is 1.4 times as stiff front to
back (bending toward the plate or the base) as R002's U, and a given bending
load stresses it 20 % less. Sideways, it is 1.12 times as stiff, with 10 % less
stress. The plate with its tongue is 1.88 times as stiff front to back as
R002's flat plate. These are geometry figures: the splice has not been
load-tested.

`manifest.json` records the source, file hashes, checks and the items that are
still unverified. Each part has an image with the same name as its STL file.

## Before printing: check the tube

1. **Tube size.** The splice fits a square tube from 18.0 to 18.6 mm per side,
   like the neck clamp's U1.
2. **Bare tube.** Each piece needs 35 mm of bare tube next to its end, with
   nothing fixed to any of its four faces.
3. **Tube ends.** Cut the ends square, so they meet flat inside the splice.

With its plate on, the splice is 70 mm long, 38.8 mm wide and 37.3 mm deep on
an 18.3 mm tube: 8 mm of U base behind the tube, and the 3 mm tongue and 8 mm
of plate in front of it.

If the tube does not match, do not print. Send the measurement, and the CAD
will be changed to fit.

## Print

| # | File | Part | Qty | Orientation, as exported | Supports | Size (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `splice-u.stl` | Splice U: 18.9 mm pocket (U1), 8 mm base, 20 mm arms, four M2.5 nut slots | 1 | On its back, pocket open upward | None | 70 × 38.8 × 28 |
| 2 | `splice-plate.stl` | Splice plate with a 3 mm tongue, four corner M2.5 holes and head recesses | 1 | Flat, tongue up, head recesses on the bed | None | 70 × 38.8 × 11 |

The U and plate are a matched pair: print both from this checkpoint. Both fit
on a 120 × 120 mm bed. Use PETG with 0.2 mm layers, the default line width for
a 0.4 mm nozzle, 6 perimeters and 100 % infill for both parts.

The U and plate take about 94 g of PETG (62 g for the U and 32 g for the plate)
and about 2 to 3.4 hours on a fast printer such as the Snapmaker U1. These
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
   and the joint is halfway along the U, 35 mm from each end.
4. Lay the plate across both tube pieces, tongue first, so the tongue drops
   between the arms onto the tube and the head recesses face out. Put an
   M2.5 × 16 screw through each corner of the plate into its nut.
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
     undersized [@prusaModelingFor3dPrinting; @hubsFdmDesign]. The tongue
     clears each arm by 0.3 mm. The clearance holes are 2.9 mm, 0.4 mm over
     the screw, and all of them print vertical. U1's 18.9 mm pocket leaves
     0.15 to 0.45 mm per side.
4. **Edges, overhangs and bridges.**
   - Chamfers rather than fillets should face the bed
     [@prusaModelingFor3dPrinting]. Rounded corners are only on edges that
     stand vertical as printed, and the edges on the bed stay square. Edges on
     the bed flare outward, which matters where a part fits [@hubsFdmDesign].
     Only the U's back and the plate's outer face touch the bed. Nothing fits
     to their edges, and the head recesses that open on the bed are loose on
     the screw heads.
   - Overhangs up to 45° print without supports, and bridges sag unless they
     are shorter than 5 mm [@hubsFdmDesign]. The U's only downward faces are
     the ceilings of its four nut slots: 5.4 mm bridges, so they may sag a
     little. Each slot is 0.6 mm taller than its nut. The plate's only
     downward faces are the ceilings of its four head recesses, where the
     screw heads seat: 5.1 mm bridges, so they may also sag a little.

The sources I read do not cover these points:

- **Base and plate thickness.** No source gives a thickness for a printed tube
  splice. The 8 mm base and plate are R002's, chosen from its joint
  cross-sections. They are `base` and `plate` in `src/splice.json`.
- **Grip length.** No source gives a length for a printed tube splice. The
  35 mm grip per piece is 5 mm more than R002's, as requested, and sets the
  rock limit described above. It is `grip` in `src/splice.json`.
- **Tongue height.** The 3 mm tongue and the 3 mm rise of the arms keep the
  neck clamp's 1 mm minimum gap between the plate and the arms. It is
  `tongue` in `src/splice.json`.
- **Nut slots.** The slots keep the neck clamp's allowance: 5.4 mm wide, 0.4 mm
  over the nut's 5.0 mm across flats and narrower than its 5.8 mm across
  corners, so the nut cannot turn; 2.6 mm thick for the 2.0 mm nut.

## Clearances

These are the fits:

- The pocket is 18.9 mm wide: 0.15 to 0.45 mm per side on an 18.0 to 18.6 mm
  tube.
- The tongue is 18.3 mm wide: 0.3 mm between it and each arm.
- The arms stand 20 mm above the pocket floor: 2 mm past an 18.0 mm tube's
  front face and 1.4 mm past an 18.6 mm tube's. After tightening, the gap
  between the plate and the arms is 1 mm on an 18.0 mm tube, 1.3 mm on an
  18.3 mm tube and 1.6 mm on an 18.6 mm tube.
- The U takes M2.5 screws from 13.9 to 24.8 mm long. A 16 mm screw passes its
  nut by at least 3.6 mm and stops at least 10.3 mm short of the end of its
  hole, which ends 2 mm below the pocket floor and 6 mm before the back of the
  U.

## Not verified

- The splice is unprinted. Its pocket is U1's, which the user chose by hand on
  the tube, but the grip of two screws per tube piece and the joint's strength
  under the robot's loads are untested.
- The fit-tested U1 printed standing; this U prints on its back. The pocket
  width stays in the print plane, but its fit has not been printed in this
  orientation.
- Printed fits: the tongue between the arms, the M2.5 nut slots and the
  clearance holes.
- The screws' clamping force crosses the U's layers.
- The head recess ceilings print as 5.1 mm bridges.
- The cross-section figures come from the CAD; the splice has not been
  load-tested.
- The print time and filament figures are estimates, not sliced. The Snapmaker
  Orca command line crashed when it loaded the U1 profiles.
