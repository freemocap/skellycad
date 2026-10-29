# R10 mass and space budget

**R10 screening estimate: 2.18–3.92 g, nominal scenario 2.95 g, excluding the
external tether.** This is a modeled range, not a weighing or statistical
confidence interval. The nominal copper sheets alone are approximately 1.24 g.
The present wide six-layer layout is not a credible subgram implementation.

`native-geometry.json` records copper polygon-union area on all 14 board layers,
via drill sizes, every footprint and its native courtyard. `component-budget.csv`
and JSON account for all 106 physical component footprints individually. The
programming pads, solder-lap footprint and two flex contact arrays have zero
separate component mass; their copper is already included in the boards.

## Method and uncertainty

Copper mass = native copper area x finished foil thickness x density. Nominal
foil is 35 um on rigid boards and 24 um on flex. The 8.91 g/cm3 nominal density
uses the CDA C11000 table [@cdaCopperDensity2026]. A +/-20% copper screening
interval is deliberately broader than numerical polygon precision; it is not a
fabricator tolerance. Barrels and finish have separate allowances. Board
laminate uses the 1.7–1.9 g/cm3 FR-4 range [@civaFr4Density2026], with dielectric
thickness scenarios, drill subtraction and resin-filled etched inner regions.
Polyimide uses 1.42 g/cm3 nominal as a generic proxy [@dupontKaptonDensity2026];
adhesives, coatings and stiffener material densities are explicit assumptions.

All **component weights are package-class estimates**, not verified manufacturer
weights. Capacitor heights, metal content, actual order codes and population
options can change them. Do not use inflated courtyard boxes as solid package
volumes. Native courtyard area is used only for packing; each package's separate
mass interval and height reservation are recorded alongside its reference.

The holder uses its current 103.4 mm3 CAD volume and an assumed polymer density.
The CH2021A specification lists a 4P lens and leaves its weight blank; the 40–150
mg lens interval is an engineering assumption, not a supplied weight
[@chuanganCh2021a]. The 0.1 m published minimum object distance also does not
qualify our intended 10–20 mm use. Filter, solder, adhesive and retention have
separate allowances. No external cable, cable-side plug or external mount is
included in the camera-module total.

## Tether, reported separately

`tether-budget.json` compares four-conductor AWG28/32/36 scenarios at 5, 10 and
20 cm. Copper is calculated from wire area and density; insulation, shield and
jacket are assumed ranges. The cable-side plug adds a separate allowance. The
0.5 A voltage-drop scenario is not measured consumption or an ampacity rating.
AWG36 is outside the reviewed JST SH contact wire range; using it would require
a different qualified termination [@jstShCatalog]. No cable has been selected.

Stiffness cannot be inferred reliably from conductor gauge alone. Strand count,
insulation, twist, shielding, unsupported length and strain relief all matter.
Keep a cable attachment/strain-relief reservation in the packaging study, then
qualify electrical performance and mechanical loading with an actual assembly.
