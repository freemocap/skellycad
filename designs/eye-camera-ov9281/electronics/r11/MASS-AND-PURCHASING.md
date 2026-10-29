# R11 mass and purchasing review

The complete module screens at **1.34 g nominal**, excluding the external tether. The low/high scenarios are **0.92/1.93 g**, not confidence bounds or guaranteed limits. The under-one-gram target is **not met by the nominal estimate**.

The material ledger uses actual native copper areas, the regional stack, coating/paste geometry, support and holder volumes, and per-package estimates. Copper is not added twice to a solid board envelope. Filled-via volume displaces polymer. The integrated flex and board connector are included. Most package masses and all unresolved optics remain assumptions. See `mass-budget.json` and `calculate_r11_mass.py` for every term.

Nominal copper density uses the cited copper data; the polymer density is a generic Kapton proxy, not the actual mixed laminate. FR4 support density and the two buck-inductor typical masses use their cited sources. Thickness, solder, finish and most package intervals are engineering scenarios [@cdaCopperDensity2026; @dupontKaptonDensity2026; @civaFr4Density2026; @murataDfeMass2025; @wurthSlimFlex0302026].

Nominal contributors: packages 0.572 g; copper 0.267 g; laminate and mask 0.250 g; solder and finish 0.071 g; supports and optics 0.182 g. Reducing area or unnecessary copper must preserve reference paths and power delivery. Moving the P4 to an off-module board would change the approved architecture and is not done here.

## Purchasing result

All 31 electronic purchasing lines, representing 104 fitted packages, have supplier observations. R7 is DNP; J103 is part of the PCB. The known unit-1-price subtotal is **USD 24.42**, including some unavailable parts. This is **not the total camera cost**: the sensor, two obsolete capacitor codes and all custom fabrication/assembly/optics costs remain unpriced. The CSV is a review BOM, not an order-ready cart.

Supplier pages and indexed snippets reviewed; these are web-listed observations, not reserved inventory, quotes, manufacturer lifecycle confirmation or delivery commitments. Counts and prices can differ between indexed captures. USD excludes tax, shipping, duties, reeling, assembly and fabrication.

| MPN | Qty | Supplier observation | USD, qty 1 | Evidence |
|---|---:|---|---:|---|
| AP1608F3C | 2 | DigiKey: Listed in stock | 0.4500 | [@r11SupplyLed] |
| DFE252012F-2R2M=P2 | 2 | DigiKey: Listed in stock | 0.2500 | [@r11SupplyBuckInductor] |
| ECS-400-10-37B2-CKM-TR | 1 | DigiKey: Listed in stock | 0.3600 | [@r11SupplyCrystal] |
| ESP32-P4NRW16X | 1 | Mouser: Backorder | 7.9800 | [@r11SupplyP4] |
| GRM1555C1H160JA01D | 2 | DigiKey: Listed stock; not recommended for new designs | 0.1000 | [@r11SupplyCap5] |
| GRM1555C1H220JA01D | 1 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyCap6] |
| GRM155R71C103KA01D | 2 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyCap7] |
| GRM155R71C104KA88D | 25 | DigiKey: Backorder | 0.1000 | [@r11SupplyCap3] |
| GRM188R61A475KE15D | 6 | DigiKey: Obsolete listing | Unpriced | [@r11SupplyCap1] |
| GRM188R71C105KA12D | 17 | DigiKey: Obsolete listing | Unpriced | [@r11SupplyCap2] |
| GRM21BR61A226ME44L | 4 | DigiKey: Backorder | 0.3200 | [@r11SupplyCap4] |
| MLP2012S3R3MT0S1 | 3 | DigiKey: Listed in stock | 0.2400 | [@r11SupplyFilterInductor] |
| OV09281-H64A | 1 | DigiKey: Listed obsolete; no orderable stock shown | Unpriced | [@r11SupplySensorDk] |
| PMZB200UNEYL | 4 | DigiKey: Backorder | 0.3900 | [@r11SupplyFet] |
| RC0402FR-07100KL | 3 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyRa3] |
| RC0402FR-0710KL | 6 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyRa0] |
| RC0402FR-071KL | 2 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyRb2] |
| RC0402FR-072K2L | 1 | DigiKey: Listed in stock | 0.1100 | [@r11SupplyRb3] |
| RC0402FR-07453KL | 1 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyRa2] |
| RC0402FR-07499KL | 2 | DigiKey: Listed in stock | 0.1100 | [@r11SupplyRa1] |
| RC0402FR-074K02L | 1 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyRb0] |
| RC0402FR-074K7L | 4 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyRb1] |
| RC0402JR-070RL | 4 | DigiKey: Listed in stock | 0.1000 | [@r11SupplyR0] |
| SM04B-SRSS-TB(LF)(SN) | 1 | DigiKey: Listed in stock | 0.5100 | [@r11SupplyJst] |
| TLV62569DRLR | 2 | DigiKey: Backorder | 0.2500 | [@r11SupplyBuck] |
| TLV73312PDQNR | 1 | DigiKey: Conflicting indexed stock; treat unavailable until checked | 0.1900 | [@r11SupplyLdo12] |
| TLV73318PDQNR | 1 | DigiKey: Backorder | 0.1900 | [@r11SupplyLdo18] |
| TLV73328PDQNR | 1 | DigiKey: Listed in stock | 0.1900 | [@r11SupplyLdo28] |
| USBLC6-2P6 | 1 | DigiKey: Listed in stock | 0.6500 | [@r11SupplyEsd] |
| W25Q32JVUUIQ TR | 1 | LCSC: Alternate listing reports stock; packaging confirmation required | 2.5291 | [@r11SupplyFlash; @r11SupplyFlashLcsc] |
| X1G004171003100 | 1 | LCSC: Out of stock | 0.9297 | [@r11SupplyOscillator] |

## Required purchasing decisions

- No qualified stocked OV09281-H64A source established. DigiKey obsolete listing is not independent manufacturer lifecycle confirmation.
- P4 and several regulators, FETs, oscillator and capacitors have backorder, unavailable or conflicting stock observations.
- Two selected capacitor codes are listed obsolete and the 16 pF code is not recommended for new designs. Suggested substitutions require a controlled component update and DC-bias/package verification.
- Flash is listed obsolete at DigiKey but available under its base code at LCSC; exact packaging, lifecycle and traceability remain unresolved.
- Custom fabrication, assembly and close-focus IR optics have no verified quote.

Supplier substitutes are research leads only. They are not silently installed into the native design. Recheck exact ordering codes, land patterns, height, rated/effective capacitance, crystal load and traceability before replacing parts.

Review scope: exact-MPN supplier product pages and indexed excerpts checked on 2026-10-29, matched to all populated native references. Sources do not establish physical fit, manufacturer lifecycle or guaranteed delivery. No order, vendor contact or fabrication submission was made.
