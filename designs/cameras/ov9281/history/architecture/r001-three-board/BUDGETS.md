# System budgets

All results are calculated scenarios. `calculate.py` reproduces `budgets.json`. No electrical, optical, mechanical or thermal result has been demonstrated on hardware.

## Image transport

| Mode | RAW8 payload MB/s | USB qualification target MB/s | Four capture buffers | Two spare buffers absorb |
|---|---:|---:|---:|---:|
| 640 x 400 at 100 fps | 25.60 | 35 | 1,024,000 bytes | 20.00 ms |
| 640 x 400 at 120 fps | 30.72 | 40 | 1,024,000 bytes | 16.67 ms |
| 1280 x 800 at 120 fps | 122.88 | Cannot fit raw USB2 | 4,096,000 bytes | 16.67 ms |

The proposed two-lane 800 Mbps CSI links provide a 1.6 Gbps line-rate ceiling. CSI packet estimates include 6 header/footer bytes and 8 optional line-start/end bytes per image line, plus 8 frame-start/end bytes. A separate 20 percent payload planning allowance is a chosen screen, not a protocol standard or validated sensor blanking budget. The 953 can accept these candidate lane rates, and the 954 forwards CSI data types [@ti953A01; @ti954A01].

USB 480 Mbps is a signaling ceiling, not 60 MB/s usable streaming. Target measured sustained application payload of 35 MB/s for primary and 40 MB/s for stretch operation. These targets are not demonstrated. Full sensor resolution at 120 fps cannot cross USB2 as RAW8. Compression or a different base-station output would be needed [@espUsbDeviceA01; @omnivisionOv9281Brief].

Four capture buffers plus one frame-sized USB staging buffer use 1.28 MB at 640 x 400. Conservatively two buffers may be occupied, leaving two for host stalls: 20 ms at 100 fps. A four-touch memory-traffic scenario is 102.4 MB/s; PSRAM/cache/DMA bandwidth needs measurement. Buffer capacity is not a latency guarantee. Exposure, readout, serializer FIFO, DMA, queueing and host scheduling must be timed separately. Record capture time and host-arrival time separately; do not call receipt time exposure time.

## Cable and local power

Chosen input assumptions: 1.5 ohm/m per 36 AWG-class conductor at 20 C; copper temperature coefficient 0.00393/K; 0.2 ohm total connector/contact allowance. Actual cable construction is unselected. Solve the constant-power load equation Vin = Vs - R*P/Vin, not a fixed-current estimate. Nominal head-side input power is approximately 0.630 W; a separate 0.9 W / 40 C / 4.75 V scenario explores uncertainty. It is not a claimed maximum load or mandatory stress multiplier.

| Tether | Case | Received V | Supply current mA | Cable/contact loss mW |
|---|---|---:|---:|---:|
| 0.30 m | nominal | 4.857 | 129.6 | 18.5 |
| 0.30 m | higher_load_screen | 4.517 | 199.3 | 46.5 |
| 0.60 m | nominal | 4.734 | 133.0 | 35.4 |
| 0.60 m | higher_load_screen | 4.302 | 209.2 | 93.7 |

Both lengths clear the chosen 3.3 V regulator-input screen. This proves only those DC calculations. The 4 Gbps channel still needs actual cable/connector impedance and loss data or measured eye/BER validation, including flexed conditions. Shield and ground termination are unresolved. Do not assume that a four-pin JST qualified for USB is qualified for this link.

The 1.8 V buck powers serializer and sensor IO, plus the input to the 1.2 V LDO. A separate 2.8 V analog LDO supplies the sensor. The sensor rail-current sum (0.134 W) is smaller than the product brief active figure (0.156 W); retain 0.022 W allowance instead of hiding the discrepancy. The remaining clock/control/IR allowances and 85 percent converter efficiency are assumptions [@omnivisionOv9281Brief; @leopardOv9281Electrical2026; @ti953SupplyA01].

A provisional 25 mm, 0.3 mm wide, 18 um copper core-supply route plus the R11 maximum filter DCR gives 1.164 V at 52 mA, above 1.14 V. The calculated minimum is reached at 114.6 mA. This is not route validation or a substitute for the missing peak-load and transient requirements [@tiTlv733R11; @leopardOv9281Electrical2026; @tdkMlp2012R11].

Base station uses a separately powered bench configuration initially; allocate 1.5-3 W to base electronics before hardware measurements. A regulated 5 V / 1 A source is a planning candidate, not the product USB power contract. Check startup, current limiting, sequencing and USB backfeed isolation in detailed design.

## Mass and placement envelopes

Candidate head 14 x 10 mm; interface 18 x 10 mm; local flex 25 x 5.5 mm; flat span 57 mm. Base station envelope 40 x 30 mm, 0.8 mm board. These are study targets, not routed minima. Retain the known R11 0.303/0.166 mm construction as the initial mass basis rather than assuming an unqualified thinner stack. Copper coverage is varied; it is not yet native routed copper.

| Backing option | Low g | Nominal g | High g |
|---|---:|---:|---:|
| FR4_100um | 0.645 | 0.871 | 1.192 |
| steel_50um | 0.703 | 0.929 | 1.250 |

The nominal FR4 option targets 0.871 g, leaving about 0.129 g below one gram. The high scenario fails the target. These are scenarios, not confidence intervals. A 0.21 g package allowance and 0.15 g optics/holder/filter/retention allowance dominate uncertainty. R11 was 1.343 g nominal: the new nominal estimate is about 35 percent lower, with different uncertainty and no demonstrated mass.

Full backing area is reserved: 0.10 mm FR4 + 0.05 mm adhesive or 0.05 mm stainless + 0.025 mm adhesive. Steel is thinner but heavier in these scenarios. Neither support has a stiffness/strain validation. Recommend FR4 first for mass; keep metal as an evaluated geometry option, not presumed superior. Polymer/coating volume excludes the effective copper volume; there is no solid-envelope-plus-copper double count [@cdaCopperDensity2026; @dupontKaptonDensity2026; @civaFr4Density2026].

The tether is excluded from the head target but not ignored: four bare nominal 0.127 mm copper conductors alone weigh about 0.135 g at 30 cm and 0.271 g at 60 cm. Insulation/shield/terminations increase these. An illustrative complete cable allocation of 0.6-1.5 g/m is unverified. Base PCB/packages/connectors are allocated 3-7 g, excluding enclosure and backpack mounts. A complete backpack mass cannot be claimed yet.

## Thermal limits

The serializer alone is typically 0.28 W; the head assembly dissipates roughly its 0.63 W electrical input less emitted IR light. Smaller packages do not make that heat disappear. No thermal resistance or surface-temperature limit is invented for animal contact. Determine interface/head temperature distribution with the final support, mount, airflow and tether before eye-adjacent use. IR output/exposure qualification remains separate from electrical current limiting [@ti953SupplyA01].

Review scope: analytical arithmetic using explicitly marked assumptions and cited component figures. No RF channel solve, thermal simulation, actual package weighing, manufactured stackup, or powered test.
