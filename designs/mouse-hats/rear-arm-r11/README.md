# R11 - five lower-left socket departure options

**Selected: R11B (B as in Buffalo), 2026-10-10.** Use B for subsequent design work. See `selection.json` for exact files and print-file hash. Other variants remain references.

User requested more than three variations around a 7:30 socket attachment,
softer bends, and differing return curves to select a subset for printing.
All five retain R10's centered 3 mm PCB root, quick taper to 2.6 mm body, no extra
band, R0.2 lower-root blend, R0.5 upper-root blend, and existing ball/socket fit.

| Option | Approximate clock position | Straight departure | Loop style |
|---|---|---|---|
| A | 7:50 (35 degrees from nine) | 2.5 mm | balanced |
| B | 7:30 (45 degrees) | 2.5 mm | balanced |
| C | 7:40 (40 degrees) | 2.5 mm | intermediate angle |
| D | 7:30 (45 degrees) | 1.5 mm | broader loop, earlier turn |
| E | 7:30 (45 degrees) | 3.5 mm | longer departure, more level return |

Clock labels approximate the supplied view; numeric angles rotate around the
socket axis. A/B/C use OuterBulge3.25 and ReturnLevelBlend0.5. D uses3.75/0.35;
E uses3.0/0.65. Blend0 means old low-loop control heights; Blend1 means R10's level
return. The 0.35-0.65 choices split the difference without copying mesh wiggles.

A steeper55/50-degree trial failed deep loft checks and is not exported. Final
section counts/loft interpolation degrees are recorded per option in settings:
A49/5, B41/5, C41/3, D49/5, E33/5. These interpolation choices passed isolated
arm checks; full-carrier/export checks are required too. Geometry validity does
not guarantee flexible ribbon clearance, stiffness, or the print-in-place fit.

Output directory: generated/mouse-hats/rear-arm-r11/ relative to playground.
- R11A/B/C/D/E-carrier-and-holder.stl: separate, two-shell print-in-place candidates.
- r11a/b/c/d/e-carrier.FCStd: source-backed carriers.
- r11a/b/c/d/e-assembly.FCStd: assembled five-part snapshots.
- five-arm-options.FCStd: labeled comparison only; offsets are display-only.
- validation.json and mesh-validation.json: measured checks.

Print chosen STL files as complete objects; do not rearrange holder separately
from carrier. Each file uses the same native origin. Accessories are unchanged.
Pinned FreeCAD Python runs build.py and verify_export.py. show.py runs in GUI.
settings.json stores units, control points and per-option overrides; build merges
those overrides into each native feature's SweepJSON and dimensional properties.
Prior candidates are retained. No printer submission or commit.

All five completed carrier builds pass deep checks with one solid. Carrier volumes
(mm3): A1236.257152, B1240.489782, C1238.437618, D1241.503131, E1242.262956.
The guide control families are intentionally close; compare B versus D/E for
return-curve differences and A/C versus B for socket angle differences.
The comparison has A/B/C across its top row and D/E below, with color labels.
Use separate STL links to select any subset. Printed ribbon behavior remains
unverified for every R11 option.

All five final assembly checks retain 0.331721863 mm minimum joint gap, zero
holder/baseplate overlap, unchanged inherited cap contact0.001611788 mm3, and
contained top/tray boundary samples. Individual mesh results are in mesh-validation.json.
