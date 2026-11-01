# E01 electrical-design requirements

This phase creates connected electrical designs and unrouted compact placement studies for three boards. R11 and A01 are preserved. Hardware operation and manufacturing release remain separate milestones.

## Size and mass objectives

The complete head-mounted assembly must target **less than 1.0 g**, including camera head, interface island, local flex, populated parts, optics/filter/retention, backing, adhesive, camera-side connector and mounting/strain relief. Report external tether mass separately.

The base station is a **compact wearable backpack module**. Minimize board area, thickness, component height, connectors and unnecessary circuitry. The A01 40 x 30 mm outline and 3-7 g electronics allowance are comparison values, not dimensions to retain or permission to add weight.

Use 30 x 25 mm and 3 g populated electronics as provisional optimization goals for the base, and 5 g for the complete backpack assembly including enclosure, connectors, strain relief and mounting allowance. These are engineering planning allocations, not measured capacities or species-specific carrying limits. Report deviations explicitly; do not force unsafe electrical clearances to meet them. Include any onboard energy storage if later introduced; none is required in this externally powered design.

Preserve A01's 14 x 10 mm head, 18 x 10 mm interface and 25 x 5.5 mm flex as starting envelopes. Actual pads, assembly clearances, optical retention and routing space govern the E01 placement; report necessary growth and its mass cost. Prefer small documented packages while retaining required capacitance, current, heat dissipation and test access. Avoid large permanent debug headers where exposed programming pads suffice.

## Electrical and optical contract

Retain OV9281, DS90UB953, DS90UB954 and ESP32-P4 as the conditional component chain, subject to pin-level documentary checks. Target 640 x 400 RAW8 at 100 fps; 120 fps is a stretch. Four-conductor tether means a differential signal pair, 5 V supply and return, with a separate shield. It is not USB. Evaluate 0.30 and 0.60 m cable cases. The local sensor flex is separate from that tether.

Retain a dedicated 24 MHz sensor oscillator. Audit actual CSI lane rates and sensor reset polarity against documentation. Keep two independently current-limited IR emitters on opposite sides of the lens along the long axis, with illumination off during startup or loss of control. No exposure or thermal safety is inferred from these circuit provisions.

Optics remain provisional: visible rejection, near-IR transmission and 10/15/20 mm working distances. Do not silently change the sensor or crop the optical field. Exact connector selection, fabrication stack and component procurement holds must remain visible.

## Deployment and verification

Mouse: base above enclosure, with cable loads evaluated separately. Rat, ferret and marmoset: the same compact base is a backpack candidate, whose complete carried mass and thermal behavior require later species-specific assessment. This phase does not alter animal geometry or mounts.

Use CLI and macros. Save native files and validation evidence in a new revision, keep finished build documents closed, and leave only the saved current review open. Establish pin connectivity, ERC results, package-pad mappings and placement feasibility; do not label an unrouted board or untested firmware as functional hardware.
