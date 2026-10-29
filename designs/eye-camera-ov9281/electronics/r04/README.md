# R04 controller placement and routing study

Start with the [whole-camera overview](overview.html) for project status.
Open [layout-review.html](layout-review.html) for the detailed before/after view, or
`controller.kicad_pcb` in KiCad PCB Editor. `assembly-routing-study.kicad_pcb`
shows both boards at the same scale. This revision demonstrates partial copper
routing within the 32 × 20 mm controller outline. It is not a fabrication release.

## Changes from R03

The P4 rotates 180 degrees. USB leaves toward the upper-left connector;
camera lanes leave toward a reserved corridor across the top and the right-edge
flex budget. The 12 × 4 mm connector reservation rotates to 4 × 12 mm; it is
still a space budget, not a chosen connector. The sensor head remains the exact
R03 14 × 14 mm board. The combined view's 30 mm strip remains illustrative.

Sixteen designated P4 decouplers now sit on the back near their corresponding
front-side power pins. Their median XY pad-centre separation falls from
13.33 mm to 0.13 mm. This is a placement metric, not a routed electrical length:
the via locations and ground returns still need design. The flash moves toward
the flash-pin bank. Sensor supplies and control translation form local groups.

The two buck converters have adjacent inductors, input/output capacitors and
feedback resistors. Added copper includes switch-to-inductor, input/output and
feedback connections. Supply distribution and ground returns remain incomplete.
These placement choices follow the reviewed regulator layout guidance
[@tiTlv62569].

Twenty-two pad-to-pad copper paths cover the USB signal chain, local buck
connections, and crystal with its load capacitors. Six additional 1 mm CSI
escapes show the camera pins leaving the P4; their open ends are intentional
study endpoints, not final stubs. The copper is saved as native KiCad tracks.

The crystal remains on the front, away from the inductors. The P4 guide calls
for a continuous ground reference, separated crystal placement and controlled
differential routing. Those requirements guide this study; they are not all
implemented yet [@esp32P4PcbLayout].

## What the checks establish

`validation.json` records 99 footprints across the two boards, 408 pad-net
checks against the original netlist, component bounds within the outlines,
and no same-side bounding-box overlaps. Each of the 22 requested pad-to-pad
paths is checked through the saved copper endpoint graph. The schematic is
byte-identical to R03 and passes ERC with zero errors and warnings.

Controller DRC reports six dangling camera escapes and the remaining unrouted
connections. It reports no other violation types under the candidate R04 rules.
The head remains unrouted. No DRC exclusions suppress these findings.
The complete report is in `generated/ov9281-r04-validation/` from the repository root.

R04 explicitly changes default clearance from 0.20 to 0.15 mm and sets a
0.15 mm minimum track width. This permits the P4 footprint's 0.15 mm pad gaps;
it is a candidate process rule, not a manufacturer approval. Published JLCPCB
capabilities list 0.15 mm SMD pad spacing and finer multilayer trace spacing,
but also list a 0.25 × 0.25 mm minimum SMD pad. The P4's 0.20 mm-wide pads
therefore still require process review. Stackup, surface finish, mask and
assembly capability are not qualified [@jlcThinPcbCapabilities].

The USB paths are obstacle-checked trial copper, not a final differential pair.
They require redrawing/tuning together once the stackup is chosen. Measured
copper lengths and mismatch appear in `validation.json`; they exclude package
and resistor delay. USB and MIPI impedance targets remain 90 Ω and 100 Ω,
respectively, with the tolerances specified by Espressif. This study does not
calculate or demonstrate either impedance [@esp32P4PcbLayout].

## Remaining before a complete PCB

Design the decoupling vias, continuous reference planes and power distribution;
complete flash and control routing; select the flex interface and finish the
camera pairs. Recheck power sequencing, load/inrush, thermal paths and component
part numbers. Select and mechanically validate the close-focus NIR optics and
illumination components. No firmware or physical image-capture test was performed.

The controller has 15 front and 61 back footprints. The assembly remains larger
than the original approximately 60 mm flattened target. No enclosure fit or
completed FreeCAD assembly is claimed.

## Lineage and reproducibility

R03 is preserved. `routing-study.json` records parent hashes, positions,
pad-distance comparisons and every trial route. `validation.json` records
the resulting native file hashes. The copied schematic, head and libraries
retain their existing provenance and license notices. Author/license text on
controller footprints moves to the comments layer for readable plots;
attribution remains in the native file and library.

Review scope, 2026-10-27: R03 native boards and netlist; Espressif power,
crystal, USB and MIPI layout sections; TI TLV62569 section 10; JLCPCB thickness,
pad/trace and hole capability entries. No supplier quote or assembly approval.

From the repository root, use KiCad's Python to validate the saved revision:

```powershell
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/validate_r04.py
```

Success updates the report and SVG views. The six expected dangling ends remain
reported. To rebuild, run `build_r04.py --output NEW_DIRECTORY` with the same
Python; the output directory must not exist. Do not overwrite an open board.
