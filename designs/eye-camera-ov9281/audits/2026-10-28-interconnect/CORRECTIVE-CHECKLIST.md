# Corrective routing worklist

This is the complete proposed response to this interconnect audit. It has not
been executed or approved as the next session. The current approved session
ends with the audit package. Future sessions may take a coherent subset of this
worklist after the user approves its displayed checklist.

- [ ] Select manufacturable rigid and flex stackups, calculate the 100 ohm MIPI and 90 ohm USB geometry, and record tolerances, via limits and explicit matching budgets.
- [ ] Restore uninterrupted reference-plane regions on both rigid boards by moving obstructing signal and power routes, preserving every net connection.
- [ ] Reroute all three sensor-head MIPI pairs with consistent pairing, compatible layers, matched transitions, ground-return vias and clock guarding.
- [ ] Reroute all three controller MIPI pairs with consistent pairing, compatible layers, matched transitions, ground-return vias and clock guarding.
- [ ] Revise flex pair geometry and both termination regions, then close the complete head-to-controller matching and spacing budgets.
- [ ] Reroute the complete USB pair through the resistor and ESD region to J101, and define the matching cable, pin mapping and shield termination.
- [ ] Recheck the complete design and all audit findings, preserve the new checkpoint, and regenerate a matched KiCad/FreeCAD review.

## Coverage and acceptance

| Work item | Audit IDs addressed | Evidence required before checking it off |
| --- | --- | --- |
| Stackup and geometry | Z-head, Z-controller, Z-flex-study | Orderable or otherwise supported layer construction; documented impedance calculation including coating and copper tolerances; supported dimensions; no nominal-thickness-only impedance claim |
| Reference planes | R-head, R-controller, U-REF | No unreviewed reference discontinuities along high-speed corridors; no connectivity regressions; narrow DC bridges must not be presented as proof of return-path quality |
| Head pairs | M-CLK, M-D0, M-D1, L-head-D0, L-head-D1, V-head, G-head | All three pairs reviewed together; symmetric transitions and pair geometry; clock guarding; return-via geometry justified |
| Controller pairs | M-CLK, M-D0, M-D1, L-controller-D0, V-controller, G-controller | All three pairs reviewed together, preserving the actual U101/J102 pin assignments and ground reference |
| Flex and matching | M-SPREAD, all M-* pair mismatches, R-flex-study, Z-flex-study | All six conductors included; connector fingers, solder lap, stiffeners and plane setback considered; assembled delay budget distinguished from planar length totals |
| USB and cable | U-LENGTH, U-REF, U-PAIR, U-CABLE, Z-controller | Complete U101-to-host channel definition, including R109/R110, U105, J101 and cable; impedance and matching targets explicitly sourced; shield path and power conductors specified |
| Combined validation | Every finding | Native DRC, net/polarity mapping, end-to-end geometry and reference checks; updated annotations; source lineage; matched geometry exports; remaining simulation and physical-test limits stated |

Use candidate four-layer routing only if it can meet these conditions. If the
sensor escape cannot retain the required reference and pair geometry, propose
the six-layer or alternative via-process change before adopting a different
construction. Do not solve clearance problems by silently relaxing the rules.

Espressif's MIPI matching and impedance recommendations supply the present
screening budgets [@esp32P4PcbLayout]. The USB-specific numerical skew budget
still needs an explicit design decision. TI's generic guide also recommends
2 mil (0.0508 mm) matching measured at the package boundary; that is a different
measurement convention from the pad-center copper paths in this audit and is
not claimed here as a P4-specific limit [@tiUsb20Layout2013].

Offline closure can establish documented layout compliance and bounded model
results. Fabrication yield, assembled channel behavior, real camera capture,
USB throughput and optical performance still require physical verification.
