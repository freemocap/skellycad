# E01 component and documentation basis

Reviewed 2026-10-29. Proceed with a conditional electrical design; procurement and hardware qualification remain separate gates. No component was purchased or reserved.

| Function | Design basis | Verification and remaining hold |
| --- | --- | --- |
| Sensor | OV09281-H64A; preserved R11/Antmicro H64A symbol and footprint | Public reference circuit retained with attribution; manufacturer product page exists; exact traceable available supply remains unverified [@antmicroOv9281Board; @ov9281ProductA01; @r11SupplySensorDk] |
| Serializer | DS90UB953TRHBRQ1, 32-pin 5 x 5 mm VQFN | TI pin table, supply, bypass, LPF, straps, coupling and package sections reviewed; supplier stock is not reserved [@ti953A01; @ti953SupplyA01] |
| Receiver | DS90UB954TRGZRQ1, 48-pin 7 x 7 mm VQFN | TI pin table and internal 1.1 V LDO option reviewed; one receive port used, unused input disabled [@ti954A01] |
| Processor | ESP32-P4NRW16X, v3.x, 10 x 10 mm | Preserve official-library pin map and R11 support circuit; review against current v3.x checklist; exact package supply remains a hold [@esp32P4HardwareGuide; @esp32P4Datasheet; @r11SupplyP4] |
| Bucks | TLV62569DRLR, 1.6 x 1.2 mm | Preserve corrected DRL pin mapping; select feedback for each actual rail, retain inductor/capacitor ratings [@tiTlv62569; @murataDfe252012R11] |
| Sensor LDOs | TLV73312PDQNR and TLV73328PDQNR | Preserve DQN map including exposed ground; drive 1.2 V from local 1.8 V and analog 2.8 V from head input [@tiTlv733R11] |
| Base reference | SG-210STF 25.0000ML, 2.5 x 2.0 mm | 1.8 V oscillator in same documented family as retained 24 MHz head oscillator; output-enable sequencing required [@epsonSG210STF; @epson25E01] |
| Tether power switch | TPS2553DRVR, 2 x 2 mm WSON | Active-high enable, default-off pull-down, fault output, resistor current limit; exact WSON pad mapping checked separately from SOT-23 [@tiTps2553E01] |
| Supply filters | BLM18SG121TN1D, 0603 | Manufacturer list specifies 120 ohm at 100 MHz, 25 milliohm maximum DCR and 3 A rating; full channel/power-noise qualification pending [@murataFerritesE01] |
| Connectors | R11 JST SH four-contact part as a candidate; shield solder land; exposed debug/power pads | Actual pin-numbered footprint is available; connector plus cable RF performance is unqualified and remains a release hold [@jstShCatalog] |

Use documented 0402 passives and retain larger MLCCs where effective capacitance requires them. Do not replace necessary bypass capacitors with 0201 body reserves merely to reproduce A01's picture. AC-coupling capacitors use the TI-required 50 V X7R class; the inherited 16 V bypass capacitor is not silently substituted [@ti953A01; @ti954A01].

The serializer needs three separately bypassed internal-regulator outputs and its LPF1 capacitor returns to VDDPLL, not ground. The receiver's internal 1.1 V outputs also remain separate capacitor-only nodes. These are explicit circuit requirements, not optional padding [@ti953A01; @ti954A01].

The base uses externally supplied regulated 5 V and a separate USB signal/VBUS-sense connection; USB VBUS will not be tied to the external power rail. Compact solder landing pads avoid adding a full-size development-board connector. The finished USB cable/termination and power source are still system-level qualifications.

Supply review: manufacturer pages and public supplier listings were inspected. The exact OV sensor could not be established as immediately orderable; its earlier lifecycle listing conflict remains unresolved. Mouser's exact P4 page returned 403, and search results did not establish stock. Active TI product listings and distributor leads do not constitute a complete purchasable BOM. Preserve these holds rather than selecting undocumented substitutes.

Review scope: datasheet pin, power, configuration, package and reference-circuit excerpts; existing licensed reference schematics; current supplier page/index observations. No confidential information or newly contacted vendors. Pin-level design can progress conditionally; sourcing and channel qualification must pass before a build order.
