# Three-board E01: connected electrical draft

E01 converts A01's architecture into two connected KiCad schematics and actual-footprint placement studies, with a matched complete FreeCAD assembly. The head and interface are two populated islands of one continuous flex assembly; the base is a separate PCB. All components are front-mounted. R11 and A01 are preserved.

Open `index.html` through the local review server. `review-manifest.json` identifies the exact matched native files and hashes. These files are an engineering draft, not an accepted production checkpoint.

## Results

| Item | E01 result |
| --- | --- |
| Head | 16 × 14 mm |
| Interface | 24 × 14 mm |
| Free flex | 25 × 5.5 mm; 0.166 mm thick |
| Complete flat head assembly | 65 mm span |
| Base | 34 × 26 mm; 0.4 mm board target |
| Complete head mass | 1.306 g nominal estimate, excluding tether; 0.959–1.785 g scenarios |
| Base electronics | 1.821 g nominal estimate |
| Complete backpack allocation | 3.639 g nominal including enclosure/mounts; no battery or external cable |
| Native files | 196 footprints; 190 fitted physical package envelopes, five PCB features and one DNP entry |
| Schematic checks | 595 intended pin connections match exported netlists; zero ERC violations |
| Electrical contracts | 420 automated checks pass |
| PCB checks | Zero placement DRC violations; 488 intentionally unrouted connections |
| Mechanical checks | Saved/reopened native assembly, ZIP integrity, valid shapes and no package/holder volume collisions |

**The under-one-gram target is not met by the nominal construction.** The low scenario is not a verified result. A01's package allowance was optimistic; the complete support circuits and actual footprints require more area and mass. The base is still designed for wearable use: its area is approximately 26% below A01's reservation and its nominal complete mass remains below the 5 g optimization goal.

The serializer manufacturer recommends at least a four-layer board with a dedicated ground plane. E01 retains that requirement instead of assuming a two-layer mass saving. The four-layer component regions retain the conservative A01/C stack and separate backing; the free flex carries only two copper layers, enforced by native inner-layer exclusions [@ti953A01].

The packing study reserves the optical holder and a CSI corridor, but does not establish a routable optimum. Bypass placement, power loops, clock proximity, return paths and bend-transition details must be refined during routing. Solder-land rectangles in FreeCAD display native pad positions; exact pad outlines remain in KiCad. Optics and package heights are reservations, not supplier STEP solids.

## Review records

- `CHECKLIST.md`: exact approved execution checklist and status.
- `COMPONENT-BASIS.md`: parts, documentation and supply holds.
- `ELECTRICAL-REVIEW.md`: corrected pin/package issues, startup contract and limits.
- `electrical-audit.json`: native checks and analytical budgets.
- `placement.json`, `mass-budget.json`: all dimensions, assumptions and mass scenarios.
- `bom.json`: every schematic entry and procurement status.
- `ROUTING-HANDOFF.md`: required next work and release holds.
- `review-manifest.json`: matched native files and hashes.

## Reproduce from the repository root

Use the installed KiCad 10 Python for `circuits.py`, `audit.py`, `place.py` and `review_pcb.py`; those scripts import `pcbnew`. Use ordinary Python for `budget.py` and `publish.py`. Run these in order:

1. Run `circuits.py`, then `circuits.py base` to generate the two schematics, libraries, netlists, PDFs and ERC reports.
2. Run `audit.py` to verify component-pad sets and electrical contracts.
3. Run `place.py`, then `review_pcb.py` to save the two PCB placement studies, their rule areas, native DRC results and SVG plots.
4. Run `budget.py` to recalculate the mass scenarios from the final placement and components.
5. Use the pinned FreeCAD Python runtime to run `build_cad.py` in its isolated hidden process. Require `generated/three-board-e01/cad-validation.json` to report success with matching hashes. The builder saves, closes, reopens, verifies and closes its documents.
6. Run `publish.py`, then `validate_package.py`, the repository bibliography checker and its tests. Run `review_html.cjs` with the bundled Node runtime while the repository preview server is available on port 8787.

The scripts overwrite only this working E01 package; copy it to a new revision before revising an accepted checkpoint. Read `docs/development.md` before native CAD work. Use `open-review.FCMacro` through the existing FreeCAD native CLI pipe for desktop review; preserve unrelated user documents.

The copied Antmicro and Espressif library notices remain alongside each native schematic. Public reference excerpts inform this draft; no vendor NDA material was used.
