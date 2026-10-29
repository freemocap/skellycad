# Size and mass targets

The approved target is **below 1.000 g for the complete camera module, excluding
its external tether**. Count both boards, inter-board flex, all electronics,
optics, LEDs, board-side connectors, solder, adhesives and module-side retention.
Report cable and cable-side connector mass separately versus length. External
mounting hardware is separate. Do not meet the target by moving the P4 off-module.
The user-reported Pupil mass is approximately 0.7 g; its weighing boundary is
unconfirmed.

The user-confirmed caliper study records 30.85 x 9 mm controller, 32.85 x 4 mm
free ribbon, and a 15 x 6 mm notched head including the LED section. Its straight
outline is 78.70 mm. R10 is 32 x 20, 35.3 x 12.5 and 14 x 14 mm respectively.
The 10 x 10 mm P4 package prevents directly matching a 9 mm controller width
without an architectural change [@esp32P4Datasheet].

The remembered electronics blocks are located in
`generated/eye-tracker/shared/camera-interlock-075-r04/` and its R05 connections
and R06 appearance derivatives. `tools/cad/add_camera_board_chips_r04.py` defines
six chip envelopes using approximate photo proportions. The recorded photo is
`codex-clipboard-926b0153-6802-4198-949a-ce155ceaf8a5.png`. The source explicitly
labels these as cosmetic, uncalibrated geometry. Preserve that limitation.
`pupil-electronics-envelopes.json` captures their dimensions and evidence.

CAMERA-DUMMY-R08 remains the accepted complete comparison assembly; its native
and material-part hashes were checked. The chip-print study is a supplemental
appearance reference, not a replacement selection. Printed materials and 0.75 mm
print thickness are not physical camera mass inputs.

Performance comparison goals are global-shutter capture at 400 x 400 / 120 fps
and 192 x 192 / 200 fps [@pupilCore200Hz]. Review scope: the manufacturer's 2017
announcement, feature list, checked 2026-10-28. These are comparison modes, not
claims of OV9281/P4 throughput. Preserve the existing near-IR and approximately
10–20 mm working-distance intent; optics, latency, power, temperature and image
quality remain unqualified.
