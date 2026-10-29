# Starter enclosure cube R01

R01 is a freestanding frame concept for the tethered mouse and rat eye-tracker
workspace. The frame opening is **500 × 500 × 500 mm**, measured between the
inside faces of the perimeter members. The outside frame is **540 × 540 ×
540 mm**. Brackets and camera mounts project into the opening. This is a new
design; it does not modify or select a species checkpoint or its matched parts.

The frame uses nominal 20 × 20 mm metric T-slot extrusion. The reference family
is 80/20 20-2020, which has four open slots and accepts that manufacturer's
20-series fasteners [@eightyTwentyProfile2020Enclosure]. The CAD slots, center bore,
brackets and camera adapters are illustrative geometry, not manufacturing
drawings or verified vendor interfaces. Select the extrusion, brackets and
slot hardware from one compatible family before ordering.

## Layout

- Four full-height uprights connect the top and bottom square frames.
- Eight horizontal rails fit between the uprights.
- One top crossbar spans between opposing top rails. Its underside carries a
  sliding plate, centered at x = y = 270 mm in this revision.
- Four short camera arms attach to the inward-facing slots of the uprights.
  Each plate uses two attachment points, 24 mm apart, to resist rotation.
  The illustrated arm centers are 320 mm above the frame bottom.
- A fifth camera faces downward from the top center. The plate can instead
  carry a compatible hang-point adapter. Simultaneous tether and camera mounting
  needs a separate attachment position and a cable-clearance review.

The blue camera bodies are generic environment-camera envelopes, not Pupil Labs
eye-camera geometry. Their axes indicate intended viewing directions only.
Camera models, sensor fields of view, focus distances, adapters and cable exits
are not specified. Corner cameras point toward (270, 270, 120) mm; the top camera
points vertically downward. The orange parts show mounting concepts.

## Preliminary parts plan

| Item | Quantity | Specification / status |
| --- | ---: | --- |
| Upright extrusion | 4 | 540 mm long, 20 × 20 mm |
| Perimeter rail extrusion | 8 | 500 mm long, 20 × 20 mm |
| Top crossbar extrusion | 1 | 500 mm long, 20 × 20 mm |
| Right-angle bracket kits | 18 | 16 rail-to-post joints and 2 crossbar joints; exact kit TBD |
| Bracket bolts and slot nuts | 36 of each | Allowance of 2 per illustrated bracket; reconcile with selected kit |
| Upright camera plates and short lockable heads | 4 sets | Actual camera attachment TBD |
| Top sliding plate and camera/hang adapter | 1 set | Actual payload attachment TBD |
| Mount plate bolts and slot nuts | 10 of each | 2 per plate; lengths and thread engagement TBD |

Total cut extrusion is **6.66 m**, before saw kerf and stock waste. As a supplier
price reference checked on 2026-10-29, the 80/20 page lists USD 0.0131/mm and a
USD 3.00 cut charge. Applying one charge to each of 13 pieces gives approximately
**USD 126.25 for cut extrusion alone** (USD 87.25 material plus USD 39.00 cuts).
This is an estimate, not a cart quote; hardware, mounts, shipping and tax are
excluded [@eightyTwentyProfile2020Enclosure]. No cheapest-supplier comparison was made.

If cost becomes the deciding constraint, a 300 mm clear cube would use four
340 mm uprights and nine 300 mm rails (4.06 m total). At the same illustrative
rate and cut-count assumption, extrusion would be about USD 92.19. R01 retains
the requested half-meter clear opening; the smaller variant has not been built.

## Scope and next decisions

This is an open frame, not an animal-containing enclosure. Floor, walls, door,
feet, lighting, tether routing and cleaning details remain to be designed.
Select the environment cameras and expected suspended mass before choosing
adapters or judging crossbar deflection. The bracket arrangement is a starting
point; joint stiffness, resistance to racking, and physical fit have not been
demonstrated. Additional gussets or panel bracing may be needed after reviewing
payload and handling requirements.

## Rebuild and inspect

Use the pinned FreeCAD Python runtime after completing the setup described in
`docs/development.md`. From the repository root, run:

```powershell
$env:FREECAD_USER_HOME = Join-Path (Get-Location) '.cad-tools/validation-profile'
& ./.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/enclosure/starter-cube-r01/build.py
```

The script saves the native model before export and writes these files under
`generated/enclosure/starter-cube-r01/`:

- `starter-cube-r01.FCStd`: grouped native solids with cut-length properties.
- `starter-cube-r01.step`: exchange geometry.
- `preview.png`: axonometric view.
- `validation.json`: dimensions, frame-interference checks, bracket contact
  checks, solid validity, reopen checks and native document SHA-256.

The rebuild replaces these generated R01 outputs. Preserve an accepted output
as a checkpoint and create a new revision before changing an accepted design.
The source script defines this concept; no accepted checkpoint is selected yet.
The script closes its own documents after saving and validating them. Geometric
contact checks establish intended placement, not fastener engagement or joint
strength. Successful ZIP checks establish file integrity, not physical fit.
