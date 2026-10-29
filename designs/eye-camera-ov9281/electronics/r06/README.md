# R06 power and ground routing

R06 adds saved copper to the R05 controller, sensor head and flex. It is a
checked routing draft, **not a fabrication release or a demonstrated camera**.
Open `controller.kicad_pcb` to inspect the power work, `head.kicad_pcb` for the
sensor, or `assembly-interconnect-study.kicad_pcb` for the flat assembly.
The combined assembly file is for inspection only; manufacture would use
three separate board definitions after the remaining engineering is complete.

## What changed

- Added 199 through vias and verified 219 component-pad-to-via paths.
- Added ground planes on the second copper layer of both rigid boards.
  All 75 controller ground pads join one electrical group. On the head,
  32 of 40 ground pads connect; eight sensor ground pads remain unconnected.
- Added 44 power branches: 37 on the third copper layer and seven on the back.
  Backside bridges join the controller's split 3.3 V fill. Of its 44 supply
  pads, 39 now connect together; five remain isolated.
- Added a continuous front-side ground plane and 18 vias to the flex.
  All 24 end-to-end conductors and all 18 ground contacts pass connectivity
  checks. Connector fingers remain exposed on the back.
- Defined provisional layer thicknesses in the native boards: 0.60 mm rigid
  and 0.10 mm flex for copper plus dielectric. These are design assumptions,
  not supplier-approved stackups. Mask, coverlay and adhesive remain additional.

The four-layer strategy follows Espressif's guidance: ground on layer 2 and
power on layer 3. The candidate inner core-supply and USB-input routes use
0.508 mm and 0.635 mm widths respectively. Other power routes use 0.254 mm.
The local surface escapes are still 0.15 mm; this does not establish compliance
with the recommended power widths, current capacity or decoupling-loop layout
[@esp32P4PcbLayout]. Circuit topology and supply sequencing still need review.

## Checks on the saved files

| KiCad unconnected items | R05 | R06 |
| --- | ---: | ---: |
| Controller | 195 | 54 |
| Sensor head | 93 | 47 |
| Flex | 8 | 0 |

These counts measure missing physical connections, not percentage completion.
There are no short-circuit or clearance violations under the inherited draft
rules. R06 still reports six open camera tracks and nine vias connected on only
one layer. These are unfinished routes, so this is **not a clean fabrication DRC**.
Schematic ERC reports zero violations under the inherited project settings;
ignored categories are visible in `checks/erc.rpt`.

`validation.json` records native-file hashes, 456 schematic-to-pad net checks,
24 assembled pin-alignment checks, retained R05 geometry and copper, and native
KiCad connectivity groups for every net. A one-pad net is trivially connected
on that board; it does not prove an external connection or a working function.
Filled region counts are geometry counts; physical copper connectivity is
checked separately, including the bridges between 3.3 V regions.

`power-routing.json` records each added escape and power route. It lists 33
pads without an escape and ten attempted power branches left unrouted. These
are diagnostic subsets of the DRC findings, not additional totals to add to
the table. Surface paths use straight or single-bend candidates; power paths
use collision-checked grid searches. Failure means the search did not find a
path, not that the circuit is impossible to route.

## What still separates this from a working camera

Complete the dense sensor/processor escapes, power circuits and camera/control
signal routes. Review placement and the fabrication process before changing
clearances or introducing finer vias. The 0.45 mm via lands and 0.20 mm drills
are provisional; this revision avoids via-in-pad. The small existing package
lands still require process review [@jlcThinPcbCapabilities].

The flex's solid plane changes its stiffness and transmission-line geometry.
No controlled impedance, supply-drop, thermal, flex-life or optical performance
is established. The wider R05 interface, 76 mm flat length, connector stiffener,
solder joint and strain relief also remain unfinished. Optics, IR illumination
and end-to-end capture firmware are separate unfinished parts of this camera.

Review scope, 2026-10-27: Espressif power and layer guidance, local native KiCad
DRC/ERC, filled-zone connectivity and retained R05 interface geometry. No
hardware, signal-integrity, optical or thermal measurements were performed.

## Reproduce and inspect

From the repository root, use KiCad 10's bundled Python to run
`designs/eye-camera-ov9281/build_r06.py --output generated/ov9281-r06-rebuild`.
Choose a new output directory; the builder refuses to replace one. Then run
`designs/eye-camera-ov9281/validate_r06.py --directory generated/ov9281-r06-rebuild`
with the same interpreter. The validator must finish successfully; inspect its
remaining unconnected items rather than treating success as release approval.

For a new FreeCAD review, run
`python designs/eye-camera-ov9281/export_r06_review.py --output generated/ov9281-r06-review-2`
from the repository root using ordinary Python. Choose another new output path
if that directory already exists. The script verifies the saved R06 hashes, exports
actual PCB solids and prepares `open-review.FCMacro`. Follow
`docs/development.md` to send that macro to the verified existing FreeCAD process.
It preserves open documents and saves a separate R06 FCStd. The review contains
substrates and copper, including internal layers; component bodies and optics
are absent. Its flex height is for viewing, not a validated mating height.
