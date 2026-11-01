# Rat R24: smooth single arm

Replaces R23's ribbon-offset arm and short terminal links with one continuous cubic curve from the embedded PCB-tray root to the socket collar. The broad sweep follows the ribbon's general route with a smooth width taper from 4 to 2.6 mm and 1.8 mm thickness. The arm no longer copies the ribbon's local twist or uses a separate elbow.

Camera, ribbon, optical datum, baseplate and anatomy remain unchanged from the hash-verified R23 complete assembly. The new arm has no solid overlap with the ribbon, holder, clip, PCB or lens; its minimum ribbon clearance is 0.741 mm. This minimum includes the attachment region and does not imply uniform clearance along the sweep. Full joint travel and physical ribbon manipulability have not been established.

The finished carrier is one valid solid. Carrier, ribbon and arm exports are closed without detected self-intersections. Matched-part checks pass, with no skull surface crossings and no sampled points inside either eye envelope. See the validation records for scope. Physical fit remains unverified; this is a review candidate, not a print release.

## Rebuild and review

From the repository root, run this directory's `build.py`, `check.py` and `check_interfaces.py` with the pinned FreeCAD Python runtime. Run `check_containment.py` with `tools/cad/.venv/Scripts/python.exe`. Outputs go to `generated/eye-tracker/rat/smooth-arm-r24/`.

Follow `docs/development.md` to submit `open.FCMacro` to the freshly verified existing FreeCAD PID. The review document is **Rat R24 - smooth single arm**. `review.json` identifies the frozen complete assembly and its SHA-256; prior checkpoints and the selected species manifest remain unchanged.
