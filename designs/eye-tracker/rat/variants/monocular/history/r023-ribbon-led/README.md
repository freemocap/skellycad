# Rat R23: ribbon-led single support

R23 keeps the R21 level-camera pose, fits a smooth ribbon between its PCB endpoints, then derives one tapered support behind that ribbon. It replaces the rejected R22 independently routed support. The ribbon and support stay on consistent sides of one another. The PCB exit has a small rectangular clearance relief in the finished carrier.

The complete assembly retains the R16 skull, R14 eyes, R17 baseplate and R21 matched camera hardware and optical datum. The selected species checkpoint remains unchanged. See `review.json` for the frozen native checkpoint and hash, and `recipe.json` for the construction order and lineage.

## Validation

- Ribbon centerline: 32.85 mm; width 4 mm; thickness 0.25 mm.
- Minimum sampled centerline radius: 5.189 mm. This is not a measurement of the inside edge radius of the twisted sheet.
- Support: 4 mm root width tapering to 2.6 mm, 1.8 mm thick, offset 2.6 mm behind the ribbon face.
- Arm-to-ribbon gap: 1.074 mm; zero solid overlap. The finished carrier clears the ribbon after exit relief.
- Carrier is one valid solid. Carrier, arm and ribbon meshes are closed and have no detected self-intersections.
- Fixed parts and camera optical datum are unchanged from R21. Matched-part validation passes. The camera retains R21's 20.916 degree offset from the estimated neutral eye axis.
- No new carrier or ribbon surface crossings with the skull. All 1,800 sampled changed-part points lie outside both whole-eye envelopes. The open anatomical skull does not support a reliable volume-containment claim.

The endpoint frames still require distributed ribbon twist (about 153 degrees). The arm follows this twist on one side; it does not cross the ribbon. The ribbon is a smooth geometric approximation with constrained centerline length, not a physical minimum-energy or inextensible-sheet simulation. Physical routing, strain, strength and ball-joint travel need prototype review. This is not a print release.

## Rebuild and review

From the repository root, use the pinned FreeCAD Python executable to run `build.py`, `check.py` and `check_interfaces.py` in this directory. Run `check_containment.py` with `tools/cad/.venv/Scripts/python.exe`. Outputs go to `generated/eye-tracker/rat/ribbon-led-r23/`; the frozen checkpoint is not overwritten by these scripts.

Open `open.FCMacro` through `tools/cad/open_in_running.py` with the freshly verified existing FreeCAD PID, following `docs/development.md`. The macro reuses a document already open at that physical path. The native review is named **Rat R23 - ribbon-led single support**.
