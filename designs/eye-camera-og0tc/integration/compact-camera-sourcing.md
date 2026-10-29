# Compact infrared camera: sourcing disposition

The wearable product is a tiny optical head on short flex, a miniature snap
connector, one thin USB controller board, and four-contact JST USB 2.0 output.
The required working distance is 10-20 mm. Monochrome, global shutter and
visible-cut/NIR-pass optics remain required. Nearby IR LEDs require a driver.
No stacked evaluation boards or long evaluation flex are the final packaging.

## Search result, 2026-10-27

**No in-stock, fully qualified combination has been verified.** Do not replace
that finding with a claim that any generic MIPI adapter will work.

| Candidate | Evidence | Disposition |
| --- | --- | --- |
| Leopard LI-OC0TC1B-MIPI | Vendor claims 8-100 mm focus, mono global shutter; backorder [@leopardOc0tcModule; @leopardOc0tcDatasheet] | Best documented focus-range candidate, but no dated delivery or USB pairing; not selected for purchase |
| Appleye AE-CCM-GS-MIRA016-M-74-WLO | Vendor application page claims 940 nm bandpass, mono global shutter and 16-36 mm focus [@appleyeMira016Eye] | Covers only 16-20 mm of our range; 10 mm requires another factory optical option. Quote required; not in-stock evidence |
| Leopard LI-OV7251M-FF | 6 x 6 mm head, 80-150 mm focus [@leopardOv7251Head] | Reject stock optics for 10-20 mm use |

Appleye's application page gives 2.5 x 5 x 2.58 mm and horizontal 74.2 degrees;
its product page gives 1.84 x 1.84 x 2.58 mm and diagonal 74 degrees. Do not
model either as qualified mechanical data. Request the exact revision drawing,
connector, spectral curve, working-distance datum and USB firmware support
[@appleyeMira016Eye; @appleyeMira016Product]. Its generic 6-8 week prototype
statement is not a delivery quote for our assembly.

## Board decision

Prefer a single physical board using an existing supported USB 2.0 UVC camera
controller circuit and firmware, adapted to our outline. Copper layer count is
separate from physical board count: one board may need four or more copper layers.
Do not freeze the old CX3 envelope as the chosen controller implementation.

First fabrication target: 0.4-0.6 mm rigid board. Manufacturers list these
thicknesses; exact layer stack, controlled impedance, assembly and connector
support require review [@jlcThinPcbCapabilities]. Alternatively use polyimide
flex, provisionally 0.1-0.2 mm, with local stiffeners at the connector and parts.
Flex fabrication and stiffeners are established options, but a supplier's minimum
thickness is not a guarantee for our circuit [@epecFlexCapabilities].

For identical area/material, reducing substrate thickness from 1.6 to 0.4 mm
reduces substrate volume and approximate substrate mass by 75 percent. This is
not a 75 percent reduction in the assembled camera: lens, copper, components,
connectors, stiffeners and cable still contribute. Report assembled mass when
parts are selected; the user has not set a numeric gram limit.

USB conversion happens on this thin board. Its outgoing four-contact connector
carries 5 V, D-, D+ and ground. The short MIPI flex stays inside the assembly.
Mechanical JST family selection, harness signal integrity and pinout remain
engineering work; four contacts do not make an arbitrary cable USB-qualified.

## Supplier deliverable

Request an existing working camera circuit adapted to this package, with samples
and a firm ship date. Require sample images at 10, 15 and 20 mm under the offered
NIR wavelength, full module drawing, spectral response, measured assembled mass,
USB mode list and recording demonstration. Target 400 x 400 at 120 fps initially;
state delivered USB modes separately from sensor ratings. Request hardware and
firmware access/licensing needed for our own subsequent board revisions.

The deliverable must include a supported USB controller/firmware route, not just
a sensor head. No supplier was contacted, no stock was reserved, and no hardware
was bought or fabricated. Existing R01/R02 CAD remains preserved concept geometry.
