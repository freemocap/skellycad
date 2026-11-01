# Three-board architecture A01

Architecture review, 2026-10-29. R11 remains the preserved working candidate; A01 is a separate study, not its replacement or a manufacturing release.

## Recommendation

Proceed to detailed design of **OV9281 -> DS90UB953 -> shielded differential tether -> DS90UB954 -> ESP32-P4 -> USB** as a conditional candidate. Move the processor and frame buffers to the base station. Keep the serializer and local supplies on the head-mounted interface board. The serializer transports raw pixels; it does not need to compress JPEG [@ti953A01; @ti954A01].

Use the FR4-backed, one-sided placement as the initial mass allocation. Keep the thin-steel variant for mechanical comparison. Their stiffness, heat spreading and retention have not been established. This does not identify the material in the photographed Pupil Labs hardware.

The primary recording target is **640 x 400 RAW8 at 100 fps**, with 120 fps as a stretch target. Both require continuous capture and USB qualification. No frame rate or latency has been demonstrated. The full-resolution 1280 x 800 at 120 fps case exceeds USB2's raw capacity before overhead. See [system budgets](BUDGETS.md).

## Review files

- Open [the rendered review](index.html) through the repository HTTP server. It links native CAD, PDF architecture sheets, source records and validation results.
- `generated/three-board-a01/THREE-BOARD-A01.FCStd` is the complete FR4-backed placement assembly plus the base station.
- `generated/three-board-a01/THREE-BOARD-A01-STEEL.FCStd` is the matched steel-backed alternative. Keep its parts together; do not mix supports from the two files.
- Four `.kicad_sch` files in that generated directory are native KiCad functional architecture diagrams. They contain no electrically connected symbol pins. They are not pin-level schematics and have no ERC or DRC clearance claim.
- `placement.json` is the common dimensional source for FreeCAD and the placement diagram. It identifies selected package bodies separately from unqualified allocations.

## Size and mass comparison

All dimensions are millimetres. All masses below are estimates, not measurements.

| Property | Preserved R11 | Three-board A01 |
| --- | --- | --- |
| Head | 14 x 14 | 14 x 10 |
| Head-mounted electronics island | 28 x 14, processor present | 18 x 10, serializer and supplies |
| Local free flex | 32.85 x 8 | 25 x 5.5 |
| Flat head-mounted span | 74.85 | 57 |
| Separate base station | None in that module | 40 x 30 x 0.8 board allocation |
| Nominal head assembly mass | 1.343 g | 0.871 g FR4 / 0.929 g steel |
| Scenario range | 0.922-1.927 g | 0.645-1.192 g FR4 / 0.703-1.250 g steel |

R11 values come from its saved mechanical and mass records. A01's changed assumptions are recorded in `calculate.py` and `budgets.json`; the estimates are not interchangeable confidence intervals. The nominal FR4 estimate is about 35% below R11, but both A01 high scenarios exceed one gram. The target is plausible, not secured.

The one-gram target includes both head-mounted islands, local flex, populated parts, optics, filter, backing, adhesives, connector and a mounting/strain-relief allowance. It excludes the external tether and base. The 3-7 g base allocation excludes its enclosure and backpack fixtures. A mouse would carry only the camera assembly and tether load; a backpack configuration must account for those additional carried masses.

The retained 0.303 mm component-region and 0.166 mm flex stack envelopes are conservative starting assumptions from R11. A01 does not claim a manufacturer-approved new stack. Additional 0.10 mm FR4 or 0.05 mm steel backing is modeled with its adhesive. Thin-board rigidity and bend life require separate qualification.

## What is represented physically

The camera head places two LED body envelopes on opposite sides of the provisional lens along the long axis. The smallest passive body allocations are 0.6 x 0.3 mm (0201); some head capacitors are 1.0 x 0.5 mm (0402). These are body reserves, not a finalized capacitor selection: required capacitance, voltage bias, current, pad size, assembly tolerance and availability can force growth.

The lens reserve has an 8 x 8 mm holder and a 6 mm barrel diameter. It is not an identified lens, a working thread, or a close-focus optical prescription. Maintain visible rejection, near-IR transmission and focus checks at 10, 15 and 20 mm. Do not substitute an IR-cut lens or silently accept a cropped image circle.

The local flex is a continuous substrate envelope with **no routed copper**. Its lack of serpentine traces is not a routing optimization result. The blue connection to the base is a diagram line, not the physical length or diameter of the 30/60 cm tether. No anatomical mount or demonstrated physical fit is included.

## Holds before a build order

| ID | Unresolved issue | Required exit evidence |
| --- | --- | --- |
| S1 | OV09281-H64A supply conflicts | Traceable, orderable exact part, correct package and lifecycle confirmation from public supplier evidence; otherwise an explicit sensor redesign |
| S2 | Exact P4 supply/revision | Orderable package and silicon revision compatible with the chosen SDK |
| L1 | 36 AWG tether and tiny connector | Qualified differential channel including shield, terminations, bend radius, voltage drop and strain; an arbitrary four-pin JST is not sufficient |
| F1 | Capture and control chain | Resolved sensor clock metadata, audited register sequence, error counters and sustained continuous USB measurements |
| O1 | Optics and retention | Actual lens/filter/holder specifications, verified near-IR focus and image coverage, realistic retained mass |
| T1 | Local heat and illumination | Bench surface-temperature measurements and appropriate exposure assessment for the intended geometry; LEDs default off |
| M1 | Placement versus finished electronics | Pin-complete schematics, qualified BOM/footprints, stack/impedance review, routed boards and manufacturing checks |

Supply evidence and the scope of technical-source review are recorded in [COMPONENT-CHAIN.md](COMPONENT-CHAIN.md). No parts were purchased or reserved. Publicly accessible documentation does not remove its license conditions.

## Next detailed-design phase

The next deliverable should be a **pin-complete design and a bench qualification plan**, not another cosmetic shrink. Work in this order:

1. Resolve the exact sensor and P4 package/revision sourcing gates; retain A01 as conditional until they pass.
2. Audit the 953/954 clocks, RAW8 forwarding, reset, remote control, protection and power sequencing; convert the four architecture sheets to real electrical schematics with named pins and qualified footprints.
3. Select the actual cable and connector, including the TI differential termination/coupling circuit, shield connections, current limiting and strain relief. Verify the full channel rather than relying on wire gauge alone.
4. Establish a reproducible firmware path: synthetic USB stream, receiver test pattern, sensor snapshots, then continuous sensor recording. Include frame counters, timestamps, dropped-frame reporting and disconnect recovery. This sequencing is a plan, not code already delivered.
5. Qualify optics and update the mass ledger with actual package/assembly data. Route the head and interface with the minimum required layer count and manufacturer-supported stack. Recheck mass, heating, bending and assembly access before ordering.

Computer work can complete the schematics, footprints, firmware build, analytical checks and fabrication package. It cannot demonstrate real link errors, sustained camera capture, thermal contact conditions, close focus or final weight without physical hardware. Keep each untested property explicit.

## Reproduction and review scope

From the repository root, run `python designs/eye-camera-ov9281/architecture/three-board-r01/calculate.py`, then `build_layout.py` in that same directory. Run `build_cad.py` with the pinned FreeCAD Python identified in `tools/cad/toolchain.json`, in an isolated process. Close the A01 review documents before rebuilding their physical paths; never rebuild R11 from these scripts.

After generation, run `python designs/eye-camera-ov9281/architecture/three-board-r01/validate_package.py`, `python -B tools/check_references.py` and `python -B -m unittest discover -s tools -p test_references.py -v`. The package validator checks preserved baseline hashes, generated-file lineage, shape-report scope, budgets and local review links. It does not perform ERC, DRC, circuit simulation or physical testing.

This review covers manufacturer interface/package excerpts, supplier listing observations, prior R11 records, analytical budgets and envelope geometry. See `review-validation.json` for machine-readable results. R11's `working-review.json` selection remains unchanged.
