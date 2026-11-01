# Ribbon-driven eye and world camera placement

R02 replaces the rejected R01 arbitrary placements and route sketches. The
world camera position and roll derive from the rear board's fixed ribbon exit,
using the existing 32.85 × 4 × 0.25 mm cylindrical-bend ribbon model. Forward aim
is constrained to skull-world +X. Camera translation and roll remain free in
the search, within a broad region in front of the carrier. Soft preferences
favor low bend obliquity and compact placement; no camera position is prescribed.

The hash-verified R43 complete assembly supplies the anatomy, boards and camera
geometry. The right-eye camera and its ribbon remain unchanged. The displayed
carrier combines the original central stock and finished right-side supports.
The binocular branch and historical species selection are unchanged.

The accepted geometric candidate has its lens at approximately
(11.1024, 1.9590, 15.8268) mm in skull coordinates. Its sensor long edge is about
3.5 degrees from horizontal. The minimum modeled inside bend radius is 3.76 mm.
The ribbon uses cylindrical bends; it is not a force, strain or fatigue model.

## Checks and limits

The finite-thickness ribbon is a valid closed solid with no mesh
self-intersections. Its mapped length and shear errors are below 1e-5.
Full-solid intersections were checked against the retained carrier, baseplate,
both main PCBs, right-eye hardware, and the world sensor, lens and LEDs. A
candidate with a small carrier intersection was rejected before selecting this
one. The new camera and ribbon have no detected crossings of the dense skull.

The inherited right-eye viewing region and a provisional forward cone are clear
of the modeled hardware and ribbon. The forward cone is an obstruction check,
not a calibrated field of view. Containment within anatomy, physical handling,
optical focus, adjustment range and mechanical strength are not demonstrated.

The real holder, clip and socket are retained as hidden transformed references.
The existing back-mounted stem and socket intersect the fixed boards/carrier;
their collisions are recorded in `selected-validation.json`. They are not shown
as finished hardware. No substitute cylinder or guessed housing is used.

First review the ribbon-driven placement. Then refit the existing holder's stem,
socket and two support attachments around that pose and rerun all clearances.
This document is a camera/ribbon configuration study, not a printable assembly.

## Reproduce and open

Run `search.py` with tooling Python, then `validate.py` with pinned FreeCAD
Python. Validation must pass before building. Run `build-isolated.FCMacro` in a
separate native FreeCAD process; never send that build macro to the desktop
session. It saves, verifies and closes its own document. `review.json` identifies
the saved native checkpoint and hash after the GUI save.

Send `open.FCMacro` through the verified existing-session IPC bridge for desktop
review. It saves and closes only this fork's obsolete review tabs and preserves
unrelated binocular work.
