# US-NECK-MOUNT-R008-FIT-SET: numbered clamp fit set

**Five clamp U sizes and one bar that fits all of them, numbered so you can
print the whole set at once and keep the U that fits. They add to
[US-NECK-MOUNT-R008](../r008-neck-mount/README.md): its enclosure back and Pi
carrier fit every U here.**

`manifest.json` records the source, file hashes, checks and the items that are
still unverified. `clamp-fit-set.png` shows the whole set with its numbers.

## Pick the U that fits

Start with U 1 and work up. Keep the first U that slides onto the tube by hand.
If a U needs force, try the next number. If it wobbles sideways once the bar is
tight, go back one.

| U | Tube pocket (mm) | Fits a tube of (mm) | A good fit feels like |
| --- | --- | --- | --- |
| 1 | 18.9 | 18.0 to 18.6 | Slides on by hand; no side wobble once tightened |
| 2 | 19.2 | 18.3 to 18.9 | Slides on by hand; no side wobble once tightened |
| 3 | 19.5 | 18.6 to 19.2 | Slides on by hand; no side wobble once tightened |
| 4 | 19.8 | 18.9 to 19.5 | Slides on by hand; no side wobble once tightened |
| 5 | 20.1 | 19.2 to 19.8 | Slides on by hand; no side wobble once tightened |

U 4 has the same pocket as the R008 clamp. The bar, marked "1-5", fits every
U.

## Print

| File | Contents |
| --- | --- |
| `clamp-fit-set-plate.3mf` | The whole plate, one named object per part, for your slicer |
| `clamp-fit-set-plate.stl` | The same plate as one STL |
| `clamp-u-1.stl` to `clamp-u-5.stl`, `clamp-bar-1-5.stl` | Each part on its own |

The parts are already in print orientation: the U's stand on their lower ends
and the bar lies flat with its number up. No part needs supports. The plate is
170 × 86 mm.

Use PETG with 0.2 mm layers, 6 perimeters, 5 top and bottom layers and 25 %
gyroid infill: the R006 clamp settings, which print these slim parts solid.

The whole plate takes about 90 g of PETG: 17 g for each U and 5 g for the bar.
It takes about 2 to 3.5 hours on a fast printer such as the Snapmaker U1. These
figures are estimated from the models, not sliced.

## How the set is sized

- **Steps.** The pockets are 0.3 mm apart. That is larger than the 0.2 mm
  accuracy Prusa gives for its printers, so neighbouring sizes feel different
  [@prusaModelingFor3dPrinting].
- **Fit window.** Each U fits tubes 0.3 to 0.9 mm narrower than its pocket:
  0.15 to 0.45 mm of play per side, around Prusa's 0.3 mm starting point for
  sliding fits [@prusaModelingFor3dPrinting]. Every tube size from 18.0 to
  19.8 mm is covered by two neighbouring U's. Printed pockets tend to come out
  slightly small [@hubsFdmDesign], so a U may fit a little tighter than the
  table says.
- **Depth.** The clamp grips front to back, so the bar takes up the tube's
  depth. In every U the arms stop 1 mm short of the smallest tube that U fits,
  so the bar always bears on the tube.
- **One bar for all.** Every U keeps R008's screw positions, 14.9 mm either
  side of the centre, and its outer width of 38.8 mm. The arm thickness absorbs
  the pocket change and leaves at least 1.45 mm, or three perimeters, between
  each nut slot and the pocket [@prusaModelingFor3dPrinting].
- **Same tongue.** Every U has R008's dovetail tongue (each measures
  4,549 mm³), so the printed enclosure back fits all of them.
- **Screws.** M3 × 16 screws fit every U.
- **Numbers.** The digits are Arial Bold at 9 mm: about 6.5 mm tall, with
  strokes of about 1.3 mm, above the 0.8 mm that every printer can make
  [@hubsKeyDesign3dPrinting]. They are sunk 0.6 mm, three 0.2 mm layers, into
  faces that face up as printed, so they print as top surfaces with no
  overhangs. The image shows them dark; printed, they are recesses in the
  same plastic.
- **No crush ribs.** None of the cited sources covers crush ribs. Because the
  clamp grips front to back, side play only affects how the fit feels, and the
  size steps already cover that.

## Hardware

For the U you keep, use the same screws as R008: 4 M3 × 16 mm socket-head
screws and 4 M3 hex nuts. The lock pin and the rest of the hardware are in the
R008 README.

## Not verified

- Which size fits the real tube, and how each fit feels.
- How readable the printed numbers are; this is judged from the geometry only.
- The print time and filament figures are estimates, not sliced.
