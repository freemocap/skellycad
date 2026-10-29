# R07 sensor escapes and surface connections

R07 adds **35 verified electrical paths** to R06: 17 on the controller and
18 on the sensor head. All 75 controller ground pads and all 40 head ground
pads now connect on their respective boards. The flex's 18 ground contacts
remain joined. This is a checked routing draft, not a working camera or a
fabrication release.

Open `OV9281-P4-R07-assembly.kicad_pcb` for the actual combined copper view.
It is an inspection assembly of three separate boards, not one fabrication
file. The editable individual boards are `controller.kicad_pcb`,
`head.kicad_pcb` and `flex-study.kicad_pcb`.

## Added copper and process assumptions

New routes join local supply, regulator feedback/enable, reset, boot and
control connections. A flash chip-select branch is also connected; the flash
interface as a whole remains unfinished. The head gains control and supply
connections plus ten narrow sensor escapes: six ground and four digital-supply
paths. Existing components, pads, tracks, vias and the schematic are preserved.
No MIPI or USB differential-pair routes were added.

The sensor footprint has 64 circular 0.20 mm lands at 0.64 × 0.50 mm pitch.
An ordinary 0.15 mm trace with 0.15 mm clearance on each side needs a
0.45 mm channel. The gaps between adjacent lands are only 0.44 and 0.30 mm.
These measurements come from the saved footprint. The narrower fan-out uses
0.10 mm traces while retaining the 0.15 mm spacing rule. Each new narrow path
is at most 4 mm long and lies within x = 3.3–10.8 mm, y = 2.75–9.25 mm in the
head's native coordinates. It introduces no new vias or via-in-pad.

JLCPCB's published 1 oz trace capabilities support considering this trace size;
they do not approve the complete land pattern, stackup or assembly. Existing
0.20 mm package lands still need process review [@jlcThinPcbCapabilities]. The
head's native minimum track width changes from 0.15 to 0.10 mm; the validator
separately checks that this revision's narrow additions stay inside the stated
fan-out area. Minimum copper spacing remains 0.15 mm on both rigid boards.

Longer added power routes use the inherited width targets: 0.635 mm USB input,
0.508 mm core supply and 0.254 mm other supply routes. Short local supply
connections may use 0.15 mm for at most 1.5 mm. These are draft geometry choices;
current capacity, feedback noise, decoupling and clock/flash timing remain
unqualified [@esp32P4PcbLayout]. R06's earlier narrow power escapes remain.

## Saved-file validation

| KiCad unconnected items | R06 | R07 |
| --- | ---: | ---: |
| Controller | 54 | 37 |
| Sensor head | 47 | 29 |
| Flex | 0 | 0 |

No short, clearance or copper-sliver violations remain under the recorded
draft rules. Six open camera tracks and seven incomplete vias still produce
warnings. The 66 unconnected items mean fabrication DRC is not clean.
Schematic ERC reports zero errors and warnings under the inherited settings;
ignored categories are listed in `checks/erc.rpt`.

`validation.json` records the native file hashes, rule snapshots, all 456
schematic-to-pad net checks, 24 matched flex interfaces, all 35 added paths,
and native KiCad connected groups for every net. No net loses connectivity.
The actual added track segments match `surface-routing.json` exactly. The
inherited `power-routing.json` remains the R06 routing record, not a current
list of missing connections.

Still unfinished: remaining supply and control connections, complete flash and
MIPI routing, supply sequencing review, impedance/thermal/current analysis,
optics, illumination and capture firmware. The dimensions and mechanical
limitations recorded in R06 remain. Ground continuity does not establish
high-frequency return-path performance or a working camera.

## Reproduce

From the repository root, using KiCad 10's bundled Python:

```powershell
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/build_r07.py --output generated/ov9281-r07-rebuild
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/validate_r06.py --directory generated/ov9281-r07-rebuild --parent designs/eye-camera-ov9281/electronics/r06 --revision OV9281-P4-R07
```

Choose a new output path if that directory exists. The validator must finish
successfully; then inspect its remaining connections and warnings.
The shared validator retains its R06 filename and accepts explicit lineage.

For a fresh FreeCAD export, use ordinary Python:

```powershell
python designs/eye-camera-ov9281/export_r06_review.py --directory designs/eye-camera-ov9281/electronics/r07 --revision R07 --output generated/ov9281-r07-review-2
```

Choose a new review directory, then follow `docs/development.md` to send its
`open-review.FCMacro` to the verified existing FreeCAD process. It preserves
open documents and saves a separate R07 FCStd. The review contains actual PCB
substrates and copper; component bodies, optics and qualified mating heights
remain absent.

Review scope, 2026-10-27: native geometry, DRC/ERC, saved connectivity and the
manufacturer's public trace-capability table. No physical measurements or
electrical, optical or thermal simulation results are claimed.
