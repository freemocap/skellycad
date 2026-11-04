# US-NECK-MOUNT-R010: Pi mount print set with one screw size, M2.5

**Reprint only the clamp U and the clamp bar. The enclosure back and Pi
carrier are byte-identical to R006 to R009, so keep the ones you printed.**

The whole mount takes one screw size, M2.5, in two lengths: 16 mm and 6 mm.
M2.5 is the size that fits every part: the Pi 5's mounting holes are 2.7 mm
across, too small for an M3 screw [@raspberrypi2025Pi5Drawing], and the
AI HAT+, the Motor HAT and the PCA9685 already mount with M2.5. Only the clamp
and its lock used M3, so they change.

The clamp keeps U1's fit, which the user chose on the tube from the fit set
U1–U5: the same 18.9 mm pocket, arms, bar and dovetail, for a tube of about
18.0 to 18.6 mm per side. Its holes, nut slots and head recesses are resized
for M2.5. One change shows on the outside: the dovetail tongue is 7.5 mm
taller, 47.5 mm instead of 40. The taller tongue reaches the enclosure back's
lock hole, so the lock is one M2.5 × 16 screw through that hole into the
tongue, instead of an M3 × 40 pin with a nut. The enclosure back's hole takes
the M2.5 screw as it is, so the back is unchanged. Because the tongue is
taller, the enclosure sits 7.5 mm higher on the clamp than in R009.

No part needs supports. The print settings stay as in R006, whose shapes and
settings follow published FDM design guidance. If U1 wobbles sideways once the
bar is tight, the next step is a pocket 0.3 mm tighter (18.6 mm).

`manifest.json` records the source, file hashes, checks and the items that are
still unverified. Each part has an image with the same name as its STL file.

## Before printing: check the tube and the space

1. **Tube size.** The clamp fits a square tube from 18.0 to 18.6 mm per side;
   U1 was chosen on the robot's tube.
2. **Bare tube.** The clamp needs 20 mm of bare tube, with nothing fixed to any
   of its four faces. Its dovetail tongue rises 27.5 mm higher behind the tube
   without touching it.
3. **Space for the mount.** The whole mount is 104 mm tall, 81 mm wide and
   85 mm deep, from the front of the clamp bar to the back of the HAT stack.
   It hangs behind the tube from 10 mm below the bottom of the clamp to 94 mm
   above it. The clamp is 39 mm wide, and its bar sits 6 mm in front of the
   tube.

If the tube or the space does not match, do not print. Send the measurement,
and the CAD will be changed to fit.

## Print

| # | File | Part | Reprint | Orientation, as exported | Supports | Size (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `clamp-u.stl` | Clamp U: 18.9 mm pocket (U1), 20 mm body, 47.5 mm dovetail tongue, M2.5 nut slots and lock pilot | Yes | Standing on its lower end, tube opening vertical | None | 27 × 38.8 × 47.5 |
| 2 | `clamp-bar.stl` | Clamp bar, 20 mm tall, with M2.5 holes | Yes | Flat, screw-head recesses up | None | 20 × 38.8 × 6 |
| 3 | `enclosure-back.stl` | Enclosure back: frame, dovetail channel and PCA9685 wing (R006 file) | No, keep yours | Standing on its lower end | None | 41.7 × 71 × 104 |
| 4 | `pi-carrier.stl` | Pi carrier: frame with four standoffs (R006 file) | No, keep yours | Flat, standoffs up | None | 64 × 55 × 7.5 |

Every part fits on a 120 × 120 mm bed. Use PETG with 0.2 mm layers, the
default line width for a 0.4 mm nozzle, and these settings:

| Part | Perimeters | Top and bottom layers | Gyroid infill | Note |
| --- | --- | --- | --- | --- |
| Clamp U and clamp bar | 6 | 5 | 25 % | They take the screw load; at 6 perimeters their slim walls print solid. |
| Enclosure back | 3 | 4 | 15 % | Add a 5 mm brim: the part is tall and stands on a narrow edge. |
| Pi carrier | 3 | 3 | 15 % | |

The clamp U and bar take about 24 g of PETG and about 30 to 50 minutes on a
fast printer such as the Snapmaker U1. All four parts take about 57 g: 18 g
for the clamp U, 5 g for the bar, 31 g for the enclosure back and 3 g for the
carrier. These figures are estimated from the models at the settings above,
not sliced.

## Design guidance used

1. **Perimeters before infill.** A print's strength comes mostly from its
   perimeters, not its infill. Most parts need 10 to 15 % infill and rarely
   more than 30 % [@prusaLayersAndPerimeters; @prusaInfill]. In measured hook
   tests, thicker walls raised strength far more than the baseline settings
   [@cncKitchenExtrusionWidth]. So the enclosure back and the carrier use
   3 perimeters with 15 % infill. The clamp, which takes the screw load, uses
   6 perimeters with 25 % infill. That is denser than the 3 perimeters with
   30 % infill that CNC Kitchen uses for loaded parts [@cncKitchenPrintsVsWood],
   because six perimeters fill most of the clamp's walls.
2. **Gyroid infill.** Gyroid has equal strength in all directions and a good
   strength-to-weight ratio [@prusaInfillPatterns]. Every part uses it.
3. **Top layers.** At least 3 top layers stop sag over sparse infill
   [@prusaLayersAndPerimeters]. The parts use 3 to 5.
4. **Minimum wall.** A wall thinner than one perimeter, about 0.45 mm, cannot
   print [@prusaModelingFor3dPrinting]. Walls over 0.8 mm print on any printer
   [@hubsKeyDesign3dPrinting]. The clamp arms are 9.95 mm and keep at least
   three perimeters (1.35 mm) around every screw feature: 2.25 mm between each
   nut slot and the tube pocket, 1.95 mm beside each screw-head recess in the
   bar, and 1.95 mm between the lock pilot and the tip of the tongue.
   Elsewhere the thinnest walls are 1.55 mm around the carrier bores and 2 mm
   in the PCA9685 wing.
5. **Overhangs.** Overhangs up to 45° print without supports
   [@hubsFdmDesign; @prusaModelingFor3dPrinting]. Prusa allows 45 to 60°; R006
   uses the stricter 45° for three features:
   - the chamfer under the dovetail block;
   - the peaked tops of the frame windows;
   - the pointed undersides of the PCA9685 bosses.
6. **Bridges.** Bridges sag unless they are shorter than 5 mm [@hubsFdmDesign].
   - The frame windows have peaked tops instead of 10 to 22 mm flat bridges.
   - Horizontal holes are 5.6 mm or smaller, and the tops of the clamp's nut
     slots bridge 2.6 mm.
   - One bridge remains: the cap over the dovetail channel, about 20 mm wide. It
     stays flat because the enclosure rests on it. A slight sag only lifts the
     enclosure a few tenths of a millimetre on the tongue, and the lock screw
     still passes its hole, which has 0.45 mm of clearance all round.
7. **First-layer flare.** Edges on the build plate flare outward, so put a 45°
   chamfer on them where fit matters [@hubsFdmDesign]. The tube opening and the
   dovetail tongue of the clamp U have 0.5 mm chamfers where they meet the bed.
   The tube clearance (0.15 to 0.45 mm per side) and the 0.3 mm dovetail
   clearance are unchanged from R009.
8. **Screws into plastic.** For thread-forming screws in thermoplastics, the
   best pilot hole is 0.8 times the screw diameter, with a counterbore at the
   entry so that the boss does not crack [@semblexDeltaPt]. Printed holes come
   out undersized [@hubsFdmDesign]. So the PCA9685 pilot holes and the lock
   pilot across the clamp tongue are 2.1 mm, 0.84 times the 2.5 mm screw. Each
   PCA9685 hole has a 2.9 mm by 0.5 mm counterbore. The lock pilot has none:
   it enters the side of the solid tongue, not a boss. The source covers
   moulded bosses and special thread-forming screws. Using it for M2.5 machine
   screws in printed PETG is an untested extrapolation.
9. **Layer direction.** FDM parts are weaker between layers, so print
   structural parts with their loads along the layers
   [@prusaModelingFor3dPrinting; @hubsFdmDesign; @cncKitchenPrintsVsWood].
   - The clamp U prints standing, so the screw tension and the dovetail loads
     run along its layers.
   - The bar prints flat, so the screw heads press across its layers.
   - The enclosure back's hanging load crosses layers only in its lightly loaded
     lower frame.
10. **Sliding fits.** Moving fits start at 0.3 mm of clearance
    [@prusaModelingFor3dPrinting]. The fit set bracketed the uncertain tube in
    0.3 mm steps, more than the 0.2 mm accuracy Prusa gives for its printers.
    U1's 18.9 mm pocket leaves 0.15 to 0.45 mm per side on an 18.0 to 18.6 mm
    tube, around that 0.3 mm start, and the user picked it on the real tube.
    The clamp grips front to back, and the arms stop 1 mm short of an 18.0 mm
    tube's front face, so the bar always bears on the tube. The dovetail keeps
    its 0.3 mm clearance.
11. **Rounded corners.** Prusa recommends chamfers rather than fillets on edges
    that face the bed [@prusaModelingFor3dPrinting]. The clamp's rounded
    corners are on edges that stand vertical as printed, so they print as
    walls; the edges on the bed keep 0.5 mm chamfers.
12. **Clearance holes.** Moving fits start at 0.3 mm of clearance
    [@prusaModelingFor3dPrinting], and vertical holes print undersized
    [@hubsFdmDesign]. So the clamp's M2.5 clearance holes are 2.9 mm, 0.4 mm
    over the screw, the same allowance as the 3.4 mm holes R006 used for M3.
    The screw-head recesses in the bar are 5.1 mm across and 2.7 mm deep for
    the M2.5 head of 4.5 by 2.5 mm. The enclosure back's lock hole stays
    3.4 mm, so the M2.5 lock screw passes it with 0.45 mm of clearance all
    round.

The sources I read do not cover these points, so the earlier rules stay:

- **Nut slots.** No printer maker or print service gives nut-trap sizes. The
  slots keep R006's allowance. They are 5.4 mm wide: 0.4 mm over the M2.5
  nut's 5.0 mm across flats, and narrower than its 5.8 mm across corners, so
  the nut cannot turn. They are 2.6 mm thick, 0.6 mm over the 2.0 mm nut, and
  reach 3.2 mm past the screw axis, so the nut can centre on the screw.
- **Screw engagement and boss size in printed parts.** The PCA9685 screws
  engage about 4.4 mm, 1.8 times their diameter, and the bosses are 5.4 mm
  across, 2.2 times the diameter. The lock screw engages 10.2 mm of the
  tongue, 4.1 times its diameter.
- **Ribs.** No rib rules specific to FDM were found. The frame-style enclosure
  back follows the perimeter rule above instead: material goes into thin rails
  and walls rather than solid blocks.
- **Snap fits.** This design has none.
- **Clamp height.** No source gives a minimum height for a screw clamp. The
  clamp body stays 20 mm. Its two rows of M2.5 nut slots leave 2.3 mm of
  plastic above and below them and 4.6 mm between them.

## Hardware

Every screw is an M2.5 socket-head cap screw, 6 mm or 16 mm long.

| Qty | Length | Item | Use |
| --- | --- | --- | --- |
| 4 | 16 mm | M2.5 socket-head screw | Clamp bar to the U, into the captured nuts |
| 4 | 16 mm | M2.5 socket-head screw | From the front face of the enclosure back, through the carrier's standoffs and the Pi, into the AI HAT+ spacers |
| 1 | 16 mm | M2.5 socket-head screw | Lock: through the lock hole in the enclosure's dovetail block, into the clamp tongue |
| 4 | 6 mm | M2.5 socket-head screw | Motor HAT onto its standoffs |
| 4 | 6 mm | M2.5 socket-head screw | PCA9685 into the printed bosses; the screws cut their own thread in the 2.1 mm pilot holes |
| 4 | – | M2.5 hex nut, 5.0 mm across flats | In the U's four side slots |
| 4 | 10 or 12 mm | M2.5 male-female standoff | Between the AI HAT+ and the Motor HAT; measure the header gap and use 10 or 12 (assembly step 6) |
| 4 | 16 mm | M2.5 spacer, supplied with the AI HAT+ [@raspberrypi2024AiHatBrief] | Pi to AI HAT+; nothing to buy. Assumed to be threaded at both ends |

In total: 9 screws of M2.5 × 16, 8 screws of M2.5 × 6, 4 nuts and 4 standoffs.
You also need 2 or more zip ties, up to 4.8 mm wide, for the wire bundle.

**Buy this:** M2.5 socket-head cap screws in 6 mm and 16 mm (at least 8 and
9), M2.5 hex nuts 5.0 mm across flats (at least 4), and M2.5 male-female
standoffs in 10 mm and 12 mm (4 of the length that fits).

## Assembly

1. Push one M2.5 nut into each of the four side slots near the open end of the
   U.
2. Place the U behind the tube, with the dovetail tongue facing away from the
   tube and the arms along its sides. Hold the bar across the front of the
   tube, and put four M2.5 × 16 screws through the bar into the nuts.
3. Slide the clamp to its height. If it replaces an R009 clamp, fit it 7.5 mm
   lower on the tube to keep the electronics at the same height. Tighten the
   four screws evenly until the clamp does not slide or turn.
4. Put the carrier against the back of the enclosure back, standoffs facing
   away, and set the Pi on the standoffs. Insert four M2.5 × 16 screws from
   the front face of the enclosure back, through the carrier and the Pi, into
   the AI HAT+ spacers.
5. Connect the AI HAT+ ribbon, and fit the AI HAT+ on its spacers and stacking
   header.
6. Choose the Motor HAT standoffs. Press the Motor HAT fully onto the header,
   measure the gap between the AI HAT+ and the Motor HAT, and take the Motor
   HAT off. If the gap is 10 mm or less, use the 10 mm standoffs. If it is
   more than 10 mm and up to 12 mm, use the 12 mm standoffs. If it is more
   than 12 mm, stop and send the measurement.
7. Screw the four standoffs through the AI HAT+ into the spacers below. Plug in
   the Motor HAT and fasten it with four M2.5 × 6 screws.
8. Screw the PCA9685 to the side wing with four M2.5 × 6 screws, with its servo
   connectors facing out. Connect its wires, and tie the bundle to the top tab.
9. Lower the enclosure onto the clamp: the channel slides down over the tongue
   until the enclosure rests on the top of the tongue. Put one M2.5 × 16 screw
   through the lock hole on either side of the dovetail block, and screw it
   into the tongue until its head is snug against the block. Do not force it:
   the screw cuts its own thread in the plastic.

To remove the electronics, take out the lock screw and lift the enclosure off.
The clamp stays on the tube.

## Clearances

These are the fits:

- The tube pocket is 18.9 mm wide: 0.15 to 0.45 mm per side on an 18.0 to
  18.6 mm tube.
- The arms stop short of the tube's front face, so the bar always bears on the
  tube. After tightening, the gap between the bar and the arms is 1 mm on an
  18.0 mm tube, 1.3 mm on an 18.3 mm tube and 1.6 mm on an 18.6 mm tube.
- The clamp takes M2.5 screws from 13.9 to 21.8 mm long. A 16 mm screw passes
  its nut by at least 3.6 mm and stops at least 7.3 mm short of the end of its
  hole.
- The screw holes end 2 mm before the back of the U, so no screw reaches the
  enclosure.
- The dovetail has 0.3 mm of clearance.
- The lock screw passes the enclosure's 3.4 mm hole with 0.45 mm of clearance
  all round and threads 10.2 mm into the tongue. Its pilot runs right across
  the tongue, so the screw goes in from either side.

The 0.5 mm bed chamfers keep the first layer's flare out of these fits. The
carrier holds the Pi at the same height above the plate as the community case
it replaced did, so the stack and its screws are unchanged. The PCA9685 wing
stands 6.5 mm beside the Pi board.

## Not verified

- The M2.5 clamp U and bar are unprinted. They keep U1's pocket, which the
  user chose by hand on the tube; the grip under the robot's motion is
  untested.
- Printed fits: the tube and dovetail fits, the M2.5 nut slots, and the M2.5
  threads in the 2.1 mm pilot holes of the PCA9685 bosses and the tongue.
- The strength of the lighter parts: the clamp's grip on the tube, the
  frame-style enclosure back, and whether one M2.5 lock screw holds the
  enclosure while the robot moves. The lock screw's thread in the tongue may
  wear if the screw is taken out often.
- The Motor HAT standoff length (10 or 12 mm, chosen at assembly) and the
  thread type of the AI HAT+ spacers.
- The wiring is drawn schematically; cable lengths and the bundle route are
  unchecked.
- Heat: the Pi 5 and the AI HAT+ are open on all sides; their temperatures are
  unchecked.
- The print time and filament figures are estimates, not sliced. The Snapmaker
  Orca command line crashed when it loaded the U1 profiles.
