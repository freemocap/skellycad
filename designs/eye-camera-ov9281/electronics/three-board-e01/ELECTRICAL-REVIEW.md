# E01 electrical review

This is a connected schematic and placement study, not a functional camera or a fabrication release. Automated net equivalence, footprint pad-set checks and ERC are recorded in `electrical-audit.json`. They cannot validate a datasheet interpretation, physical cable, optics or firmware by themselves.

## Corrected during this phase

- Use the receiver's actual RGZ0048B 4.1 mm exposed pad, not a generic 7 mm package with a 5.15 mm pad. The serializer uses its RHB 3.7 mm pad. Both local footprints preserve the manufacturer's pitch and land dimensions [@ti953A01; @ti954A01].
- Use the WSON-specific TPS2553 pin numbers. External 5 V feeds the base and switched head power. USB VBUS has its own net, clamp supply and FET presence detector [@tiTps2553E01].
- Include all serializer internal-output bypass capacitors and connect LPF1 to VDDPLL. Keep all four receiver internal 1.1 V outputs separate [@ti953A01; @ti954A01].
- Fit low-capacitance TPD1E01B04DPYR clamps on both tether data conductors at both ends. Their component ESD rating does not certify the complete connector/cable or assembled system [@tiTpd1E01B04E01].
- Distinguish 7-bit addresses: receiver 0x30, serializer 0x18, sensor 0x60. Use 1.8 V head I2C and 3.3 V local base I2C; the link carries remote control [@ti953A01; @ti954A01; @antmicroOv9281Schematic].

## Required startup and shutdown contract

1. External source supplies regulated 5 V; USB VBUS remains electrically separate. Initially keep tether power disabled and receiver PDB low. The base clock-disable pull-up keeps its oscillator disabled.
2. Wait for base 3.3 V and receiver 1.8 V to settle. Pull clock-disable low, wait for oscillator startup, then drive receiver PDB high. Wait at least the receiver's 2 ms I2C-ready interval. Its VDDIO can rise before or after VDD18; actual rail rise times still need measurement [@ti954A01].
3. Select the synchronous CSI-2 receiver mode strapped by 78.7 kΩ/97.6 kΩ. Configure STP reception, port 0, remote I2C, two output lanes and the verified sensor format. Disable unused receive port 1. Do not assume strap mode alone configures the complete channel.
4. Enable head power. The serializer has its own delayed PDB, while the sensor reset and illumination gates remain low. Wait for stable power and link lock before accessing the serializer and sensor. The RC delay is a nominal startup provision; it is not a voltage supervisor [@ti953A01].
5. Configure serializer GPIO0 for sensor reset and GPIO1 for illumination. Release reset, load a validated sensor mode and confirm good frames before enabling either IR LED. Nominal LED branch resistance is 2.2 kΩ from head 5 V, about 1.7 mA for a 1.3 V LED drop. Optical exposure and irradiance are unqualified.
6. On lock loss, fault, stopped capture or watchdog reset, disable tether power. Normal reset pulls the power enable low. **Loss-of-link shutdown requires functioning firmware; this circuit does not contain an independent hardware watchdog that guarantees illumination off after every fault.**

## Performance and power limits

640 × 400 RAW8 at 100 fps is 25.6 MB/s before transport headers. A USB 2.0 high-bandwidth isochronous endpoint is limited to 24.576 MB/s before UVC overhead, so it cannot carry that uncompressed target. Bulk is the candidate transfer mode. Espressif documents bulk and isochronous UVC support, but documents JPEG input; a working RAW8/host path is not established by that documentation. Do not promise 100 or 120 fps from this design package [@usbIsoBudgetE01; @espUvcBulkE01].

The current-limit calculation uses an 80.6 kΩ, 1% resistor and the TI limit equations. It is a fault limit above the 210 mA planning load, not an arbitrary doubled-current normal operating requirement. The 36-AWG voltage-drop estimate uses copper resistance and explicit switch/contact allowances; cable temperature, connector resistance, inrush and measured load remain open [@tiTps2553E01].

The 1.8 V buck feedback uses 200 kΩ/100 kΩ with the 0.6 V reference. Retained P4 supplies follow R11's corrected support circuit. Effective MLCC capacitance, regulator startup, ripple, thermal rise and transient margin require exact-part curves and hardware verification [@tiTlv62569; @esp32P4HardwareGuide].

## Release holds

- Traceable available OV09281-H64A and exact P4 supply; quote the full BOM before committing a build.
- Qualified 100 Ω differential tether and connectors, including the added ESD capacitance, loss, reflections, skew, flex transitions and ground return. Four loose fine wires are not an RF specification.
- Manufacturer-approved flex stack, minimum features, stiffener registration, QFN/SON stencil and reflow process. Candidate new capacitor and resistor ordering codes need purchasing confirmation.
- Actual compact placement and routing closure, PDN assessment, effective capacitance and measured power/temperature.
- Close-focus IR lens, filter, mechanical retention, optical datum and exposure qualification.
- Implemented and tested initialization, RAW8 transport, host recording, watchdog and illumination shutdown.

These are explicit unresolved dependencies. No orderable manufacturing package is produced by E01.
