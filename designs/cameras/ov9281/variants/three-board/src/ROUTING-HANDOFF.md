# E01 routing handoff

This package completes the approved electrical-design session. It does not complete the camera project. R11 remains the preserved routed predecessor; E01 is a new architecture whose 488 PCB connections are not routed.

## Before freezing a routed design

1. Close the mass gap. The nominal complete head estimate is 1.306 g without tether. Replace package and optics allowances with defensible masses, refine the layout and agree a qualified construction. Do not remove required bypass/filter parts or assume a two-layer serializer board simply to pass the target [@ti953A01].
2. Confirm exact sensor and P4 supply, passive order codes, voltage/bias capacitance and compatible assembly processes. The BOM is not a purchasing-ready list.
3. Freeze the lens/filter/holder interface. Keep the two IR emitters on the long axis beside the lens. The current 8 mm holder and 6 mm barrel are provisional, so no physical fit or focus is established.
4. Confirm the stack with the fabricator: four-layer populated regions, two-layer free flex, full backing assumptions, layer terminations, stencil, bend clearance and QFN/SON thermal-pad treatment. KiCad's global thickness does not define the regional stack by itself.

## Routing sequence

1. Place each high-frequency bypass capacitor against its actual supply pin and minimize the loop to ground. Keep serializer internal-cap outputs and receiver internal 1.1 V outputs separate. Preserve LPF1's return to VDDPLL.
2. Place regulators, inductors, feedback and input/output capacitors as compact power loops. Verify regulator stability and effective capacitance. Recalculate sensor DVDD at maximum supported operating current across the local flex and filter; nominal-current calculations are not a worst-case guarantee.
3. Route sensor CSI pairs to the serializer with continuous return paths. Derive trace geometry from the actual stack and control intra-pair skew. Do not reproduce R11's meanders or force unrelated nets to equal lengths.
4. Route serializer output through its two 50 V coupling capacitors and low-capacitance protection to the four-contact tether connector. The connector carries 5 V, link N, link P and ground; it is not USB. Shield termination is separate.
5. Route the corresponding base input to the receiver, then two CSI lanes and clock to the P4. Preserve local control, reset, clock-enable, lock/fault reporting and default-off tether power.
6. Route P4 core power, memory, crystal, USB and debug. Keep host VBUS separate from external 5 V. Verify the cable, connector and protection discontinuities using appropriate models or measurements.
7. Run full connectivity, clearance, return-path, power and mechanical audits. Re-export a matched assembly and recompute mass after routing and construction changes. Resolve all substantive findings before generating fabrication files.

## Firmware and eventual bench work

Implement the startup/shutdown contract in `ELECTRICAL-REVIEW.md`. Confirm sensor mode, serializer GPIO behavior, STP settings, remote I2C, CSI format and USB transport. RAW8 at 640 × 400 × 100 fps requires bulk transfer or another transport approach; the documented Espressif UVC JPEG path does not establish RAW8 compatibility [@espUvcBulkE01; @usbIsoBudgetE01].

Hardware must establish rail behavior, signal integrity across the selected 30/60 cm cable, image quality, frame delivery, thermal behavior, fault recovery and illumination exposure/shutdown. E01 has no independent hardware guarantee that IR LEDs turn off on every lost-link fault. No animal-mounted use is validated by these CAD checks.
