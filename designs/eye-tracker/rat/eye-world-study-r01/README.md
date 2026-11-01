# Rat eye and world camera: concept fork

This independent study forks the hash-verified R43 complete assembly. It keeps
the right-eye camera, back-to-back main PCBs, skull and baseplate. The left-eye
camera becomes a world camera pointing straight ahead along skull-world +X.
The binocular branch and species selection are unchanged.

The proposed world holder has a stem rising from the tray's top, with a vertical
socket above it. The camera hangs below the socket in front of the PCB carrier.
The socket, tray and support directions are simplified envelopes. They are not
matched printable parts. The removed left-eye supports remain hidden in the
source assembly for reference; the displayed carrier combines the central stock with the finished right half. The right-eye supports retain their finished source geometry.

## Placement comparison

All dimensions use millimetres in the aligned skull frame: +X forward, +Y left,
+Z up. Both candidates aim along +X, as requested.

| Candidate | Lens position X, Y, Z | Question |
| --- | --- | --- |
| A: centered | 12, 0, 12 | Can the rear ribbon reach the center without an awkward fold? |
| B: offset | 12, 10, 12 | Does staying nearer the ribbon exit provide an easier route? |

The yellow line is a route hypothesis, not a finite-width ribbon simulation.
Its length is reported in `study.json` against the inherited 32.85 mm stock.
Neither endpoint orientation, bend radius, ribbon collision nor strain has
been accepted. Do not print these documents or treat the line as a solved fold.
World-camera optical coverage and focus are also unverified.

## Next decisions

First review the hanging-camera arrangement and lateral position. Then solve
the ribbon with fixed endpoint frames, its existing length and a minimum
3.5 mm inside bend radius. Camera roll may change while forward aim is retained.
Use the feasible route to design the tray, vertical socket, two attachments and
ribbon protection. Validate view clearance, adjustment access, joints and
anatomy separately before producing a matched print pack.

## Files and isolation

Outputs are in `generated/eye-tracker/rat/eye-world-study-r01/`. `study.json`
records source identity, candidate native paths and hashes. The species
`active-model.json` still selects historical R01; its previously recorded hash
mismatch is not used as the source of this fork.

`build-isolated.FCMacro` runs `build.py` in a separate native FreeCAD process.
It saves and closes its own documents without controlling an existing desktop
session. Do not send this build macro to the shared review session. Native
documents pass ZIP integrity checks; those checks do not establish physical fit.

The first route sketches measure 41.4 mm for A and 30.7 mm for B. A exceeds
the ribbon stock length as drawn. B fits the length budget only; neither route
resolves the endpoint frames or finite-width folds. B is the next routing study
candidate, not an accepted mechanical solution.
