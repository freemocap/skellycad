# Component-chain decision

Recommend OV9281 -> DS90UB953 -> shielded twisted pair -> DS90UB954 -> ESP32-P4 -> USB as a **conditional architecture candidate**. Do not release a purchase or fabrication order. Exact sensor supply is still unresolved.

## Compatibility evidence

The 953 accepts 80-832 Mbps per CSI lane. The proposed 800 Mbps/lane setting is within that range, but the R11 driver metadata disagreement remains unresolved. Use two lanes, RAW8 and VC0 initially. The 954 passes CSI data types through when paired with the 953; DVP RAW10/RAW12 limitations must not be mistaken for a RAW8 CSI prohibition [@ti953A01; @ti954A01; @espressifOv9281Driver].

Use the receiver backchannel as the serializer reference and retain the existing 24 MHz sensor oscillator until a validated CLK_OUT alternative exists. A 25 MHz base reference gives the candidate 4 Gbps forward link. Keep one receiver input active. Candidate 954 output is two lanes at 800 Mbps/lane; receiver FIFO, sensor blanking, CSI clock behavior and P4 receiver settings require a register-level audit and later hardware tests.

Power travels on separate conductors. Do not add power-over-coax filters to the STP candidate without need. Base I2C commands tunnel to the sensor through the link; exposure, reset and LED control therefore need no extra tether wires. Reserve a local LED driver and hardware off-state. This is a functional contract, not a connector pinout or finished circuit [@ti953A01; @ti954A01].

The P4 receives CSI and uses its High-Speed USB peripheral as a device. This avoids the bottleneck of receiving a USB camera on its only High-Speed port and then attempting to forward high-rate video through the Full-Speed port [@espUsbDeviceA01].

## Procurement observations, 2026-10-29

- OV09281-H64A: manufacturer page still lists it; Arrow says active/out of stock; DigiKey says obsolete. No traceable, immediately orderable bare-sensor supply was verified [@ov9281ProductA01; @ov9281ArrowA01; @r11SupplySensorDk].
- DS90UB953TRHBRQ1: Mouser UK indexed page reports 258 units; direct fetch failed. Treat as a lead to recheck, not reserved inventory [@ti953MouserA01].
- DS90UB954TRGZRQ1: LCSC indexed listing reports 348 units; recheck at ordering and qualify traceability [@ti954LcscA01].
- ESP32-P4NRW16X: earlier current distributor review reports backorder. Preserve rev3.x SDK compatibility; no silent package/revision substitution [@r11SupplyP4; @espP4Rev3Guide].

Only publicly accessible technical sources and existing licensed repository inputs are used. TI datasheets are linked, not relicensed or copied wholesale. Public access does not mean vendor firmware/libraries have no license obligations. Existing Antmicro and Espressif licenses remain unchanged.

## Alternatives and boundaries

Direct MIPI over the proposed four-conductor cable cannot carry its separate clock/data/control/power connections. USB at the head requires a camera bridge there; no smaller documented replacement has been qualified. Coax plus separate power remains a cable alternative if the STP connector/loss budget fails; power-over-coax would need a different filter/power study. None is silently substituted into this design.

The first firmware milestone is transport-independent synthetic continuous recording; then receiver test pattern; then sensor snapshots; then continuous sensor capture with frame counters, error counters and reconnect handling. No SerDes driver is claimed implemented. Architecture work can proceed with explicit sourcing/optics holds; a build order cannot.

Review scope: manufacturer feature, interface, clock and package excerpts; retailer listings/indexed snippets; saved R11 firmware and BOM. No pin-level schematic audit, cable certification, firmware execution or physical camera test.
