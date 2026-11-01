# Packaging recommendation — OV9281 + ESP32-P4

Use candidate B's **24 x 12 mm controller and 12 x 12 mm head** as the compact
development target. Keep candidate C as the alternative based on a published
construction. Do not manufacture the heavier A comparison simply to make progress.
First resolve the package weights and stackup constraints that determine whether
the compact target is practical. R10 remains the selected working electrical
baseline; this study does not select or route a replacement circuit.

## Result and mass boundary

The target is strictly **less than 1.000 g, excluding the external tether**.
It includes the OV9281, ESP32-P4, both board regions, their interconnecting flex,
all populated components, lens, holder, filter, illuminators, board-side connector,
solder, adhesive and module-side retention. The cable and cable-side plug are
reported separately. Moving the P4 into an external receiver is not used to make
these totals smaller.

| Construction | Controller / head, mm | Free neck, mm | Flat span | Estimated module mass |
| --- | --- | --- | --- | --- |
| R10 baseline | 32 x 20 / 14 x 14 | Existing separate flex | 76 mm | 2.18–3.92 g; nominal 2.95 g |
| A: thin modular | 32 x 16 / 14 x 14 | 30.3 x 12.5 | 76.30 mm | 1.63–2.87 g; nominal 2.16 g |
| B: custom thin rigid-flex | 24 x 12 / 12 x 12 | 32.85 x 8 | 68.85 mm | 0.72–1.63 g; nominal 1.10 g |
| C: locally supported SLIM.flex | 26 x 12.5 / 12.5 x 12.5 | 32.85 x 8 | 71.35 mm | 0.84–1.87 g; nominal 1.27 g |

These intervals are engineering scenarios, not measurements or confidence bounds.
**Neither compact nominal estimate meets one gram.** B needs approximately another
0.10 g reduction from its nominal budget; C needs about 0.27 g. Their low scenarios
are below the target, which makes the target worth investigating, not established.
No component mass has been obtained by treating a courtyard box as a solid package.

The selected Pupil comparison has a 30.85 x 9 mm controller, 15 x 6 mm head and
32.85 x 4 mm free ribbon. Its straight board outline is 78.70 mm. The reported
~0.7 g weight comes from the user, with its original weighing boundary unresolved.
The accepted CAD model and photo-based electronics blocks establish a useful
comparison envelope; their printing materials and thicknesses do not establish
the real camera's weight. The P4 package alone is 10 x 10 mm
[@esp32P4Datasheet], which prevents a direct 9 mm-wide controller match while it
remains on the module.

## What the study establishes

All candidate package reservations fit their proposed board outlines on two sides
without same-side overlap. A contains all 106 existing physical references; B/C
retain 105 after eliminating the inter-board connector J102. The conditional
smaller flash, regulator, switch and passive packages are listed individually in
`options.json`. They are not selected parts or electrically validated substitutions.
Q201 is moved to the underside in each packing. Programming-pad and connector-exit
areas are reserved, and A retains its solder-lap interface area.

C's support plate and hollow ring have explicitly reserved underside space. This
increased its controller dimensions relative to the initial sketch. Native CAD
checks found no component/support/optics intersection in the nominal reservations.
The complete Pupil reference and actual R10 geometry are included in the native
comparison. Those geometry checks establish neither routability nor physical fit.

The lighter B/C support is a 48.24 mm3 hollow solid, giving an assumed nominal
polymer mass of 0.0579 g. The lens remains a 6 mm envelope. Threads, attachment,
tolerances and stiffness are unresolved. Its axial barrel overlap drops to
0.47 mm at a reserved 1 mm extension; adequate retention has not been established.
The public CH2021A minimum object distance is 0.1 m [@chuanganCh2021a], so using
its envelope does **not** establish the requested 10–20 mm infrared focus.

## Construction and cost

B's 0.25 mm six-layer component region and 0.12 mm two-layer neck are custom
targets without a verified matching fabrication stackup. C uses the public
0.303 mm / 0.166 mm SLIM.flex construction as a stronger starting point
[@wurthSlimFlex0302026]. Its standard process uses microvias; existing R10
through-vias cannot simply be copied. The extra local stiffeners, their material,
adhesive and strength still require qualification.

No project quotation has been obtained. A is expected to have the lowest change
and assembly complexity; B/C require premium fabrication and assembly. That is
a comparative engineering expectation, not a price promise. Obtain comparable
assembled quantities, such as 5, 20 and 100, with tooling, fabrication, assembly,
parts, inspection, yield allowance and shipping itemized. Small-package assembly
capability exists [@pcbwayAssemblyCapabilities2026]; capability is not a quote or
an approval of this design. No supplier was contacted or given project files.

## Constraints for the next electrical revision

1. Keep OV9281 and P4 on the module, with infrared imaging and the four-contact
   USB connection as the primary architecture. Preserve the explicit mass boundary.
2. Select actual smaller parts before replacing footprints. Check regulator
   currents, losses and stability; capacitor effective capacitance under bias;
   inductor current and saturation; flash compatibility; thermal and assembly
   constraints. Keep every current electrical function accounted for.
3. Establish a fabricable stackup, via process and impedance geometry before
   rerouting. Preserve required return paths. Do not reduce copper only to meet
   a weight number. The 8 mm neck is a packing reservation, not a routed proof.
4. Replace the largest mass uncertainties with supplier package/lens data or
   physical measurements when available. Recalculate the whole module. Set a
   design margin below one gram before treating the target as met; do not choose
   only the favorable ends of independent uncertainty ranges.
5. Qualify 10–20 mm infrared focus, filter transmission and illumination before
   fixing the lens support. Reserve space for a real thread/retention solution,
   production tolerances and camera mounting; the present allowance is not proof
   of adequate strength. Re-budget any added enclosure or mounting structure.
6. Select the cable separately for USB behavior, voltage drop, flexibility and
   strain relief. Four conductors do not by themselves establish suitable USB
   construction. `tether-budget.json` gives mass-versus-length estimates and the
   limitations of its conductor assumptions; it is not a cable qualification.

Only after those choices should a new electrical revision replace the schematic
parts, redo placement/routing and repeat the electrical, geometry and mass checks.
Hardware tests will still be needed for image capture, timing, focus, thermal
behavior, robustness and real mass. Public Pupil performance figures remain
comparison targets [@pupilCore200Hz], not demonstrated OV9281/P4 performance.

The five-item approved packaging study is complete when the final validation and
checkpoint manifest are saved. This closes the size/mass investigation for this
session; it does not close the remaining camera-development project.
