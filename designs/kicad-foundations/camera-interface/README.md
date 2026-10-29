# Single-camera interface study

R01 is an editable logical schematic of the Raspberry Pi 4 15-pin camera
interface. J1 and J2 both use the **host pin convention**. Matching labels
connect their pins; this is not a verified camera-end connector or cable drawing.
The host pin table supplies two image-data pairs, a clock pair, module-dependent
control signals, I2C, ground and 3.3 V [@raspberryPiCameraPinout].

The candidate camera family is Arducam OV9281 with a supported Raspberry Pi
receiver. Its guide documents a software setup path, but its catalog links
contain inconsistent sensor descriptions. Exact SKU, cable and image mode
remain pending; this is not a purchasing specification [@arducamOv9281Guide].

## What to inspect

Open `electronics/r01/camera-interface.kicad_sch` in KiCad. The native project
includes an original local symbol library. `interface.json` records the pin map,
units and schematic hash. No footprint, sensor circuit, USB bridge or PCB has
been selected. No hardware/video test has been performed.

This study teaches the interface we will preserve while changing camera-head
geometry. A MIPI receiver and a USB video interface are separate design choices;
renaming connector pins cannot perform that conversion.

## Validation and rebuild

From the repository root, use Python 3 and KiCad 10 CLI. Generate into a new
directory with `python designs/kicad-foundations/camera-interface/build.py --output generated/kicad-foundations/camera-rebuild`.
The generator refuses to overwrite an existing directory.

Export the native schematic with `kicad-cli sch export netlist --format kicadxml --output generated/kicad-foundations/camera-r01/netlist.xml designs/kicad-foundations/camera-interface/electronics/r01/camera-interface.kicad_sch`.
Then run `python designs/kicad-foundations/camera-interface/validate.py generated/kicad-foundations/camera-r01/netlist.xml`.
Run `kicad-cli sch erc --exit-code-violations --output generated/kicad-foundations/camera-r01/erc.txt designs/kicad-foundations/camera-interface/electronics/r01/camera-interface.kicad_sch`.

R01 passed ERC with zero violations and the 12-net, 30-endpoint pin-map check
on 2026-10-27. Passive connector pins limit ERC: these checks do not establish
power compatibility, cable orientation, signal integrity or working video.
Resolve the exact module and cable before assigning footprints or routing.

## Evidence review

Reviewed the official host connector table and control-signal descriptions;
reviewed the Arducam overview, catalog and software setup excerpts. No module
schematic, physical cable or measured image stream was verified. The supplied
multi-head handoff informs the direction, not the electrical pin assignments.

## Selected bench reference — 2026-10-27

Use **Arducam B0224 + its bundled 150 mm 15-pin/1.0 mm to 22-pin/0.5 mm
cable + Raspberry Pi 4B** as the documentary bench reference. The vendor lists
NoIR monochrome global shutter operation and Pi 4 support. The module is
40 x 40 mm and its listed focus range starts at 30 cm; neither establishes
suitability for a compact close-up eye camera. Lens replacement descriptions
conflict, so do not assume interchangeability [@arducamB0224Selection].

The manufacturer table identifies a 22-contact top-contact module connector
[@arducamGlobalShutterQuickstart]. R01's J2 remains a **15-pin host-convention
boundary before the vendor cable**, not the module connector. Do not assign a
22-pin footprint to the existing 15-pin symbol. A future adapter may retain
that vendor cable, but still needs connector contact-side and cable mapping
validation. No footprint or fabrication release is made here.

The vendor lists 1280 x 800 at 143 fps in RAW8 and 114 fps in RAW10. Thus our
approximately 120 fps goal must specify bit depth and an actually supported
mode; it is not a blanket capability of every configuration
[@arducamB0224Selection]. These are advertised limits, not measurements.

When the hardware is available, first use the stock cable directly, before
inserting a custom PCB. Follow the vendor setup guide for the exact revision
and OS. On that configured Pi, run `rpicam-hello --list-cameras` and save the
reported modes [@raspberryPiCameraSoftware]. Then measure captured frame timing
and dropped frames in the chosen mode. Hardware availability, delivered mode,
close-focus optics and cable continuity remain unverified. No purchase made.

This selection refines the earlier generic candidate; it does not revise R01
or its recorded hash. Review scope: product specification/package excerpts,
manufacturer quick-start table and official mode-listing documentation.

## R02 digital walkthrough delivered

The course checklist now tracks completed digital teaching artifacts instead
of conflating lessons with future hardware acceptance. Its four deliverables
are architecture, KiCad electronics, FreeCAD integration, and product-direction
study. All four have artifacts. This does not mark the original physical camera,
manufacturing or multi-head product acceptance milestones complete.

R02 adds a 30 x 34 mm routed teaching coupon, Molex 200528-0150 footprints,
a bottom ground plane, eight ground vias and four mounting holes
[@molex200528Series; @kicadFootprintsSource]. The footprint is a layout candidate;
no cable interoperability or impedance claim is made. The unchanged copied
library file has attribution and a hash under electronics/r02.

The digital checks include ERC, DRC with schematic parity, independent pin and
route inspection, FreeCAD solid validity, and board/envelope-to-tray intersection
checks. The FreeCAD assembly imports the actual KiCad board-only STEP and adds
explicit approximate connector/cable envelopes. No eye-camera reference
geometry or selected species checkpoint was changed.

Native files: electronics/r02/camera-interface.kicad_sch and .kicad_pcb;
mechanical/r02/camera-interface-assembly.FCStd and .step. Example layer/drill
exports and reports are in electronics/r02/verification and manufacturing-demo.
The PCB is explicitly marked NOT FOR FAB. Physical cable mapping, stackup,
impedance, video, optics, fastening and printed fit remain unverified.

To rebuild, run build_board.py with KiCad's bundled Python and --output NEW_DIR.
Export a board-only STEP using KiCad CLI with --user-origin 50x50mm, then run
build_mechanical.py with the pinned FreeCAD bundled Python, --board-step STEP_FILE
and --output NEW_DIR. Both builders refuse an existing output directory.
The generator uses the installed KiCad library; compare the recorded footprint
hash before treating a rebuild as the same revision. Run validate.py against
an exported XML netlist and validate_board.py with KiCad Python against the PCB.
