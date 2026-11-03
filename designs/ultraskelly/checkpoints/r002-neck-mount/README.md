# US-NECK-MOUNT-R002: neck mount print set

This checkpoint is the complete set of printed parts for the neck mount. The
clamp grips the 1 inch spine tube. The enclosure carries the Pi 5 stack and the
PCA9685, and it slides onto the clamp. Print all four files. `manifest.json`
records the source, file hashes, checks and the items that are still
unverified. The clamp U and bar are byte-identical to the files in
[US-NECK-CLAMP-R001](../r001-neck-clamp/README.md).

## Before printing: check the robot

The robot in the CAD is an estimated mock-up. Take two measurements with a
ruler:

1. Measure the bare spine tube between the top of the shoulder piece and the
   bottom of the neck drive. It must be at least 70 mm; the mock-up assumes
   85 mm.
2. Measure how far the neck drive and the shoulder piece stick out behind the
   back face of the tube. Each must be no more than 12 mm, because the
   enclosure passes 15 mm behind the tube, beside both parts.

If either measurement is outside its limit, do not print. Send the
measurement, and the CAD will be adjusted to fit.

## Print

| # | File | Part | Orientation, as exported | Supports | Size (mm) |
| --- | --- | --- | --- | --- | --- |
| 1 | `clamp-u.stl` | Clamp U with the dovetail tongue | Standing on its lower end, tube channel vertical | None | 36.7 × 46 × 50 |
| 2 | `clamp-bar.stl` | Clamp bar | Flat, screw-head recesses up | None | 50 × 46 × 8 |
| 3 | `enclosure-back.stl` | Enclosure back with the dovetail channel and the PCA9685 wing | Standing on its lower end | Under the dovetail block only | 42.7 × 75 × 121 |
| 4 | `pi-case-30mm.stl` | Pi case, 30 mm deep (already shortened in the CAD) [@omtPi5Case] | Floor on the bed, open side up | None | 102 × 66 × 30 |

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

All four parts together take about 165 g of PETG and 4.5 to 12 hours of
printing: about 4.5 hours on a fast current printer and up to 12 hours on an
older one. These figures are estimated from the model volume, not sliced; your
slicer gives the actual time.

## Hardware

| Qty | Item | Use |
| --- | --- | --- |
| 4 | M3 × 25 mm socket-head screw (25 to 35 mm fits) | Clamp bar to the U |
| 5 | M3 hex nut, 5.5 mm across flats | 4 in the U's side slots, 1 on the lock pin |
| 1 | M3 × 40 mm screw | Lock pin through the enclosure, below the tongue |
| 4 | M2.5 × 16 mm socket-head screw | From the front face of the enclosure back, through the case floor and the Pi, into the AI HAT+ spacers |
| 4 | M2.5 × 16 mm spacer | Supplied with the AI HAT+ [@raspberrypi2024AiHatBrief]; assumed to be threaded at both ends |
| 4 | M2.5 male-female spacer, about 11 mm | Between the AI HAT+ and the Motor HAT; the height is an estimate, so measure the header gap first |
| 4 | M2.5 × 6 mm screw | Motor HAT onto its spacers |
| 4 | M2.5 × 6 mm screw | PCA9685 into the printed bosses; the screws cut their own thread. A longer screw comes through the wing and touches the case. |
| 2 or more | Zip tie, up to 4.8 mm wide | Wire bundle, through the two slots in the top tab |

## Assembly

1. Push one M3 nut into each of the four side slots in the U.
2. Place the U behind the spine tube, with the dovetail tongue facing the back
   of the robot. Hold the bar against the front of the tube, and put the four
   M3 × 25 screws through the bar into the nuts.
3. Leave 9 mm between the top of the U and the bottom of the neck drive. Tighten
   the four screws evenly until the clamp does not slide or turn.
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

The gaps below were measured in the CAD against the estimated mock-up, with
9 mm between the top of the U and the neck drive.

| Robot part | Gap (mm) | Closest point |
| --- | --- | --- |
| Neck drive | 3.0 | The enclosure back passes behind the drive. The top of the dovetail block is 5.0 mm below it. |
| Shoulder piece | 8.0 | The lower end of the enclosure back passes behind it. |
| Ribcage | 6.2 | Below the lower end of the enclosure back. |
| Jaw | 52 or more | Above the enclosure back. |
| Skull | 62 or more | Above the enclosure back. |

The first on-robot check placed the U 5 mm below the neck drive. There, the top
of the dovetail block was only 1.0 mm from the drive; the 9 mm placement gives
it 5.0 mm, and the other gaps stay at 3 mm or more.

The fits between printed parts are deliberate: 0.3 mm around the tube and in
the dovetail, a 1 mm take-up gap between the bar and the U, and 0.5 mm around
the case and beside the PCA9685 wing.

## Not verified

- The robot parts are an estimated mock-up, so every gap above is an estimate
  until the two measurements under "Before printing" are taken.
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
