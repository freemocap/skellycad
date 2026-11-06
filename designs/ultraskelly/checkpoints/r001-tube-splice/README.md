# US-TUBE-SPLICE-R001: splice for two pieces of the square tube

**Print one splice U and two splice bars. They hold two pieces of the square
tube end to end with eight M2.5 × 16 screws and eight M2.5 nuts, the same
screw and nut as the neck mount.**

The splice is the neck clamp's U made 60 mm long. The two tube ends meet
halfway along the U, and each piece has its own bar with four screws, so each
side tightens on its own tube. Its cross-section is the fit-tested U1 clamp of
US-NECK-MOUNT-R010: the same 18.9 mm pocket, arms, M2.5 holes and captured-nut
slots, for a tube of about 18.0 to 18.6 mm per side. No part needs supports.

Each piece is gripped over 30 mm, 1.5 times the neck clamp's 20 mm. The bars
clamp the tube front to back. Sideways, the pocket leaves 0.3 to 0.9 mm of
play, so a piece can rock at most 0.57 to 1.72° before the arms stop it,
instead of about 0.9 to 2.6° over 20 mm.

`manifest.json` records the source, file hashes, checks and the items that are
still unverified. Each part has an image with the same name as its STL file.

## Before printing: check the tube

1. **Tube size.** The splice fits a square tube from 18.0 to 18.6 mm per side,
   like the neck clamp's U1.
2. **Bare tube.** Each piece needs 30 mm of bare tube next to its end, with
   nothing fixed to any of its four faces.
3. **Tube ends.** Cut the ends square, so they meet flat inside the splice.

With its bars on, the splice is 60 mm long, 38.8 mm wide and 28.3 mm deep on
an 18.3 mm tube: the U's base is 4 mm thick behind the tube, and the bars are
6 mm thick in front of it.

If the tube does not match, do not print. Send the measurement, and the CAD
will be changed to fit.

## Print

| # | File | Part | Qty | Orientation, as exported | Supports | Size (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `splice-u.stl` | Splice U: 18.9 mm pocket (U1), 60 mm long, eight M2.5 nut slots | 1 | Standing on one end, tube opening vertical | None | 21 × 38.8 × 60 |
| 2 | `splice-bar.stl` | Splice bar with four M2.5 holes | 2 | Flat, screw-head recesses up | None | 29.75 × 38.8 × 6 |

Both parts fit on a 120 × 120 mm bed. Use PETG with 0.2 mm layers, the
default line width for a 0.4 mm nozzle, and the neck clamp's settings for
both: 6 perimeters, 5 top and bottom layers and 25 % gyroid infill.

The U and two bars take about 49 g of PETG (35 g for the U and 7 g per bar)
and about 1.1 to 1.8 hours on a fast printer such as the Snapmaker U1. These
figures are estimated from the models at the settings above, not sliced.

## Hardware

| Qty | Length | Item | Use |
| --- | --- | --- | --- |
| 8 | 16 mm | M2.5 socket-head cap screw | Each bar to the U, four per bar, into the captured nuts |
| 8 | – | M2.5 hex nut, 5.0 mm across flats | In the U's eight side slots |

Use plain hex nuts: the slots take nuts up to 2.6 mm thick, so thicker
nylon-insert lock nuts do not fit.

**Buy this:** M2.5 socket-head cap screws in 16 mm (at least 8) and M2.5 hex
nuts 5.0 mm across flats (at least 8). With the neck mount (R010), the robot
needs 17 screws of M2.5 × 16, 8 screws of M2.5 × 6, 12 nuts and 4 standoffs in
all.

## Assembly

1. Push one M2.5 nut into each of the eight side slots in the U's arms.
2. Butt the two tube ends together.
3. Fit the U over the joint from one side: both tube pieces lie in its pocket,
   and the joint is halfway along the U, between the second and third screw
   rows.
4. Hold one bar across each tube piece, opposite the U's base, so the 0.5 mm
   gap between the bars is at the joint. Put four M2.5 × 16 screws through
   each bar into the nuts.
5. Tighten the four screws of one bar evenly, a little at a time, until its
   tube piece does not slide or turn in the U. Repeat for the other bar.

To take the splice off, remove the eight screws.

## Design guidance used

1. **The neck clamp's rules.** The cross-section, holes, nut slots and print
   settings are the neck clamp's (US-NECK-MOUNT-R010), which follow these
   sources:
   - Strength comes mostly from perimeters; most parts need 10 to 15 %
     infill and rarely more than 30 % [@prusaLayersAndPerimeters; @prusaInfill;
     @cncKitchenExtrusionWidth]. The splice takes the screw load, so it uses
     6 perimeters with 25 % gyroid, which has equal strength in all
     directions [@prusaInfillPatterns].
   - A wall thinner than one perimeter, about 0.45 mm, cannot print
     [@prusaModelingFor3dPrinting]. Every screw feature keeps at least three
     perimeters (1.35 mm): 2.25 mm between each nut slot and the pocket,
     1.95 mm beside each screw-head recess, 2.3 mm between the end nut slots
     and the U's ends, and 2.45 mm between the recesses and the bar ends.
   - Moving fits start at 0.3 mm of clearance, and vertical holes print
     undersized [@prusaModelingFor3dPrinting; @hubsFdmDesign]. The clearance
     holes are 2.9 mm, 0.4 mm over the screw, and U1's 18.9 mm pocket leaves
     0.15 to 0.45 mm per side.
   - Edges on the build plate flare outward [@hubsFdmDesign], so the pocket
     has a 0.5 mm 45° chamfer where it meets the bed. Rounded corners are only
     on edges that stand vertical as printed [@prusaModelingFor3dPrinting].
2. **Overhangs and bridges.** Overhangs up to 45° print without supports, and
   bridges sag unless they are shorter than 5 mm [@hubsFdmDesign]. The U's
   only downward faces are the tops of its 2.9 mm holes and the 2.6 mm tops of
   its nut slots.
3. **Layer direction.** FDM parts are weaker between layers, so print
   structural parts with their loads along the layers
   [@prusaModelingFor3dPrinting; @hubsFdmDesign; @cncKitchenPrintsVsWood]. The
   U prints standing, like the neck clamp, so the screw tension runs along its
   layers. Bending at the joint pulls along the tube, across the U's layers,
   which is the weaker direction.

The sources I read do not cover these points:

- **Grip length.** No source gives a length for a printed tube splice. The
  30 mm grip per piece follows from the pocket's play, as described above. It
  is one number, `grip`, in `src/splice.json`.
- **Nut slots.** The slots keep the neck clamp's allowance: 5.4 mm wide, 0.4 mm
  over the nut's 5.0 mm across flats and narrower than its 5.8 mm across
  corners, so the nut cannot turn; 2.6 mm thick for the 2.0 mm nut.

## Clearances

These are the fits:

- The pocket is 18.9 mm wide: 0.15 to 0.45 mm per side on an 18.0 to 18.6 mm
  tube.
- The arms stop 1 mm short of an 18.0 mm tube's front face, so each bar always
  bears on its tube. After tightening, the gap between a bar and the arms is
  1 mm on an 18.0 mm tube, 1.3 mm on an 18.3 mm tube and 1.6 mm on an 18.6 mm
  tube.
- The U takes M2.5 screws from 13.9 to 21.8 mm long. A 16 mm screw passes its
  nut by at least 3.6 mm and stops at least 7.3 mm short of the end of its
  hole, which ends 2 mm before the back of the U.
- The bars are 0.5 mm apart at the joint, so each one tightens on its own tube
  piece.

## Not verified

- The splice is unprinted. Its pocket is U1's, which the user chose by hand on
  the tube, but its grip and the joint's stiffness under the robot's loads are
  untested.
- Printed fits: the tube fit, the M2.5 nut slots and the clearance holes.
- Bending at the joint loads the U across its layers.
- The print time and filament figures are estimates, not sliced. The Snapmaker
  Orca command line crashed when it loaded the U1 profiles.
