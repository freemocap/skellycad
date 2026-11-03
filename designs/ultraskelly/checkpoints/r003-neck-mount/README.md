# US-NECK-MOUNT-R003: neck mount print set

This checkpoint is the complete set of printed parts for the neck mount. The
mount is sized for the measured 133.5 mm square neck tube. The clamp grips the
tube, and the enclosure carries the Pi 5 stack and the PCA9685 and slides onto
the clamp. Print all four files. `manifest.json` records the source, file
hashes, checks and the items that are still unverified. Each part has an image
with the same name as its STL file.

## Before printing: check the robot

The parts in the CAD are fitted to a 133.5 mm square tube. Before printing,
check the following on the robot:

1. **Tube size.** The clamp fits a tube 131 to 140 mm deep (front to back) and
   up to 136 mm wide (side to side).
2. **Free length.** You need at least 127 mm of tube with nothing fixed to its
   back face: the mount is 121 mm tall, plus 3 mm above and below. The clamp
   occupies 50 mm of that length, starting 33.5 mm above its lower end, and
   needs all four faces of the tube bare there.
3. **Space around the tube.** Over the mount's height, keep these distances
   clear:

   | Where | Clear space needed (mm) | Part that needs it |
   | --- | --- | --- |
   | Behind the back face of the tube | 66, plus room for the wires | Enclosure, Pi case and HAT stack |
   | Beside each side face | 12 | Clamp arms, over the clamp's 50 mm |
   | In front of the front face | 9 | Clamp bar, over the clamp's 50 mm |

If the robot does not meet one of these checks, do not print. Send the
measurement, and the CAD will be changed to fit.

## Print

| # | File | Part | Orientation, as exported | Supports | Size (mm) |
| --- | --- | --- | --- | --- | --- |
| 1 | `clamp-u.stl` | Clamp U with the dovetail tongue | Standing on its lower end, tube opening vertical | None | 143 × 156.5 × 50 |
| 2 | `clamp-bar.stl` | Clamp bar | Flat, screw-head recesses up | None | 50 × 156.5 × 8 |
| 3 | `enclosure-back.stl` | Enclosure back with the dovetail channel and the PCA9685 wing | Standing on its lower end | Under the dovetail block only | 42.7 × 75 × 121 |
| 4 | `pi-case-30mm.stl` | Pi case, 30 mm deep (already shortened in the CAD) [@omtPi5Case] | Floor on the bed, open side up | None | 102 × 66 × 30 |

The clamp U needs a print bed of at least 170 × 160 mm.

Use PETG with 0.2 mm layers, 4 walls, 5 top and bottom layers and 40 % gyroid
infill. Add a 5 mm brim to the enclosure back, because it is tall and stands on
a narrow edge.

The enclosure back needs supports under its dovetail block only. The block
starts 22 mm above the bed and sticks out 9 mm from the plate. Set supports to
"on build plate only", and keep them out of the dovetail channel: turn on
"don't support bridges" or put a support blocker in the channel. The holes, the
PCA9685 bosses and the 2 mm lips print without supports.

The Pi case prints without supports. The openings in its walls print as
bridges; the longest is 54 mm, over the opening at one end. It can sag slightly,
but no other part fits against it.

All four parts together take about 293 g of PETG. Printing takes about 8 hours
on a fast current printer and up to 21 hours on an older one. These figures are
estimated from the model volume, not sliced; your slicer gives the actual time.

## Hardware

| Qty | Item | Use |
| --- | --- | --- |
| 4 | M3 × 30 mm socket-head screw (25 mm also fits) | Clamp bar to the U |
| 5 | M3 hex nut, 5.5 mm across flats | 4 in the U's side slots, 1 on the lock pin |
| 1 | M3 × 40 mm screw | Lock pin through the enclosure, below the tongue |
| 4 | M2.5 × 16 mm socket-head screw | From the front face of the enclosure back, through the case floor and the Pi, into the AI HAT+ spacers |
| 4 | M2.5 × 16 mm spacer | Supplied with the AI HAT+ [@raspberrypi2024AiHatBrief]; assumed to be threaded at both ends |
| 4 | M2.5 male-female spacer, about 11 mm | Between the AI HAT+ and the Motor HAT; the height is an estimate, so measure the header gap first |
| 4 | M2.5 × 6 mm screw | Motor HAT onto its spacers |
| 4 | M2.5 × 6 mm screw | PCA9685 into the printed bosses; the screws cut their own thread. A longer screw comes through the wing and touches the case. |
| 2 or more | Zip tie, up to 4.8 mm wide | Wire bundle, through the two slots in the top tab |

## Assembly

1. Push one M3 nut into each of the four side slots near the open end of the
   U.
2. Place the U behind the neck tube, with the dovetail tongue facing the back of
   the robot and the arms along the sides of the tube. Hold the bar across the
   front of the tube, and put the four M3 × 30 screws through the bar into the
   nuts.
3. Slide the clamp to its height within the free length. Tighten the four screws
   evenly until the clamp does not slide or turn.
4. Put the case against the back of the enclosure back, inside the lips, and put
   the Pi in the case. Insert the four M2.5 × 16 screws from the front face of
   the enclosure back, through the case and the Pi, into the AI HAT+ spacers.
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

The clamp leaves 1.5 mm between the tube and the U at the sides and at the
back, so the U slides along the tube before you tighten it. The arms stop 4 mm
short of the tube's front face, so the bar always bears on the tube. On a
133.5 mm tube, 2.5 mm of that gap remains after tightening. The other fits are
0.3 mm in the dovetail, and 0.5 mm around the case and beside the PCA9685 wing.

Clearances to the rest of the robot are unchecked. This project's skeleton
mock-up was built around a 1 inch spine, so it does not match the 133.5 mm tube.
The space table under "Before printing" replaces that check.

## Not verified

- The tube size comes from one measurement of a flat face; the depth of the tube
  and the space around it are unchecked.
- Printed fits: the tube and dovetail fits, the nut slots, and the M2.5 threads
  in the PCA9685 bosses.
- The clamp's grip on the tube, and whether one M3 pin holds the enclosure while
  the robot moves.
- The Motor HAT spacer height (11 mm is an estimate) and the thread type of the
  AI HAT+ spacers.
- The wiring is drawn schematically; cable lengths and the bundle route are
  unchecked.
- Heat: the Pi 5 and the AI HAT+ run in a case that is open at the back; their
  temperatures are unchecked.
- The print time and filament figures are estimates, not sliced.

## License

`pi-case-30mm.stl` is derived from the Open Media Transport Raspberry Pi 5 case
[@omtPi5Case], which is MIT licensed. Its license is in
`LICENSE-omt-case.txt` and ships with the file.
