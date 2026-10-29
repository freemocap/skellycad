# Resume here — 2026-10-28

The current PCB routing review is **R09 data1p trial 03**. All five connections
in the approved session checklist are complete. Native checks report zero
unconnected items and zero DRC violations on the controller, head and flex.
`routing-review.json` records this PCB-only checkpoint and its hashes.

The [interconnect audit](audits/2026-10-28-interconnect/REPORT.md) is now complete.
All three MIPI pairs exceed the reviewed geometric matching budget; the USB
pair also needs closer pairing, matching and reference-plane repair. The audit
locates 21 findings and provides annotated native copies and a rendered review.
Copper is unchanged. Zero DRC violations did not establish high-speed quality.
See the [global roadmap and completed session](ROADMAP.md) and the proposed
[corrective worklist](audits/2026-10-28-interconnect/CORRECTIVE-CHECKLIST.md).

The last matched PCB/FreeCAD review remains **R09 DOVDD trial 09 / compact optics
R05**, recorded in `working-review.json`. Its copper exports were not regenerated
in this routing session. R08 remains the selected electrical baseline in
`controller-selection.json`. These are engineering drafts, not release designs.

## Native files

- Current KiCad head: `generated/ov9281-r09-data1p-03/head.kicad_pcb`.
- KiCad assembly overview: `generated/ov9281-r09-data1p-03/OV9281-P4-R09-assembly.kicad_pcb`.
  This combines three boards for inspection. Edit the separate controller,
  head and flex files in that directory, then rebuild the overview.
- FreeCAD: `generated/ov9281-compact-optics-r05/OV9281-COMPACT-OPTICS-R05.FCStd`.
  It uses the older DOVDD trial 09 substrate and copper exports. The dark cylinder is
  the CH2021A dimension envelope; the translucent shroud is our proposed holder.
  Orange solids reserve component space, and purple reserves filter space.
  These are explicitly labeled assumptions, not manufacturer component bodies.
- The complete accepted Pupil mock-up is included as a hidden reference group.
  Its parts and optical datum remain together; its checkpoint hashes were checked.

Paths above are relative to the repository root. Generated working files are
local and ignored by Git. Current routing files and reports are preserved in
`checkpoints/2026-10-28-routing-complete/`; the previous matched PCB/FreeCAD files
remain in `checkpoints/2026-10-28-review-03/`. Earlier reviews remain in
`checkpoints/2026-10-28-review-02/` and `checkpoints/2026-10-28-review/`.
These are review snapshots, not release selections.

## Evidence

| Check | Result |
| --- | --- |
| R08 source hashes | Unchanged |
| R09 schematic-to-pad checks | 471 passed |
| Flex paths and assembled XY alignment | 24 each passed |
| Schematic ERC | Zero errors and warnings |
| Controller DRC | Zero unconnected and zero violations under the unchanged recorded rules |
| Head DRC | Zero unconnected items and zero violations, including dangling tracks |
| Flex DRC | Zero violations and unconnected items |
| Host protocol tests | 11 passed in the previous review; unchanged and not rerun in this routing session |
| Compiled sensor and synthetic firmware | Current implementation hashes match both saved build reports; neither executed on hardware |
| Compact holder geometry | One valid solid; no intersection with the modeled front component reservations after relief pockets |
| Lens travel | 0, 0.5 and 1.0 mm recomputed without lens/holder or lens/filter-reservation intersection |

The 8 mm square holder initially intersected D202's and Q201's reservations.
R03 removes a full-height corner for the LED and a lower pocket for the
transistor. Reservations use native courtyard XY plus assumed heights of 0.8 mm
for the sensor and 1.0 mm for other front components. Reliefs add 0.1 mm in XY.
Lens geometry follows the public 6 mm diameter, 2.65 mm length and 3.85 mm TTL
specification [@chuanganCh2021a].

R04 retains the R03 holder geometry and substitutes the repaired PCB copper.
Clearance repair moved connected track endpoints and vias together, preserving
footprints, nets and board rules. Six single-layer vias were removed; four
unfinished track ends remain visible in DRC. Two new supply paths connect
U1.D3 to C13.1 on DOVDD and U1.C5 to existing DVDD copper. The first adds a
0.4/0.2 mm via and a back-layer path; the second stays on the front. Both use
0.1 mm tracks and the existing 0.1 mm clearance rule. Source hashes, endpoint
changes and route geometry are recorded in the new snapshot.

R05 substitutes the checked DOVDD trial 09 copper while retaining the R04
mechanical dimensions. This trial connects U1.B7 to DOVDD on the front layer.
It replaces the obstructing DVDD segment with an escape from U1.D8 through a
0.4/0.2 mm via and a back-layer connection. Refilling the ground plane exposed
an isolated connection to U1.A7; an explicit back-layer ground bridge restores
it. Two obsolete DVDD stubs were removed after native DRC identified them.
All per-net pad groups are at least as connected as in clearance trial 06,
and component placement and native project rules are unchanged.

The approved routing session closed U1.E4 (SCL), E8 (VH), F7 (VN3), G4 (MIPI
clock P) and G5 (MIPI data 1 P). Each checked stage preserved every other net's
pad connectivity and the native project rules. The combined comparison against
DOVDD trial 09 also passes. The head retains 31 footprints and now has 62 vias.
The controller, flex and schematic native hashes are unchanged.

The final route required local changes to power, control and ground routing.
SCL, VH and data 1 P use In1, which also carries the ground pour. Ground regions
separated by these traces were reconnected with explicit tracks. DC connectivity
passes; ground return quality, differential impedance and pair delay remain
unqualified. Data 1 P and N use different paths and layers. Do not interpret the
zero-DRC result as a functional camera demonstration or a routing release.

Several dense passages meet the existing minimum spacing exactly. Passing DRC
does not establish fabrication yield, adequate power-track width or MIPI/USB
signal integrity. Existing signals on the ground layer still require review.

The lens image-plane Z remains an assumed 1.2 mm above PCB Z=0. The holder has
a smooth 6.05 mm bore representing space for an M6 interface; it is not a
finished threaded part. At 1 mm travel the axial overlap with the bore is
0.9 mm, not proof of adequate thread engagement. Mounting, filter retention,
light sealing, component heights, emitter clearance cones and tolerances remain
unfinished. No near-focus or 940 nm performance was established.

## Continue the engineering work

1. Preserve the completed routing checkpoint. Audit differential-pair routing,
   ground returns, power widths and the fabrication stackup before layout release.
2. Replace component-height reservations with verified package geometry, then
   finish holder attachment, thread engagement and filter retention. Keep
   [compact lens qualification limits](mechanics/compact-optics.md) visible.
3. Complete component purchasing data and electrical reference-circuit review.
   R09 replaces the inherited oscillator and adds a provisional LED driver;
   this does not qualify the entire circuit or illumination system.

Hardware-dependent validation remains real sensor capture, USB rate, electrical
measurements, near-IR imaging at the intended distance, mass, fit and exposure.

## Reproduce checks

Use the KiCad Python and FreeCAD runtime described in `docs/development.md`.
Before opening or modifying a working file, verify its hash against
`routing-review.json` for the current PCB or `working-review.json` for the older
matched mechanical review, or start a new revision from the appropriate frozen copy.

Run `validate_r09.py --directory generated/ov9281-r09-data1p-03` with KiCad Python
to regenerate native reports and the combined overview. The validator reports
remaining DRC violations; its successful exit does not mean fabrication-ready.
Do not run it while editing that overview in KiCad.

To reproduce the DOVDD routing change, run `reroute_head_dovdd.py` with KiCad
Python, `--source generated/ov9281-r09-clearance-06`, and `--output` pointing to
a new directory. It records the removed and added copper, refills the plane,
and checks that native DRC has one fewer gap and the same four warnings.
Then run `validate_r09.py` against that new directory for schematic, placement,
flex and per-net checks. The routing script's success alone does not replace
those checks.

The mechanical build uses `export_r06_review.py --revision R09`,
`export_head_interfaces.py` and `build_compact_optics.py`. Each output directory
or interface file must be new. Open the result with `open_compact_review.FCMacro`
through the existing FreeCAD desktop workflow. The macro reads `working-review.json`.
Its saved hash changes when desktop styling is saved; refresh the working review
record after an intentional change, preserving the frozen snapshot. The review
macro updates that hash after saving its display styles.
