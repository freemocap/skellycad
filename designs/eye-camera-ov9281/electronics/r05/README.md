# R05 head-to-controller interface

Open [the rendered overview](overview.html). R05 adds a physical connector on the
controller, solder lands on the sensor head, and an editable flex connectivity
study. It preserves R04's existing component placement and copper. This remains
an incomplete camera design, not a fabrication release.

## Physical arrangement

The 32 × 20 mm controller uses J102, a candidate Hirose
FH34SRJ-24S-0.5SH(99). Its specified body is 14 × 3.8 × 1 mm, with 24 contacts
at 0.5 mm pitch [@hiroseFh34Product]. Its footprint fits without moving the P4,
USB parts or crystal. J201 adds 24 solder lands to the front of the existing
14 × 14 mm sensor head. It adds no connector housing at the head.

The straight flex study is 35.3 × 12.5 mm, including its end overlaps; the clear
gap between boards is 30 mm. It is substantially wider than the user's roughly
4 mm Pupil ribbon reference. A narrower neck requires a new fan-out and
impedance design. The flat assembly remains 76 mm long, above the approximately
60 mm target. No mass estimate or demonstrated physical fit is claimed.

The connector footprint transcribes the manufacturer's mounting pattern:
0.30 × 0.80 mm signal lands, 0.40 × 0.80 mm mounting lands and
0.25 × 0.65 mm signal stencil openings. The 24-contact dimension row supplies
the mounting locations. Pin 1 follows the published mounting-pattern view.
The selected cable uses the bottom contact option; its exposed copper faces the
rigid boards' component sides. Nominal tip thickness is 0.30 ± 0.03 mm, with a
2.5 mm stiffener and 1.5 mm exposed contact length
[@hiroseFh34Drawing; @hiroseFh34Catalog].

The native flex uses a provisional 0.1 mm body envelope; that is **not** a selected
stackup. The tip stiffener is a drawing annotation. Tip corner rounding,
coverlay, adhesives, finishes, manufacturing tolerances and bend limits still
need explicit fabrication definitions. The head's solder-lap joint needs an
assembly process, access check and strain relief. Do not order this draft.

## Electrical correspondence

`interface.json` contains the full numbered pinout. J102 pin *n* connects through
flex contacts J301.*n* and J302.*n* to head land J201.*n*. The original 24-pin
assignment is retained: three MIPI pairs with adjacent ground contacts, sensor
supplies, I²C, reset and synchronization, plus reserved 3.3 V/LED control.
The local head oscillator supplies the sensor clock; no clock conductor is added.
The reserved LED conductors do not constitute an implemented LED driver.

`camera.kicad_sch` includes both attachment symbols and their footprint names.
`controller.kicad_pcb`, `head.kicad_pcb` and `flex-study.kicad_pcb` are separate
native boards. `assembly-interconnect-study.kicad_pcb` places those files in their
nominal assembled positions for inspection only. It is not a combined fabrication
board. The sensor head rotates in this assembly view; its native placement stays
unchanged.

## Checks and limits

`validation.json` records the saved file hashes and these checks:

- R04 parent hashes, all prior placements and all prior tracks are preserved.
- All 456 assigned rigid-board pads agree with the exported schematic netlist.
- All 24 flex conductors have continuous saved copper and the correct end nets.
- The rotated head lands align with the corresponding flex lands; connector
  contact rows agree with the flex pin order.
- Both rigid boards have no same-side footprint bounding-box collisions and
  retain at least 0.75 mm bounds clearance to their outlines.
- The schematic passes ERC with zero errors and warnings under the existing
  project checks; inherited ignored check categories are listed in `erc.rpt`.

DRC still reports six open camera escapes and 195 unconnected controller items,
93 unconnected head items, and eight separate ground connections on the flex.
The latter require a designed ground reference and bonding. No other DRC
violation types occur under the recorded draft rules. These are **not clean
fabrication DRC results**.

Flex traces are 0.15 mm-wide straight study copper, with equal 33.8 mm centerline
lengths. Whole-link skew, 100 Ω differential impedance, return paths and supply
voltage drop remain unverified. Do not infer electrical performance from equal
lengths [@esp32P4PcbLayout]. The flex's custom DRC rule permits terminal fingers
to reach the cut edge (−0.05 mm edge allowance for pads); other copper requires
0.25 mm edge clearance. All flex pads are terminal fingers. This is an explicit
geometry rule, not a supplier acceptance or an excluded error.

Next work is to choose compatible rigid/flex stackups and complete board routing,
including ground references and power distribution. Optics, illumination,
firmware capture and physical validation remain unfinished.

Review scope, 2026-10-27: Hirose public product specifications, drawing sheets
1/2/4 for dimensions and 5/6 for operation, and catalog features/specifications.
No supplier stock check, physical mating, soldering or signal-integrity test.
Original PDFs are not vendored into the public source tree.

## Reproduce

From the repository root, with KiCad 10 installed at the shown path:

```powershell
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/validate_r05.py
```

Success writes `validation.json`, the assembled study and SVG views. Full DRC
and ERC reports go to `generated/ov9281-r05-validation/`. To rebuild elsewhere,
run `build_r05.py --output NEW_DIRECTORY`, then
`validate_r05.py --directory NEW_DIRECTORY`. The output directory must not exist.
The validator checks against preserved R04 and rejects changed parent files.
