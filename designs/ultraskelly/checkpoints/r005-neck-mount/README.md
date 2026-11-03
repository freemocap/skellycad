# US-NECK-MOUNT-R005: light Pi mount print set

This checkpoint is the complete set of printed parts for the Pi mount on the
13.35 mm square tube. It works like R004 and keeps its fits and hardware, but
it uses about a third of the plastic:

- The clamp is shorter and thinner.
- The enclosure back is a frame with windows.
- A light carrier with four standoffs replaces the community Pi case.

No part needs supports. Print all four files.

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
   46.5 mm above its top. The clamp is 32 mm wide, and its bar sits 6 mm in
   front of the tube.

If the tube or the space does not match, do not print. Send the measurement,
and the CAD will be changed to fit.

## Print

| # | File | Part | Orientation, as exported | Supports | Size (mm) |
| --- | --- | --- | --- | --- | --- |
| 1 | `clamp-u.stl` | Clamp U with the dovetail tongue | Standing on its lower end, tube opening vertical | None | 22.3 × 32.2 × 40 |
| 2 | `clamp-bar.stl` | Clamp bar | Flat, screw-head recesses up | None | 40 × 32.2 × 6 |
| 3 | `enclosure-back.stl` | Enclosure back: frame, dovetail channel and PCA9685 wing | Standing on its lower end | None | 41.7 × 71 × 104 |
| 4 | `pi-carrier.stl` | Pi carrier: frame with four standoffs | Flat, standoffs up | None | 64 × 55 × 7.5 |

Every part fits on a 120 × 120 mm bed. Use PETG with 0.2 mm layers and these
settings:

| Part | Walls | Top and bottom layers | Gyroid infill | Note |
| --- | --- | --- | --- | --- |
| Clamp U and clamp bar | 4 | 4 | 25 % | These take the screw load, so keep them stronger. |
| Enclosure back | 3 | 4 | 15 % | Add a 5 mm brim: the part is tall and stands on a narrow edge. |
| Pi carrier | 3 | 3 | 15 % | |

The dovetail block has a 45° chamfer underneath, so it prints without supports.
The windows and the cap over the dovetail channel print as short bridges, up to
22 mm.

All four parts together take about 56 g of PETG, compared with about 157 g for
R004. Printing takes about 1.5 to 2 hours on a fast printer such as the
Snapmaker U1, compared with 3.5 to 6 hours for R004. All these figures are
estimated from the models, not sliced; your slicer gives the actual numbers.

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
| 4 | M2.5 × 6 mm screw | PCA9685 into the printed bosses; the screws cut their own thread. A longer screw comes through the wing. |
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

The carrier holds the Pi at the same height above the plate as the R004 case
did, so the stack and its screws are unchanged. The PCA9685 wing stands 6.5 mm
beside the Pi board.

## Not verified

- The tube size comes from one measurement of a flat side.
- Printed fits: the tube and dovetail fits, the nut slots, and the M2.5 threads
  in the PCA9685 bosses.
- The strength of the lighter parts and settings: the clamp's grip on the tube,
  the frame-style enclosure back, and whether one M3 pin holds the enclosure
  while the robot moves.
- The Motor HAT spacer height (11 mm is an estimate) and the thread type of the
  AI HAT+ spacers.
- The wiring is drawn schematically; cable lengths and the bundle route are
  unchecked.
- Heat: the Pi 5 and the AI HAT+ are open on all sides; their temperatures are
  unchecked.
- The print time and filament figures are estimates, not sliced.
