# OV9281 infrared eye camera

**Current working candidate: [R11 C SLIM.flex](WORKING-REVIEW.md).**
The approved nine-item offline session produced one routed circuit, matched
FreeCAD assembly, compiled bring-up firmware, mass ledger and purchasing BOM.
Open [the rendered review](electronics/r11/index.html) for actual native views.

The controller is 28 × 14 mm, the head 14 × 14 mm and the integrated free flex
32.85 × 8 mm. Nominal module mass is **1.34 g excluding the external tether**;
the under-one-gram target is not met. No functional camera has been demonstrated.

Native spacing/connectivity and offline assembly checks pass. Sensor DVDD stress
margin, supply-chain qualification, real close-focus IR optics, fabrication,
thermal behavior and hardware operation remain open. The [test plan](electronics/r11/PROTOTYPE-TESTS.md)
separates remaining design gates from eventual bench tests. The [global roadmap](ROADMAP.md)
is broader than this completed session.

R08 remains the selected historical electrical baseline. R10, the C packaging
study and the complete Pupil reference are preserved. `working-review.json`
identifies R11 as the latest checked working candidate, not an accepted release.

## Earlier design rationale

The following notes preserve earlier architecture decisions and research context.
Historical revision descriptions and preliminary dimensions below are superseded
by the current R11 records where they differ.

## Camera to build

Adjustable close-focus lens and NIR filter -> OV9281 head with IR LEDs ->
approximately 30 mm flex -> one thin USB controller board -> four-contact JST ->
external USB hub and computer.

The sensor is monochrome, global shutter, with two-lane MIPI CSI-2 and RAW8/RAW10
output. Its published full-resolution rate is 1280 x 800 at 120 fps; that is a
sensor capability, not the promised USB rate [@omnivisionOv9281Brief].

Use the supplied Pupil handoff as a physical reference: approximately 30 x 9 mm
controller, 30 x 4 mm flex, 10 x 6 mm head, and 0.7 g assembly. These are the
user's reported measurements, not manufacturer tolerances or our predicted mass.
Source: user attachment `83c93e3c-61a5-4c68-a1f4-e200a1bd08ac/Pasted text.txt`,
"Multi-head eye camera board: design handoff", dated 2026-10-27.
Pupil publishes 400 x 400 at 120 fps and 192 x 192 at 200 fps for its global-shutter
eye camera [@pupilCore200Hz]. Its sensor and circuit have not been identified.

The existing [complete Pupil mock-up](../eye-tracker/shared/cameras/pupil-core-eye/README.md)
remains checkpoint CAMERA-DUMMY-R08. Its 6.3 mm holder and 0.25 mm substrate are
model geometry, not qualified parts or a camera PCB stackup. No geometry changed.

## Electrical partition

| Assembly | Contents and interfaces | Design status |
| --- | --- | --- |
| Sensor head | OV9281, local decoupling, required sensor bias network, close-focus optics, two provisional LED locations | Adapt one sensor channel from Antmicro; head outline must accommodate actual lens and routing |
| Short flex | MIPI clock pair and two data pairs, control bus, power, grounds, reset and reserved LED connections; oscillator stays on head | R05 defines 24-pin mapping, controller connector and head solder lands; impedance stackup and whole-link skew unqualified |
| USB board | Receiver, firmware storage/memory as needed, sensor supplies, USB protection, LED current control, programming pads | ESP32-P4 selected for the first implementation; exact variant and supporting BOM pending |
| External connector | USB VBUS, D-, D+, GND | Candidate JST SH: 1 VBUS, 2 D-, 3 D+, 4 GND; cable construction and compatibility unverified |

Antmicro provides a complete dual-sensor KiCad design under Apache-2.0. Reuse one
sensor channel and its reviewed symbol/footprint basis, preserving attribution;
do not retain the second sensor, M12 mounting layout or 50-pin host connector
merely because the reference uses them [@antmicroOv9281Board; @antmicroOv9281License].
The published schematic includes 1.2 V, 1.8 V and 2.8 V supplies, 24 MHz clocks
and sensor bias/decoupling circuitry [@antmicroOv9281Schematic]. Supply sequencing,
component selection, unused pins and routing need checking during adaptation.

Put the receiver and most power circuitry on the controller board. Keep required
local capacitors at the sensor. Board thickness target is 0.4-0.6 mm, subject to
fabricator approval of the actual multilayer stackup [@jlcThinPcbCapabilities].
ESP32-P4 has a 10 x 10 mm package, so the 9 mm-wide Pupil board is not a viable
outline. User accepts a wider board. Final width follows component placement
and routing [@esp32P4Datasheet].

## Optics and infrared

The [compact lens comparison](mechanics/compact-optics.md) reconnects this design
to the earlier Pupil reconstruction. CH2021A is the preferred next mechanical
study candidate; close-focus and 940 nm performance remain unverified. The
[supplied CIL829 model](mechanics/optics-r01/README.md) is retained as an oversized
reference rather than the target lens envelope.

Target focus adjustment across 10-20 mm from the front optical surface, with
940 nm illumination and visible suppression. A narrow 940 nm filter is an option
within the requested 800-1000 nm region, not a requirement to pass that entire
band. Select the filter together with the LED wavelength and lens.

OV9281's published image area is 3.896 x 2.453 mm, approximately 4.60 mm diagonal
[@omnivisionOv9281Brief]. For full-array coverage, select a lens whose image circle
covers that area. A smaller thread is acceptable only if its actual optics and
back-focus clearance work. Do not carry over the Pupil M5-looking holder by
appearance. Use a purchased NIR-capable threaded lens and adjustable holder;
exact thread, focal length, aperture and part number remain open. Cropping changes
field of view and must be considered when choosing the lens.

Provide controlled LED current and default-off enable. Current, duty cycle and
permitted eye exposure remain unset until optical output and geometry are
evaluated. Initial imaging tests use a target, not an eye. Measure focus at
10, 15 and 20 mm under the selected IR illumination before fixing the holder.

## USB and firmware feasibility

Espressif's Apache-2.0 OV9281 driver includes a 640 x 400 RAW8, 100 fps mode with
24 MHz input clock [@espressifOv9281Driver]. Its ESP32-P4 UVC example captures
camera data, encodes JPEG/H.264 and sends video to a PC. The documented example
uses other sensors; it does not establish OV9281 monochrome operation at our
target rate [@espressifVideoUvc]. Check RAW8 handling, the driver's Bayer metadata,
ISP bypass/conversion, buffering, USB transfer mode and host controls together.
The driver alone is not proof of an end-to-end open dependency chain; review
licenses for the selected build, including USB and any codec dependencies.

First integration mode: the existing 640 x 400 at 100 fps configuration.
Product target remains approximately 400 x 400 at 120 fps, requiring a validated
sensor crop/timing mode and transport. UVC is preferred for convenient capture,
but the user's handoff permits a documented host API instead.

Derived uncompressed 8-bit image payloads, excluding all transport overhead:

| Mode | Payload |
| --- | --- |
| 1280 x 800 at 120 fps | 122.88 MB/s: exceeds USB 2.0's 60 MB/s signaling ceiling |
| 640 x 400 at 100 fps | 25.60 MB/s: requires an actual transfer/buffering test |
| 400 x 400 at 120 fps | 19.20 MB/s: target, not measured throughput |

Do not assume fitting below the signaling ceiling guarantees a USB mode. UVC
format support, endpoint limits and conversion can increase required bandwidth.
Prefer preserving grayscale detail for pupil tracking; qualify any compression.

## Source handling

The Vision Tech-hosted OV9281 datasheet is useful technical background, but its
front matter marks it proprietary and restricts redistribution. It is linked,
not copied into this public repository [@ov9281DatasheetMirror]. Its presence on
a public URL is not an open-source license. Use Antmicro's expressly licensed
hardware and Espressif's expressly licensed driver as the reuse starting points.
Do not claim that their licenses cover OMNIVISION's separate document.

## Current implementation and completion criteria

The native schematic, split boards, routing records, component inventory,
compiled snapshot firmware and host recording implementation are saved. Run
`python designs/eye-camera-ov9281/verify_offline.py` after both firmware builds to
check selected file hashes, board/firmware pin assignments, build hashes, the
address/reset contract and host protocol tests. The report also identifies
unresolved engineering work; a successful check does not authorize fabrication.

The remaining computer work includes completing routing, resolving the Y1
oscillator voltage/footprint conflict, reviewing power sequencing, finishing
illumination, selecting and modeling real optics, and qualifying interface
constraints. Actual capture, focus, optical exposure, USB rate, thermal behavior
and physical fit then require hardware. See [STATUS.md](STATUS.md) for the full
release criteria. No hardware purchase, flash or fabrication occurred.

## First implementation: OV9281 + ESP32-P4 (R01 history)

The user selected ESP32-P4 on 2026-10-27 as the first implementation controller.
Continue with it unless an actual integration failure requires reconsideration.
It combines MIPI input, processing, high-speed USB and in-package PSRAM
[@esp32P4Datasheet]. External flash, a crystal, core DC-DC conversion and supporting
passives remain necessary. Use the manufacturer's revision-v3.0-or-later circuit
basis; the current guide distinguishes pin 54 and power/USB circuitry from older
revisions [@esp32P4HardwareGuide]. This is a revision selection criterion, not a
verified purchasable order code. Sensor rails, USB protection, LED drive and
control-voltage compatibility also remain part of our board.

Open [the native head draft](electronics/r01/ov9281-head.kicad_sch).
The original licensed KiCad schematic and PCB are preserved under
`reference/antmicro/`, with commit and SHA-256 provenance. R01 retains the source
coordinates and component references to make comparison straightforward.
It contains one sensor channel, its three supply filters, three regulators and
24 MHz oscillator. The location of these components on head versus controller
is not yet assigned; the file is an electrical draft, not a placement drawing.

The generator `extract_head.py` refuses to overwrite its output revision. KiCad
10.0.7 successfully exported its netlist and SVG. Comparison against the original
netlist found identical connectivity among retained component pins. ERC reports
2 errors (undriven supplies) and 104 warnings, including external-library links;
these are unresolved, not waived. See `electronics/r01/validation.json`.
No P4 schematic, flex connector, LED circuit or custom PCB layout is completed.
R02 resolves local libraries and adds receiver/interface circuitry; see the current draft above.
