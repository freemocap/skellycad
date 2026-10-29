# R11 electrical review

R11 is a fully connected offline engineering candidate. It is not a tested
camera or a released manufacturing design. The board keeps the OV9281 and
ESP32-P4 on one continuous C SLIM.flex circuit.

## Verified from native files

- 106 footprints, 105 populated parts; R7 remains DNP.
- 418 schematic pin assignments and 343 retained baseline signal nodes checked.
- 62 routed nets; zero ERC violations, PCB errors or unconnected items.
- 771 adjacent laser-via segments. All spans, diameters and transition setbacks
  checked. KiCad reports 199 coincident-hole warnings for stacked segments;
  `board-validation.json` identifies and explains each warning. No blanket DRC
  suppression is used.
- 393 clearance-checked copper tapers. None of the identified narrow junctions
  remains on the constrained-taper list. Tapers and drying openings follow the
  published construction guidance; fabrication approval remains separate
  [@wurthSlimRules2023].
- Native centerline measurements put each CSI conductor at approximately
  60.183 mm. Intrapaired mismatch is below 0.0001 mm after file quantization.
  Package delay, bend discontinuities and manufacturing tolerance are not
  included in that numerical precision.
- USB lengths include the connector/ESD copper and equal resistor-center spans.
  The saved report contains the actual paths and their layer transitions.
- Sampled trace centers and edges have filled In3 ground beneath every tested
  uniform CSI/main-USB section. Launch regions are reported separately.
- Components, vias and outer-layer copper remain outside the two-layer neck.

## Electrical models

The quasi-static cross-section model gives approximately 100.84 ohms for flex
CSI, 96.73 ohms for component-region CSI and 92.00 ohms for the main USB pair.
These nominal results fall within the selected manufacturer targets. The final
mesh changes the result by less than 0.8%; material and dimensional sensitivity
are retained in `impedance-validation.json` [@esp32P4HardwareGuide].

These are uniform-section calculations. They do not qualify the connector/ESD
fanout, package escapes, individual tuning lobes, material losses or a complete
channel eye diagram. Permittivities are engineering assumptions pending the
fabricator's actual materials and impedance compensation.

The DC sheet model uses the saved copper, explicit filled-via resistors and a
0.025 mm grid. At an assumed 1 A load, the controller model gives approximately
14.5 mV maximum core-rail drop and 9.4 mV system-rail drop. Coarser grids are
retained for comparison. This is a conductor stress screen, not a statement
that the camera draws 1 A or complies with USB bus-power limits. Regulator
transients, package impedance, heating and ground-return drop are excluded.

The separate sensor screen includes routed trace resistance, 0.247 ohm filter
DCR (0.19 ohm plus its 30% tolerance), 1.4% LDO error and an explicit return
allowance. It passes at the published typical rail currents. The conservative
core estimate is 1.159 V at 52 mA. At twice that typical current the estimate
is 1.135 V, approximately 4.7 mV below the published 1.14 V minimum. This is a
failed stress screen, not a demonstrated operating failure: maximum current
and transient behavior are not established. The earlier calculation omitted
the inductor DCR tolerance; this review corrects it. Loaded sensor-rail margin
must be qualified or the power delivery revised before fabrication. Measure
actual rail currents and sensor-pad voltages before accepting the power design
[@leopardOv9281Electrical2026; @tiTlv733R11; @tdkMlp2012R11].

## Qualifications that remain

The prototype review must establish regulator startup/load steps, capacitor
effective values, sensor sequencing and rail noise, crystal startup/drive,
actual clock/data signaling, USB enumeration/inrush/suspend current, and
thermal behavior. A powered hub is not evidence of bus-power compliance.

The fabrication review must establish sequential laser processing, filled and
capped via-in-pad structures, material tolerances, mask webs, drying openings
beside solid reference corridors, and the windowed stiffener bond. The native
global KiCad stackup cannot express local layer removal or independently
thicken the ENIG finish; `STACKUP.md` records those limits
[@wurthSlimFlex0302026; @wurthSlimRules2023].

The IR filter, 10–20 mm focus, optical datum height, lens retention and safe
illumination remain provisional. No physical fit, camera image, USB compliance
or eye-safety result is claimed.

Review scope: native schematic and PCB data, public component/package drawings,
regional construction, analytical component screens, 2D electrostatics and DC
conduction. See the final checkpoint verification for bibliography results.
