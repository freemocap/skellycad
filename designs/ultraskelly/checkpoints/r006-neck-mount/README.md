# US-NECK-MOUNT-R006: light Pi mount print set

This checkpoint is the complete set of printed parts for the Pi mount on the
13.35 mm square tube. It works like R004 and keeps the R004 fits and hardware,
but it uses well under half of the R004 plastic. Its shapes and print settings
follow published FDM design guidance; "Design guidance used" below lists each
rule and the change it drove. No part needs supports. Print all four files.

`manifest.json` records the source, file hashes, checks and the items that are
still unverified. Each part has an image with the same name as its STL file.
`before-after.png` compares each part with R004 at the same scale.

## Before printing: check the tube and the space

1. **Tube size.** The clamp fits a square tube from 12.5 to 14 mm per side. It
   is sized for the measured 13.35 mm.
2. **Bare tube.** The clamp needs 40 mm of bare tube, with nothing fixed to any
   of its four faces.
3. **Space for the mount.** The whole mount is 104 mm tall, 81 mm wide and
   80 mm deep, from the front of the clamp bar to the back of the HAT stack.
   It hangs behind the tube from 17.5 mm below the bottom of the clamp to
   46.5 mm above its top. The clamp is 34 mm wide, and its bar sits 6 mm in
   front of the tube.

If the tube or the space does not match, do not print. Send the measurement,
and the CAD will be changed to fit.

## Print

| # | File | Part | Orientation, as exported | Supports | Size (mm) |
| --- | --- | --- | --- | --- | --- |
| 1 | `clamp-u.stl` | Clamp U with the dovetail tongue | Standing on its lower end, tube opening vertical | None | 22.3 × 34.2 × 40 |
| 2 | `clamp-bar.stl` | Clamp bar | Flat, screw-head recesses up | None | 40 × 34.2 × 6 |
| 3 | `enclosure-back.stl` | Enclosure back: frame, dovetail channel and PCA9685 wing | Standing on its lower end | None | 41.7 × 71 × 104 |
| 4 | `pi-carrier.stl` | Pi carrier: frame with four standoffs | Flat, standoffs up | None | 64 × 55 × 7.5 |

Every part fits on a 120 × 120 mm bed. Use PETG with 0.2 mm layers, the
default line width for a 0.4 mm nozzle, and these settings:

| Part | Perimeters | Top and bottom layers | Gyroid infill | Note |
| --- | --- | --- | --- | --- |
| Clamp U and clamp bar | 6 | 5 | 25 % | They take the screw load, so they get the strongest settings. |
| Enclosure back | 3 | 4 | 15 % | Add a 5 mm brim: the part is tall and stands on a narrow edge. |
| Pi carrier | 3 | 3 | 15 % | |

All four parts together take about 65 g of PETG, compared with about 157 g for
R004. Printing takes about 1.5 to 2.5 hours on a fast printer such as the
Snapmaker U1, compared with 3.5 to 6 hours for R004. These figures are
estimated from the models at the settings above, not sliced; your slicer gives
the actual numbers.

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
   [@hubsKeyDesign3dPrinting]. R005 left only 0.4 mm between each screw-head
   recess and the edge of the clamp bar. R006 widens the clamp arms back to
   10 mm, which gives 1.4 mm, or three perimeters. The thinnest walls left are
   1.4 mm at those recesses, 1.55 mm around the carrier bores and 2 mm in the
   PCA9685 wing.
5. **Overhangs.** Overhangs up to 45° print without supports
   [@hubsFdmDesign; @prusaModelingFor3dPrinting]. Prusa allows 45 to 60°; R006
   uses the stricter 45° for three features:
   - the chamfer under the dovetail block;
   - the peaked tops of the frame windows;
   - the pointed undersides of the PCA9685 bosses.
6. **Bridges.** Bridges sag unless they are shorter than 5 mm [@hubsFdmDesign].
   - The frame windows have peaked tops instead of 10 to 22 mm flat bridges.
   - Horizontal holes are 5.6 mm or smaller.
   - One bridge remains: the cap over the dovetail channel, about 20 mm wide. It
     stays flat because the enclosure rests on it. A slight sag only lifts the
     enclosure a few tenths of a millimetre on the tongue, and the lock pin
     still clears.
7. **First-layer flare.** Edges on the build plate flare outward, so put a 45°
   chamfer on them where fit matters [@hubsFdmDesign]. The tube opening and the
   dovetail tongue of the clamp U have 0.5 mm chamfers where they meet the bed.
   The 0.4 mm tube clearance and the 0.3 mm dovetail clearance are unchanged.
8. **Screws into plastic.** For thread-forming screws in thermoplastics, the
   best pilot hole is 0.8 times the screw diameter, with a counterbore at the
   entry so that the boss does not crack [@semblexDeltaPt]. Printed holes come
   out undersized [@hubsFdmDesign]. So the PCA9685 pilot holes are 2.1 mm,
   0.84 times the 2.5 mm screw, instead of R005's 2.4 mm, which was 0.96 times.
   Each hole has a 2.9 mm by 0.5 mm counterbore. The source covers moulded
   bosses and special thread-forming screws. Using it for M2.5 machine screws in
   printed PETG is an untested extrapolation.
9. **Layer direction.** FDM parts are weaker between layers, so print
   structural parts with their loads along the layers
   [@prusaModelingFor3dPrinting; @hubsFdmDesign; @cncKitchenPrintsVsWood].
   - The clamp U prints standing, so the screw tension and the dovetail loads
     run along its layers.
   - The bar prints flat, so the screw heads press across its layers.
   - The enclosure back's hanging load crosses layers only in its lightly loaded
     lower frame.
10. **Sliding fits.** Moving fits start at 0.3 mm of clearance
    [@prusaModelingFor3dPrinting]. This agrees with the 0.3 mm dovetail and
    0.4 mm tube clearances kept from R004.

The sources I read do not cover these points, so the R004 choices stay:

- **Nut slots.** No printer maker or print service gives nut-trap sizes. The
  slots stay at 5.9 mm, which is 0.4 mm over the nut's 5.5 mm across flats,
  and 3.0 mm wide for the 2.4 mm nut.
- **Screw engagement and boss size in printed parts.** The PCA9685 screws
  engage about 4.4 mm, 1.8 times their diameter. The bosses are 5.4 mm across,
  2.2 times the diameter.
- **Ribs.** No rib rules specific to FDM were found. The frame-style enclosure
  back follows the perimeter rule above instead: material goes into thin rails
  and walls rather than solid blocks.
- **Snap fits.** This design has none.

## Hardware

| Qty | Item | Use |
| --- | --- | --- |
| 4 | M3 × 16 mm socket-head screw | Clamp bar to the U |
| 5 | M3 hex nut, 5.5 mm across flats | 4 in the U's side slots, 1 on the lock pin |
| 1 | M3 × 40 mm screw (35 mm also fits) | Lock pin through the enclosure, below the tongue |
| 4 | M2.5 × 16 mm socket-head screw | From the front face of the enclosure back, through the carrier's standoffs and the Pi, into the AI HAT+ spacers |
| 4 | M2.5 × 16 mm spacer | Supplied with the AI HAT+ [@raspberrypi2024AiHatBrief]; assumed to be threaded at both ends |
| 4 | M2.5 male-female spacer, about 11 mm | Between the AI HAT+ and the Motor HAT; the height is an estimate, so measure the header gap first |
| 4 | M2.5 × 6 mm screw | Motor HAT onto its spacers |
| 4 | M2.5 × 6 mm screw | PCA9685 into the printed bosses; the screws cut their own thread in the 2.1 mm pilot holes |
| 2 or more | Zip tie, up to 4.8 mm wide | Wire bundle, through the two slots in the top tab |

## Assembly

1. Push one M3 nut into each of the four side slots near the open end of the
   U.
2. Place the U behind the tube, with the dovetail tongue facing away from the
   tube and the arms along its sides. Hold the bar across the front of the
   tube, and put the four M3 × 16 screws through the bar into the nuts.
3. Slide the clamp to its height. Tighten the four screws evenly until the
   clamp does not slide or turn.
4. Put the carrier against the back of the enclosure back, standoffs facing
   away, and set the Pi on the standoffs. Insert the four M2.5 × 16 screws from
   the front face of the enclosure back, through the carrier and the Pi, into
   the AI HAT+ spacers.
5. Connect the AI HAT+ ribbon, and fit the AI HAT+ on its spacers and stacking
   header. Screw the 11 mm spacers through the AI HAT+ into the spacers below.
   Plug in the Motor HAT and fasten it with four M2.5 × 6 screws.
6. Screw the PCA9685 to the side wing with four M2.5 × 6 screws, with its servo
   connectors facing out. Connect its wires, and tie the bundle to the top tab.
7. Lower the enclosure onto the clamp: the channel slides down over the tongue
   until the enclosure rests on the top of the tongue. Push the M3 × 40 screw
   through the hole below the tongue, and fit the nut.

To remove the electronics, take out the lock pin and lift the enclosure off.
The clamp stays on the tube.

## Clearances

These fits are the same as in R004:

- The clamp leaves 0.4 mm between the tube and the U at the sides and at the
  back, so the U slides along the tube before you tighten it.
- The arms stop 1.5 mm short of the tube's front face, so the bar always bears
  on the tube. On a 13.35 mm tube, 1.1 mm of that gap remains after
  tightening.
- The screw holes end 2 mm before the back of the U, so no screw reaches the
  enclosure.
- The dovetail has 0.3 mm of clearance.

The 0.5 mm bed chamfers keep the first layer's flare out of these fits. The
carrier holds the Pi at the same height above the plate as the R004 case did,
so the stack and its screws are unchanged. The PCA9685 wing stands 6.5 mm
beside the Pi board.

## Not verified

- The tube size comes from one measurement of a flat side.
- Printed fits: the tube and dovetail fits, the nut slots, and the M2.5 threads
  in the 2.1 mm PCA9685 pilot holes.
- The strength of the lighter parts: the clamp's grip on the tube, the
  frame-style enclosure back, and whether one M3 pin holds the enclosure while
  the robot moves.
- The Motor HAT spacer height (11 mm is an estimate) and the thread type of the
  AI HAT+ spacers.
- The wiring is drawn schematically; cable lengths and the bundle route are
  unchecked.
- Heat: the Pi 5 and the AI HAT+ are open on all sides; their temperatures are
  unchecked.
- The print time and filament figures are estimates, not sliced. The Snapmaker
  Orca command line crashed when it loaded the U1 profiles.
