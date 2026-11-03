# US-NECK-CLAMP-R001: neck clamp grip test

The U clamp and front bar from the approved clamp-and-enclosure concept, released
to test their grip on the robot's 1 inch square spine tube before the enclosure
is printed. `manifest.json` records the source commit, file hashes, geometry
checks and the open questions. Physical fit is unverified.

## Print

| File | Orientation | Size (mm) |
| --- | --- | --- |
| `clamp-u.stl` | As exported: standing on its lower end, tube channel vertical | 36.7 × 46 × 50 |
| `clamp-bar.stl` | As exported: flat, screw-head recesses facing up | 50 × 46 × 8 |

Use PETG if you have it; PLA is fine for a fit test. Suggested settings are
0.2 mm layers, 4 walls, 5 top and bottom layers, 40 % gyroid infill and no
supports. Both parts together should take about 1 to 1.5 hours and 50 g of
filament; this is an estimate from the model volume, not a sliced time.

## Hardware

- 4 × M3 socket-head screws, 25 to 40 mm long.
- 4 × M3 hex nuts, 5.5 mm across flats.

## Fit the clamp

1. Push one nut into each of the four side slots in the U's arms until it lines
   up with the screw hole.
2. Place the U behind the spine tube, with the dovetail tongue facing the
   skeleton's back.
3. Hold the bar against the front of the tube.
4. Insert the four screws through the bar into the nuts.
5. Tighten the screws evenly, a little at a time, until the clamp no longer
   slides when you push and twist it by hand.

## Report

- Whether the nuts seat in their slots.
- Whether the U slides onto the tube before tightening, and holds without
  slipping or turning after tightening.
- Any cracking at the screw holes or arms.
- The free tube length behind the neck, from the top of the shoulder piece to
  the bottom of the head mechanism. The enclosure needs about 120 mm there.

The enclosure back, which slides onto this tongue, is printed after the grip
test so that any change to the clamp can carry over to its channel.
