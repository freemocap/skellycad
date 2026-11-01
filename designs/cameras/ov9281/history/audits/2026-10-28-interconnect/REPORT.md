# Interconnect audit — 2026-10-28

The audit is complete. The present routing is connected, but it does not meet
the reviewed high-speed layout guidance. No corrective copper changes were
made in this session. There are 21 localized findings and a complete proposed
[corrective worklist](CORRECTIVE-CHECKLIST.md).

## Main results

| Check | Result |
| --- | --- |
| Native input identity | All five files match `routing-review.json` before and after inspection |
| MIPI routing continuity | 18 board-level paths connected; all 24 connector-pin checks preserve mapping |
| Clock pair difference | 1.184 mm versus 0.254 mm geometric budget |
| Data 0 pair difference | 2.214 mm versus 0.254 mm geometric budget |
| Data 1 pair difference | 1.384 mm versus 0.254 mm geometric budget |
| Pair-mean spread | 13.772 mm versus 0.762 mm screening budget |
| USB routing continuity | Four net sections connected through the documented zero-ohm links |
| USB copper-path difference | 2.379 mm; P4-specific numerical tolerance not established |
| Reference coverage | Sampled gaps on both rigid boards and at both flex terminations |
| MIPI transition returns | 14 of 16 signal vias have no GND via within 1 mm; two have one; screening heuristic only |
| Impedance | Not calculated or qualified for the provisional stackups |
| External cable | Pinout checked; construction, length and shield termination unresolved |

The MIPI budgets are drawn from Espressif's layout guidance
[@esp32P4PcbLayout]. Pair means are this audit's declared inter-pair screening
convention. Different routing layers and materials make geometric length an
incomplete substitute for propagation delay.

## Open the work

- Open `index.html` as rendered HTML for selectable issue overlays on actual
  native board geometry. Cyan/violet identify conductors; orange marks sampled
  reference gaps. The grey-green ground fill is context and can be on a
  different layer from the selected signal.
- Open `native/AUDIT-head.kicad_pcb`, `native/AUDIT-controller.kicad_pcb` or
  `native/AUDIT-flex-study.kicad_pcb` in KiCad for native inspection. Show
  **Dwgs.User** to see finding IDs, representative callouts and gap overlays.
  These are annotated copies, not manufacturing inputs.
- `findings.json` contains every finding ID and board-coordinate location,
  including trace/via UUIDs where applicable. `mipi.json` and `usb.json` contain
  the full paths and numeric evidence. Coordinates are in local board frames.
- Read [requirements](requirements.md), [MIPI details](MIPI.md) and
  [USB/cable details](USB.md) for assumptions and source-review boundaries.

The native review copies were reloaded and compared with the measured originals:
track geometry, net names, pads, vias, filled zones and board outlines are
identical. Only drawing-layer annotations were added. Native file hashes are
listed in `native-review.json`; original PCB and schematic hashes remain intact.

## Method and limits

The extractor reads KiCad objects directly. A centerline graph splits junctions,
crossings and overlaps, then measures the endpoint path rather than adding all
copper indiscriminately. All measured endpoints coincide with their pad centers
within the graph tolerance. Path and inventory lengths agree in this design;
the graph separately has regression tests for branched and multilayer examples.

Via barrels, solder laps, connector contacts and package paths are excluded.
USB measurements also exclude the component-internal bridge across each series
resistor. No electromagnetic solver, impedance calculation, eye diagram or
hardware test was run.

Reference screening samples the saved ground fill at no more than 0.05 mm
intervals. It checks In1 beneath rigid F/In2 routes and flex F beneath B routes.
An In1 signal on the head has no adjacent continuous GND plane in this model.
Filled-polygon coverage does not evaluate the width or connectivity of the
entire return-current corridor. A nearby ground via is not by itself sufficient
proof of a sound transition. Pair proximity is a nearest-centerline geometry
screen, not a calculation of electromagnetic coupling.

## Reproduce

From the repository root, use KiCad's Python to run `audit_interconnect.py
--kind mipi`, then `audit_interconnect.py --kind usb`, and finally
`build_interconnect_review.py` in `designs/eye-camera-ov9281/`. The tools require
the exact source hashes selected by `routing-review.json`. Outputs are under
this audit directory; preserve this completed package before creating another
audit revision. Do not rerun the builder while editing its native copies.

Run `python -B -m unittest discover -s designs/eye-camera-ov9281 -p
test_interconnect_graph.py`, `python -B tools/check_references.py`, and
`python -B -m unittest discover -s tools -p test_references.py` for the graph
and bibliography checks. These checks support the audit method, not hardware
qualification.

The global electrical-qualification milestone remains open. The previous
FreeCAD R05 review still represents earlier copper and was not regenerated in
this read-only electrical audit.
