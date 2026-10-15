# Rat R25: leading-edge arm connection

Moves the R24 arm root into the PCB tray leading edge beside the ribbon exit. The root widens to 6 mm, then tapers smoothly to the existing 2.6 mm socket attachment. A 0.4 mm fillet fills the underside junction. The carrier is fused into one valid solid; the PCB remains a separate part.

The arm-to-tray overlap before finishing increases from 1.004 to 9.005 cubic millimetres. A 1.4 by 4.5 by 3.2 mm relief box preserves the ribbon exit. The finished carrier has no ribbon overlap and a minimum 0.100 mm static ribbon gap at the attachment region. This gap is not a demonstrated motion clearance or manufacturing allowance. Full adjustment travel and physical fit remain unverified.

Camera, ribbon, holder, optical datum, skull, eyes and baseplate are unchanged from the hash-verified R24 complete assembly. Matched-part checks pass. Carrier, arm and ribbon meshes are closed without detected self-intersections. The new carrier has no skull surface crossing, and sampled changed-part points remain outside both eye envelopes.

## Rebuild and review

Run `build.py`, `check.py` and `check_interfaces.py` with the pinned FreeCAD Python runtime from the repository root. Run `check_containment.py` with `tools/cad/.venv/Scripts/python.exe`. Outputs go to `generated/eye-tracker/rat/joined-arm-r25/`.

Follow `docs/development.md` to send `open.FCMacro` to the verified existing FreeCAD PID. The document is **Rat R25 - blended leading-edge arm**. See `review.json` for the frozen complete assembly and hash. This review candidate does not replace the selected species checkpoint or establish a print release.
