# Rat R26: rounded arm and flared junctions

R26 replaces the rectangular arm section with a smooth oval section. The tray attachment flares to 6 mm, the span narrows toward 3.4 mm, and the socket attachment flares to 4.8 mm. Thickness increases from 1.8 mm along the span to 2.2 mm at the socket. Width changes are smooth along the existing broad curve.

A 0.5 mm root fillet blends the exposed underside and side transition into the tray. A 0.4 mm socket fillet blends the selected outer shoulder into the collar. These are native solid fillets, not display smoothing. Mating socket surfaces remain unchanged. The final geometry is one valid carrier solid; both attachment regions retain positive solid engagement before blending.

Camera, ribbon, optical datum, baseplate and anatomy remain unchanged from the hash-verified R25 complete assembly. Static solid checks show no collision with the ribbon, sensor PCB, holder or lens. Matched-part checks pass. No skull surface crossing was detected; 1,200 sampled points remain outside the eye envelopes. Full ball-joint travel and physical strength have not been tested.

The finished carrier and unchanged ribbon STL exports pass closure and self-intersection checks at 0.04 mm linear and 0.15 rad angular tessellation settings. Finer experimental tessellation produced local crossing triangles near curved seams; those experiments are not print exports. The embedded construction arm is not a standalone manufactured part and is not exported. Inspect a sliced prototype before treating this review as a print release.

## Rebuild and review

Run `build.py`, `check.py` and `check_interfaces.py` with the pinned FreeCAD Python runtime from the repository root. Run `check_containment.py` with `tools/cad/.venv/Scripts/python.exe`. Generated outputs are in `generated/eye-tracker/rat/blended-arm-r26/`.

Following `docs/development.md`, submit `open.FCMacro` to the verified existing FreeCAD PID. The document is **Rat R26 - rounded arm and blended junctions**. The frozen checkpoint and SHA-256 are recorded in `review.json`; the selected species checkpoint remains unchanged.
