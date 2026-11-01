# R03 physical placement draft

Open `assembly-placement.kicad_pcb` in KiCad PCB Editor, or view
[the rendered overview](preview.html). This revision places 99 footprints on
two boards. It is an unrouted space study, not a manufacturing release.

| Part | Outline | Front / back footprints |
| --- | --- | --- |
| Controller | 32 × 20 mm | 6 / 70 |
| Sensor head | 14 × 14 mm | 1 / 22 |
| Illustrative flex gap | 30 mm | No flex copper or connector selected |

Both boards use a provisional 0.6 mm thickness and four copper layers. These
are design assumptions, not a fabricator-approved stackup. The flattened length
is 76 mm; this draft does not yet achieve the approximately 60 mm product goal.
The head grew from an initial 14 × 12 mm envelope to preserve edge space.

## What is real and what is reserved

The pads and component outlines come from the R02 circuit and its local
libraries. The OV9281 reference footprint comes from Antmicro; the P4 footprint
comes from Espressif; standard parts use KiCad libraries
[@antmicroOv9281Board; @espressifKicadLibrary; @kicadFootprintsSource].
Their license notices are preserved alongside the local libraries.

The head holds the sensor on the front and its oscillator, bias components
and capacitors on the back. The controller holds the P4, flash, power supplies,
USB protection and candidate JST connector. J103 is five programming pads.
The provisional 10/22 µF capacitors use 0805 footprints and 1/4.7 µF parts use
0603 where recorded in `placement.json`; actual part numbers and capacitance
under voltage remain unqualified.

Outlined regions reserve an 8 × 8 mm lens budget, two emitter areas, a flex
tail and a controller flex connector. These are chosen space budgets, not
selected optical or connector parts. J102 and J104 remain schematic-only
interfaces and are excluded from placement. No LED current driver is added.
The drawn flex strip is an illustration, not a designed flexible PCB.

The combined file has two separate board outlines for review. Use the separate
`controller.kicad_pcb` and `head.kicad_pcb` for subsequent board work; the combined
file is not a fabrication panel. Back-side SVG geometry is shown through the
board from the front, without mirroring.

## Validation and remaining work

`validation.json` records 99 footprints, 408 checked pad-net assignments,
zero same-side bounding-box overlaps, and all footprint geometry inside the
outlines with the selected margin. R03 schematic ERC reports zero errors and
warnings. Source schematic hashes and final file hashes establish lineage.
R02 remains preserved.

The controller DRC reports 103 clearance violations within the P4 footprint:
its smallest pad gaps are 0.15 mm, below the current 0.20 mm default rule.
No clearance rules were weakened. Qualify the fabrication process and P4
escape routing before setting final rules. The controller has 193 unconnected
items and the head has 71; neither board has copper traces. The head has no
other reported DRC violations.

This placement checks available area. Passive components still need regrouping
around the pins they serve, with decoupling, power-loop and signal-routing
constraints. It does not demonstrate routing feasibility, physical assembly
fit, lens focus, IR performance, heat, mass or working USB video.

Next, qualify the P4 escape and power placement, select the flex interface and
optics, and refine the board envelopes before routing and FreeCAD enclosure
work. Review scope for R03: local R02 netlist, vendored footprints, native board
geometry, ERC and DRC outputs; no new vendor specification review.

From the repository root, validate with the installed KiCad Python:

```powershell
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/validate_placement.py
```

Success updates `validation.json` and SVG previews; DRC limitations remain
reported rather than waived. To regenerate, run `build_placement.py --output`
with a new directory using the same Python. Never overwrite an open PCB file.
