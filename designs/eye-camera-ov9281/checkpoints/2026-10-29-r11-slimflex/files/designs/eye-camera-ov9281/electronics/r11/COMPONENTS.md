# R11 component selection

`components.json` assigns a manufacturer part and expected pin-to-net mapping to
every physical component. It retains the complete R10 sensor bias network and
the ESP32-P4 v3.x electrical functions. The integrated flex replaces J102 and
J201; J104 was an obsolete schematic-only IR port. Programming lands remain.
This is an offline engineering selection, not evidence of a functioning camera.

## Selected changes

| Function | Selection | Package and electrical decision |
| --- | --- | --- |
| Flash | W25Q32JVUUIQ TR | 4 × 3 × 0.6 mm maximum-height USON; 4 MB, 2.7–3.6 V; use the P4's default 3.3 V flash supply and 40 MHz DIO [@winbondW25Q32JvK2026; @esp32P4HardwareGuide] |
| System and core bucks | TLV62569DRLR | 1.6 × 1.6 mm SOT563; pin 1 FB, 2 GND, 3 VIN, 4 SW, 5 EN, 6 NC; preserve the revision-specific P4 feedback network [@tiTlv62569; @esp32P4HardwareGuide] |
| Sensor regulators | TLV73318PDQNR, TLV73312PDQNR, TLV73328PDQNR | 1 × 1 mm X2SON; pin 1 OUT, 2 GND, 3 EN, 4 IN; center thermal land connects to GND [@tiTlv733R11] |
| SCCB translation, reset and IR switching | PMZB200UNEYL | 1 × 0.6 mm DFN1006B; G/S/D = 1/2/3; specified 0.49 ohm maximum at 1.5 V gate drive, 25 °C [@nexperiaPmzb200R11] |
| Buck inductors | DFE252012F-2R2M=P2 | 2.5 × 2 × 1.2 mm; 2.2 uH, 3.3 A saturation criterion, 2.3 A temperature-rise rating, 0.082 ohm maximum DCR [@murataDfe252012R11] |
| Processor crystal | ECS-400-10-37B2-CKM-TR | 40 MHz, 10 pF load, 10 ppm initial tolerance, 2 × 1.6 mm; start with two 16 pF C0G capacitors [@ecs1637b2R11; @ecs400R11] |
| Bulk capacitors | GRM21BR61A226ME44L | Keep 0805, 22 uF, 10 V; change C123/C124 from 10 to 22 uF for capacitance margin [@murata22u10v2025] |

The flash's two mechanical center lands share local footprint pad 9 and ground.
Winbond permits grounding these lands; avoid exposed vias under them. The TI
regulators also require their thermal lands soldered. Compact footprints need
correct paste and mask geometry, not merely smaller body outlines
[@winbondW25Q32JvK2026; @tiTlv733R11].

The OV09281-H64A sensor, Epson X1G004171003100 24 MHz 1.8 V oscillator, three
MLP2012S3R3MT0S1 bias inductors and USBLC6-2P6 protection remain.
The LEDs use AP1608F3C with separate 1 kohm resistors. The placement pass replaces
the larger MMBT3904 with PMZB200UNE, retaining a low-side switch, 2.2 kohm gate
resistor and 100 kohm gate pulldown. Keep GPIO5 low at boot
[@omnivisionOv9281Brief; @antmicroOv9281Board;
@epsonSG210STF; @tdkMlp2012R11; @stUsblc6; @kingbrightAP1608F3C;
@nexperiaPmzb200R11].

Resistors are 0402 Yageo RC parts, 1% except zero-ohm links. Capacitors retain
0402/0603/0805 sizes according to the selected ratings; nominal capacitance is
not effective capacitance under bias [@yageoRc0402R11; @murataMlccList2025].

## Compatibility and remaining qualification

Run `python designs/eye-camera-ov9281/select_r11_components.py` from the repository
root to regenerate the selection and `component-calculations.json`. A successful
run verifies that every physical reference has a part and pin map, that the
resistor/feedback-tolerance voltage ranges fit the processor rails, and that the
chosen inductor/current and 100 kHz SCCB screening budgets fit their stated limits.

The sensor screen assumes a 0.2 W load envelope, above the published 0.156 W active
figure. This is not a specified worst-case power figure. The 300 mA LDOs cover
the resulting individual current bounds. A hypothetical all-core allocation
would dissipate 0.375 W in the 1.2 V LDO at 3.45 V input; thermal performance on
the actual thin board therefore needs explicit checking. Do not treat JEDEC-board
thermal resistance as the thermal resistance of this module
[@omnivisionOv9281Brief; @tiTlv733R11].

The selected crystal load calculation assumes 2 pF of board/input stray
capacitance: 16 pF / 2 + 2 pF = 10 pF. Frequency, startup and drive level remain
prototype measurements [@esp32P4HardwareGuide; @ecs1637b2R11].

The two LEDs draw about 2 mA each in the nominal electrical model. Their default
is off. Neither that current nor a successful synthetic recording establishes
eye safety, optical focus or real camera performance. The board-side four-pin
JST assignment is 1 VBUS, 2 D−, 3 D+, 4 GND; this does not establish compatibility
with an existing Pupil Labs cable [@jstShCatalog].

Item 5 must check routing-dependent power integrity, capacitance sensitivity,
USB startup/current bounds and thermal assumptions. Vendor fabrication review,
physical bring-up, optical qualification and eye-exposure assessment remain
release gates. No component was ordered during this selection.
