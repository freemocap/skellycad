# R11 firmware and connector contract

R11 preserves the R10 electrical functions while replacing the two separable
24-contact flex interfaces with continuous copper. The selected processor is
ESP32-P4NRW16X, revision v3.x, with 16 MB internal-package PSRAM and 4 MB external
3.3 V flash. These assignments describe the schematic; they do not establish
physical camera operation. [@esp32P4Datasheet; @winbondW25Q32JvK2026]

| Function | Assignment | Required behavior |
|---|---|---|
| Camera control clock/data | GPIO7 / GPIO8 | 100 kHz SCCB through 3.3–1.8 V translation |
| Sensor address | 0x60, 7-bit | R8 fitted; R7 DNP |
| Sensor reset assertion | GPIO6 | High asserts reset; release only after supplies and clock settle |
| IR LED control | GPIO5 | Default low; two 1 kΩ current-limited branches |
| Camera clock | Dedicated 24 MHz, 1.8 V oscillator | Independent of a firmware clock output |
| MIPI CSI-2 | P4 dedicated D0/D1/CLK pins | Two lanes; verify driver timing against the selected mode |
| USB | Dedicated P4 USB D− / D+ pins | ESD protection and zero-ohm series links retained |
| Flash | Dedicated SPI pins, 3.3 V | DIO, 40 MHz, 4 MB; do not select a 1.8 V flash supply |
| Programming | J103 exposed pads | UART TX/RX, ground, boot and enable; use schematic pad numbers |

J101, viewed by its native footprint pin numbers, is **1: USB VBUS, 2: D−,
3: D+, 4: ground**. Its mechanical part is JST SM04B-SRSS-TB(LF)(SN).
This definition does not establish compatibility with a Pupil Labs cable.
The external cable is excluded from the mass target; J101 is included.
[@jstShCatalog]

## Package changes checked in this revision

- The DRL buck regulators use pins 1 FB, 2 ground, 3 VIN, 4 SW, 5 EN,
  and 6 NC. Their maps differ from the former DBV packages. [@tiTlv62569]
- Each DQN sensor regulator uses 1 OUT, 2 ground, 3 EN, 4 IN and
  5 exposed thermal ground. The central land is connected. [@tiTlv733R11]
- The USON flash retains signal pins 1–8. Both small mechanical center
  lands are pad 9 and connect to ground. [@winbondW25Q32JvK2026]
- PMZB200UNE uses 1 gate, 2 source and 3 drain. The signal-translation
  topology remains unchanged. [@nexperiaPmzb200R11]

The placement pass also replaces Q201's larger bipolar package with PMZB200UNE.
GPIO5 drives its gate through R203 (2.2 kΩ); R204 (100 kΩ) pulls the gate low.
The old IR_BASE net is renamed IR_GATE. The two 1 kΩ LED resistors remain.
The calculated current is approximately 2.02 mA per LED at the stated nominal
LED forward voltage; optical exposure still requires measurement.
[@nexperiaPmzb200R11; @kingbrightAP1608F3C]

The new local land patterns use TI's DRL dimensions, Murata's 2.8 mm outer /
1.2 mm inner inductor pad spacing, and ECS's stated 1.35 × 1.15 mm pad-center
spacing. The ECS drawing's vertical dimension chain is inconsistent with its
stated center spacing; the explicit center spacing governs this footprint.
Its 0.45 ± 0.05 mm height is reserved as 0.50 mm maximum. Confirm this drawing
interpretation against the supplied reel/package before assembly.
[@tiTlv62569; @murataDfe252012R11; @ecs1637b2R11]

Review scope: all native schematic pins, baseline functional connections and
footprint pad numbers are compared by `validate_r11_schematic.py`. The native
ERC report is retained. Package drawing review is not an assembly-yield test.
