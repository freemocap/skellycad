# Camera replacement feasibility

Research date: 2026-10-10. Scope: alternatives to the user's Pupil Labs eye camera for a tethered eye tracker, initially emphasizing rat/marmoset prototypes. This is a purchasing and engineering exploration, not a validated replacement design. USD listings exclude tax, shipping, and integration. No purchases, supplier messages, or geometry changes were made.

## Assessment

Cheaper eye-imaging hardware is feasible. A compact, flexible, infrared-sensitive global-shutter camera is also feasible. The unproven combination is close-focus optics, illumination, a light and compliant tether, reliable acquisition, and total mounted mass at a substantially lower system cost.

My preferred direction is a monochrome OV9281 camera with a separate sensor head and USB controller. A rigid USB board is useful for an optical bench comparison. A small MIPI head is promising for miniaturization but makes the connection to the computer a separate engineering project. Do not start with a bare image sensor or assume that a Raspberry Pi ribbon can replace the existing tether.

## Workbench orientation

The workspace is a reproducible FreeCAD workbench: Python builders and explicit parameters under `designs/`, disposable output under `generated/`, and a pinned FreeCAD 1.1.4 runtime in `tools/cad/toolchain.json`. The introductory course is preserved in `designs/cad-foundations/`; its README identifies `replay.py` as the safe fresh-build entry point.

Real-part work is already substantial: the mouse-hat assembly was reconstructed into editable parts and developed through printed revisions. The latest handoff and `rear-arm-r11/selection.json` select R11B. Older root/project README statements describe earlier phases and are not the latest design status.

The local `functional-map.md` describes the PCB tray, protective cap, separate adjustable sensor holder, retention clip, ribbon path, and skull baseplate. It records a user-reported assembly mass below 4 g, with the included components unspecified. This is not a camera-only mass or an established species-specific mass limit. Replacement work would chiefly affect the tray/cap, sensor seat/clip, LED arrangement, ribbon routing, and strain relief. It need not begin with redesigning the baseplate.

## Baseline and unknowns

The user describes an approximately $700 Pupil camera, integrated IR LEDs, a flexible sensor neck, and a four-conductor tether to an overhead receiver. Treat $700 as the user's baseline; this research did not establish a current standalone replacement-camera quote or the exact installed revision.

Pupil's published 200 Hz camera modes are 192 × 192 at 200 fps and 400 × 400 at 120 fps, with global shutter. These are reference modes, not confirmation of the user's actual acquisition settings. [Pupil camera announcement](https://pupil-labs.com/blog/200-frames-per-second).

Pupil support identifies Core camera connectors as JST SH, 1.0 mm pitch. This likely resolves the spoken “JWST,” but does not verify the installed harness or pinout. The remote box may be a USB hub/adapter rather than the first conversion to USB; identify it before reusing it. [Pupil support, January 2025](https://chat-archive.pupil-labs.com/logs/core/2025/01/).

A Core support answer identifies an 850 nm eye-camera filter. That is evidence for starting an 850 nm comparison, not proof of this camera's exact LED spectrum/filter. [Pupil support, April 2022](https://chat-archive.pupil-labs.com/logs/core/2022/04/).

User clarification during research: current acquisition is approximately 120 fps; the recalled IR range is 800–1000 nm; and the sensor-to-PCB ribbon is approximately 30 mm long. The user considers that ribbon longer than desirable and believes a shorter one could improve camera placement. This is distinct from the long electrical tether to the computer, whose length remains unknown. The 120 fps global-shutter candidates therefore match the nominal current rate, subject to actual output format and exposure.

Still needed: actual resolution/exposure; lens-to-eye distance in mm; required field of view; long tether length in m; exact IR spectrum; existing module and complete headgear mass in g; receiver identity; and whether the analysis uses pupil diameter, pupil center, corneal reflections, or a calibrated 3D gaze model.

The R06 notes explicitly describe ribbon spring clearance and the later arm studies preserve room for the loop. A shorter custom flex is therefore a meaningful mechanical requirement. Request sensor-to-controller separation and flex length independently of total module length. Choose the shortest route that retains adjustment travel, specified bend radius and strain relief; the minimum straight-line distance is not sufficient. Integral camera flex cannot simply be cut shorter. No numeric replacement length is selected without endpoint geometry and motion measurements.

## Candidate comparison

Published dimensions below describe different components; do not compare a sensor package with an entire USB camera as if they were equivalent. Unknown mass remains unknown.

| Candidate | Published price and size | Imaging/interface | Fit for this project |
| --- | --- | --- | --- |
| Arducam B0332 OV9281 USB | $49.99; 38 × 38 mm board; module mass not established | Mono global shutter, no IR-cut filter, USB 2.0 UVC. Current page: 1280 × 800 MJPEG at 100 fps; full-size YUY2 only 10 fps | Convenient bench reference; bulky at the eye. Stock focus is 1 m–infinity and lens replacement requires vendor discussion. Close-focus configuration is a purchase condition. |
| Leopard LI-OV9281-MIPI-RS-85H | $59; 8 × 8 mm head; datasheet module weight approximately 0.3 g | Mono global shutter, 850 nm bandpass, 1280 × 800 at 120 fps; two-lane MIPI CSI-2 | Strong miniature-head lead. Lens is glued, specified 22 cm–infinity. Needs factory close focus, separate LEDs, matched interface and tether. |
| Shenzhen CM flexible OV9281 USB listing | Quote required; controller 25 × 18 mm; lens-plus-flex envelope 70 × 10 mm; mass unknown | Supplier advertises flexible USB/global-shutter architecture and 120 fps | Closest architectural lead. Exact fps/format, IR filtering, close focus, current availability and electrical details are unverified. |
| Arducam OV5647 miniature B0066 family | Base listing $29.99; 300 mm flex. NoIR variant price needs confirmation | Color, rolling shutter; Raspberry Pi camera interface | Cheap packaging experiment. Select explicit NoIR SKU; standard B0066 has an IR filter. Lower priority for rapid eye motion and precision pupil edges. |
| OMNIVISION OVM7251 CameraCubeChip | Quote required; package 3.96 × 3.46 × 3.34 mm, excluding PCB/LEDs/bridge | Mono global shutter, VGA at 120 fps; 850 or 940 nm versions; MIPI/LVDS | Plausible custom tiny camera; component-level development rather than a ready USB camera. |

Sources: [Arducam B0332](https://www.arducam.com/arducam-120fps-global-shutter-usb-camera-board-1mp-720p-ov9281-uvc-webcam-module-with-low-distortion-m12-lens-without-microphones-for-computer-laptop-android-device-and-raspberry-pi.html), [Leopard product](https://leopardimaging.com/product/robotics-cameras/cis-2-mipi-modules/mobile-modules/li-ov9281-mipi/li-ov9281-mipi-rs-85h/), [Leopard datasheet](https://leopardimaging.com/wp-content/uploads/2025/10/LI-OV9281-MIPI-RS-85H_Datasheet.pdf), [CM manufacturer listing](https://www.camera-module.com/product/globalshuttercameramodule/120fps-monochrome-global-shutter-usb-camera-ov9281.html), [B0066 family](https://www.arducam.com/arducam-raspberry-pi-5mp-spy-camera-b0066.html), [OVM7251](https://www.ovt.com/products/ovm7251/).

Source limitations: CM information was available through the indexed manufacturer page; direct fetch failed twice. Treat it as an RFQ lead, not a purchase-ready choice. Arducam B0332's URL says 120 fps but its current title/specification says 100 fps; this note uses the current specification. Leopard's product prose mentions Jetson compatibility while its platform table only checks USB3.0; request the exact supported board, adapter and firmware.

Arducam's $25.99 B0411 OV9281 is a useful counterexample: its 25 × 24 mm board has a 650 nm IR-cut filter despite NIR sensor marketing. A monochrome sensor does not guarantee an IR-ready assembled camera. [B0411 specification](https://www.arducam.com/blog/product/mini-ov9281-mono-global-shutter-for-pi/).

OMNIVISION also lists OVM6211, a 3.23 × 3.23 mm lens/sensor package, 400 × 400 at 120 fps, with MIPI output. This demonstrates that tiny eye-tracking components exist; it does not identify the Pupil sensor or supply a finished replacement. [OVM6211](https://www.ovt.com/products/ovm6211/). Avoid basing a new design on OV7251 without checking lifecycle: its sensor page currently says end-of-life; OVM7251 is a separate module listing whose supply must be confirmed. [OV7251](https://www.ovt.com/products/ov7251/).

## The tether determines the architecture

Conceptual alternatives, not wiring diagrams:

```text
A. Small USB camera
   eye head + LEDs -- short flex -- USB controller on carrier
                                  -- compliant USB tether -- PC/hub

B. Remote MIPI interface
   eye head + LEDs -- qualified MIPI harness -- overhead interface -- USB -- PC

C. Serialized camera link
   eye head -- short flex -- serializer + power on carrier
                            -- coax -- overhead deserializer/host -- PC
```

A best resembles the described current arrangement, provided the controller is light enough and the selected video mode works over the intended USB tether. A four-pin connector alone establishes neither protocol nor pinout. A USB 3 interface also cannot retain its SuperSpeed connection through only the usual four USB 2 conductors.

B moves mass off the head, but MIPI is not USB: the Leopard head exposes 25 contacts, differential data/clock, control, and multiple supply rails. Its stock flex is not evidence that a meter-scale freely moving harness will work. Require vendor-qualified length, bend behavior and adapters. [Leopard datasheet](https://leopardimaging.com/wp-content/uploads/2025/10/LI-OV9281-MIPI-RS-85H_Datasheet.pdf).

C is technically plausible for a thin long link. TI V3Link transports image data and control over coax or suitable twisted pair, with power-over-coax support in relevant designs. It requires electronics at both ends and a receiver/host path; it is not a passive ribbon-to-USB cable. My assessment is that it adds too much initial integration effort unless the tether becomes the limiting constraint. [TI V3Link](https://www.ti.com/product-category/interface/high-speed-serdes/v3link-serdes/overview.html), [TSER953 datasheet](https://www.ti.com/lit/ds/symlink/tser953.pdf).

## Optical and acquisition feasibility

Engineering requirements inferred from the application:

- Prioritize sharp pupil boundaries at the real working distance, stable exposure, and appropriate time resolution over megapixel count. Global shutter is the preferred starting point for rapid eye/head motion. A higher-resolution 100/120 fps camera does not reproduce 200 fps temporal sampling.
- IR sensitivity, spectral filtering, and illumination are separate requirements. NoIR removes an IR blocker; an 850 nm bandpass selects a spectral band. A 940 nm LED should not be paired with an 850 nm-only optical path without transmission data. Compare 850/940 nm using measured pupil contrast at the intended exposure and illumination, not the word “infrared” in a title.
- Add one or more small IR LEDs near the lens on a separate tiny board or custom flex, with a current-controlled drive and a deliberate reflection geometry. Integration includes power, heat, wiring and mounting. Establish optical exposure limits for the actual geometry; no safe current or species suitability is inferred here.
- Test MJPEG pupil-edge bias against uncompressed imagery, manual exposure/gain behavior, dropped frames, timestamps and synchronization. “UVC” establishes an acquisition interface, not compatibility with every Pupil software feature or calibrated gaze model.
- Measure head-mounted mass and tether pull separately. A light camera with a stiff cable can be mechanically worse than a heavier camera with a compliant tether. Larger animals broaden the possible design space but do not establish an acceptable load by themselves.

## Costs and what to build first

The approximately $30–$60 figures above buy camera hardware, not complete eye trackers. They omit illumination, close-focus optics, filters when absent, interface boards, custom cable, mounting, software integration and engineering time. Relative to the user's $700 reference, those component prices are roughly 12–23 times lower, but that ratio is not system savings.

Interface hardware can dominate a prototype: Leopard lists a different CSLINK/I-PEX USB tester at $299 and approximately 10 g. Its connector differs from the 25-pin head above; **this is an interface cost/mass example, not a compatible shopping bundle**. Obtain a matched quote. [Tester listing](https://leopardimaging.com/product/automation-cameras/usb-3-0-cameras/usb-3-0-i-pex-mipi-cameras/li-usb30-cslink-ipx-tester-2/).

Planning allowances, my estimates rather than vendor quotes: $100–$250 for a USB optical bench experiment with suitable optics, LEDs, cabling and a simple mount; $300–$700 for a miniature MIPI evaluation path with a matched bridge and optical changes. Both exclude labor, existing computer, shipping and tax; customization could exceed these allowances. A bespoke rigid-flex/USB design needs an NRE and minimum-order quote before claiming savings at small quantities.

Recommended sequence:

1. Record the present camera modes, optics distance, module/assembly mass and tether properties. Retain the Pupil setup as the comparison reference.
2. Get exact close-focus, IR and video-format specifications for a USB OV9281 sample. In parallel as a research direction, request a matched Leopard head/interface quote and a flexible USB module quote; no supplier messages have been sent.
3. Bench-compare at the same working distance and target frame rate. Measure focus across the eye region, pupil/glint contrast, blur, timing, dropped frames and temperature. Run the existing analysis pipeline against recordings.
4. Only after the optical and acquisition result passes, build a rat/marmoset-sized carrier variant with replaceable sensor and PCB seats. Keep measured mass and cable force as acceptance criteria. Revisit mouse packaging after those measurements.

## Supplier questions ready to use

Request the exact module revision, sample price, stock/lead time, MOQ and lifecycle; uncompressed and compressed fps at required ROI; manual exposure/gain and trigger support; 850/940 nm response and filter transmission; factory focus at the measured distance in mm; full 3D envelope and mass including flex; LED integration options; connector/pinout and approved cable length; and the complete PC interface BOM with supported OS/SDK/UVC modes. Ask separately for one-off sample costs and recurring costs at realistic quantities.

## Change note

Added this sourced feasibility note only. Preserved R11B and all CAD geometry. No physical imaging, electrical, mass, fit or animal-use tests were performed. Research conducted in this chat without delegation, consistent with workspace instructions.
