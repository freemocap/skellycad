# First working infrared camera

Current requirements and supplier disposition: [compact camera sourcing](compact-camera-sourcing.md). No stocked module satisfying all requirements has been verified. The stacked evaluation kit is not the wearable product.

Earlier acquisition candidate, now conditional on availability and final packaging: **Leopard Imaging
LI-OC0TC1B-MIPI plus a vendor-confirmed USB receiver and matching firmware**.
This uses the selected OC0TC already assembled into a camera module. Request
one complete working evaluation set, not a loose sensor and a generic adapter.
No order or supplier message has been sent.

## What is now established

The vendor lists the module at USD 99, on backorder. Its product page and V0.2
datasheet specify monochrome global shutter, 400 x 400 up to 240 fps, one-lane
MIPI D-PHY and an 8-100 mm focusing range. These are vendor claims, not our
measurements. The quoted price excludes the receiver, illumination and shipping.
The focus claim materially improves the case for retaining integrated optics
[@leopardOc0tcModule; @leopardOc0tcDatasheet].

The module connector is AXT624124, 24 contacts at 0.4 mm pitch. The host supplies
1.1 V and 2.8 V; control IO is 1.8 V. A transcription is in
`li-oc0tc1b-connector.csv`. This is the assembled module connector, NOT the
16-contact OC0TC component pinout or a PCB footprint. The listed 8-bit I2C address
0x6C corresponds to 7-bit address 0x36. Confirm connector mating part, orientation,
clock, sequencing and initialization against the delivered revision before wiring
[@leopardOc0tcDatasheet].

The published 2.3 mm focal length and 70-degree horizontal FOV warrant clarification:
400 pixels at 2.2 micrometres span 0.88 mm; a simple rectilinear model would give
about 22 degrees for 2.3 mm focal length. This calculation is a consistency check,
not a substitute optical prescription. Do not size a mount from that focal-length
field. Exact depth-of-field criteria and 940 nm filter transmission remain unverified.

## Build sequence

1. Obtain a matched camera, receiver, interconnect, firmware and Windows capture
   software from Leopard. Ask for a demonstration of 400 x 400 at 120 fps over
   USB, with manual exposure/gain. The sensor's 240 fps rating does not establish
   the USB system's delivered frame rate. Do not order a generic MIPI tester as
   a presumed compatible substitute.
2. Connect the supplied assembly by USB using the vendor instructions. Record a
   bench target first. Preserve the delivered firmware version and capture mode.
   The repository's `tools/electronics/record-camera.ps1` can enumerate and record
   a camera exposed through Windows DirectShow. A proprietary RAW/SDK-only device
   requires the supplier's capture program instead [@ffmpegDshow].
3. Check focus at the intended mount distances and field coverage under matched
   940 nm illumination. The actual application distances must come from the selected
   complete assembly. A provisional bench sweep at 10, 20, 30, 50, 80 and 100 mm
   characterizes the vendor claim; it does not select a species geometry.
   Validate visible rejection. Use a bench target before on-eye illumination;
   LED current, geometry and exposure assessment are still required.
4. Build our mount and illumination board around the working camera. Keep the
   evaluation USB receiver outside the small head initially. Then implement our
   compact USB board using the demonstrated receiver design and available design
   rights. Obtain schematic/firmware redistribution rights if an open design is
   required. A purchased camera module alone does not make its internals open.
5. Qualify the compact USB 2.0 mode and four-wire harness before replacing the
   evaluation cable with JST. USB 3.0 streaming cannot simply be wired through four
   contacts. The earlier R02 geometry remains a concept, not this vendor assembly.

## Shortlist and disposition

| Option | Useful fact | Decision |
| --- | --- | --- |
| LI-OC0TC1B-MIPI | Selected tiny OC0TC assembled; focus 8-100 mm | First supplier route; receiver/firmware confirmation and delivery quote needed |
| LI-OV7251M-FF | 6 x 6 mm mono global-shutter head; published 80-150 mm focus; vendor USB tester compatibility | Backup if working distance fits; NIR filter and exact kit remain to confirm [@leopardOv7251Head] |
| KLT-USB1A-OV7251 V1.0 IR940 | USB 2.0, 640 x 480, LEDs and advertised 940 nm filtering; 60 x 23.5 mm PCB | Larger bench fallback, not our tiny head; focus, frame rate, filter curve and LED control need confirmation [@kltOv7251Ir940] |
| Bare OG0TC1B | Retains freedom to choose lens and board | Custom sensor PCB, optics assembly, power/clock/control and receiver firmware work; defer until a working supported system exists [@omnivisionOg0tcBrief; @infineonCx3ApplicationNote] |

The KLT page also says "650nm IR Cut and 940nm IR Pass"; its wording is insufficient
to establish a purely NIR passband. Do not treat that listing as verified visible
suppression. Stock and delivery of that option were not established.

## Completion evidence

First hardware milestone: a recorded bench-target clip, documented resolution and
pixel format, measured received-frame timing, repeatable manual exposure, usable
focus over the intended distance range, and verified IR filtering. Neither a CAD
render nor a synthetically generated video meets this milestone.

Review scope: product-page specification excerpts and the extracted V0.2 datasheet
text were reviewed. Drawing dimensions and the graphical power timing diagram were
not transcribed or qualified. No new CAD geometry, electrical layout, purchase or
physical-camera test is claimed.
