# Rat R27: ribbon-facing tapered socket join

Replaces R26's oval, flared terminal with a flat-faced arm that narrows continuously to a 2.6 by 1.6 mm tip. The broad-face orientation rotates smoothly toward the ribbon's terminal plane. The tip is embedded lower in the collar at 3.7 mm along its axis, removing the previous projecting shoulder. A 0.35 mm fillet blends the underside of the socket connection.

The section has 0.2 mm corner chamfers. The tray root is 4.4 mm wide, shifted 0.98 mm along the tray to avoid the existing stepped edge, and retains a 0.4 mm underside fillet. The arm remains one broad continuous curve behind the ribbon. Camera pose, ribbon, holder, optical axis, baseplate and anatomy are unchanged.

The finished carrier is one valid solid. Static solid checks show no overlap with the ribbon, holder, sensor PCB or lens; matched-part checks pass. Carrier and ribbon exports are closed without detected self-intersections at the recorded export settings. No skull surface crossing or sampled eye-envelope containment was detected. Physical fit, strength and full adjustment travel remain unverified.

## Rebuild and review

Run `build.py`, `check.py` and `check_interfaces.py` with the pinned FreeCAD Python runtime from the repository root. Run `check_containment.py` with `tools/cad/.venv/Scripts/python.exe`. Outputs are in `generated/eye-tracker/rat/aligned-tip-r27/`.

Submit `open.FCMacro` to the verified existing FreeCAD PID following `docs/development.md`. The document is **Rat R27 - ribbon-facing tapered socket join**. `detail.FCMacro` captures the socket from behind and restores the overall view. The frozen complete assembly and its hash are in `review.json`. Prior checkpoints and the selected species manifest are preserved.
