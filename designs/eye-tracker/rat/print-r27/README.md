# RAT R27 print pack

This pack uses the approved ET-RAT-ALIGNED-TIP-R27 complete assembly. Print at 100% scale; all dimensions are millimetres. The anatomical reference remains unchanged. These are mesh-validated, unsliced print files, not G-code or a demonstrated physical fit.

## Main files

- `anatomy/RAT-R27-Snapmaker-U1.3mf`: open as a project in Snapmaker Orca. Contains the skull, connected eyes and attached baseplate as four material regions.
- `hardware/RAT-R27-carrier-and-holder.stl`: print-in-place candidate with the carrier and matching movable holder in their existing relative pose. The back of the carrier has raised **RAT R27** text, 3 mm high and 0.4 mm proud of the surface.
- `hardware/RAT-R27-clip.stl`: revised C01 removable camera clip.
- `hardware/RAT-R27-cap.stl`: matching optional PCB cover.

The physical PCB, camera lens, LEDs and flexible ribbon are not part of the rigid hardware print. The combined carrier/holder file contains two separate solid shells so the joint can move; do not Boolean-union those shells. Keep their relative placement when orienting them on the bed. Review supports around the ball/socket before printing so supports do not lock it.

Separate carrier and holder STLs are alternatives to the combined file. Do not print both sets. The separate baseplate STL is optional: the four-color skull already includes that plate in its exact R27 location.

## Revised clip C01

The clip retains the R27 holder interface. Its internal span increases from about 8.2 to 8.6 mm, the arms extend from 2.5 to 3.0 mm above the crossbar, and their thickness increases from 0.75 to 0.95 mm. Catch projection increases from 0.50 to 0.65 mm, with sloped entry faces and 0.25 mm root fillets. The longer arms provide more room to flex; the actual insertion force remains untested.

The static CAD check records 0.00794 mm³ of inherited skew contact with the holder, below the existing 0.01 mm³ interface allowance. Arm and ribbon intersections are zero. This is a fit-test candidate, not a verified snap fit. The original R27 clip remains preserved in the frozen checkpoint.

## Four PLA colors

| Part | U1 slot | PLA color |
| --- | --- | --- |
| Skull and eye-connecting bar | 1 | Red |
| Sclera | 3 | White |
| Cornea | 2 | Black |
| Attached baseplate | 4 | Yellow |

The user confirmed yellow PLA is available. All four slots use the existing Snapmaker PLA SnapSpeed profiles for the U1 with 0.4 mm nozzles and 0.2 mm layer height. Settings are inherited from the established four-color project, not newly calibrated. Check loaded spools, orientation, supports and the sliced preview before printing.

The portable `RAT-R27-four-colors.3mf` and separate material STLs are alternatives. When importing the separate material files, load them together as parts of one object; do not center or drop each region independently.

## Anatomy and attachment

The print skull comes from the current symmetric R16 skull as placed in R27, not the older unregistered R04 anatomy. Small scan gaps are closed, the medial braincase is filled, and the exterior is remeshed for printing. The lateral eye sockets are preserved by restricting transverse fill to the medial region. This is a manufacturing derivative, not a replacement anatomical measurement.

A 2.25 mm diameter bar passes through both current eye centers, matching the diameter used in the recent mouse print. It uses skull material. Eye positions and shapes are retained. Skull material is removed where the eyes and baseplate occupy space, giving mutually exclusive material regions. The baseplate retains its R27 world pose; one shared translation brings the complete print to the bed. The single-color `rat-eyes-embedded-baseplate.stl` is an alternative to the four-color project.

## Validation and reproduction

The pack includes checkpoint identity, hashes, geometry checks and previews. The anatomical print is a connected solid. The final Boolean meshes use a 0.001 mm stabilization tolerance to remove numerical sliver triangles before STL export. Material regions have no meaningful volume overlap. The actual hardware STLs are checked for closed surfaces, manifold topology and self-intersections. Physical strength, joint travel, print settings and dimensional fit still need prototype testing.

From the repository root, use the pinned FreeCAD Python executable for `export_cad.py`, `check_meshes.py` and `check_anatomy_meshes.py`. Use `tools/cad/.venv/Scripts/python.exe` for `prepare_skull.py`, `build_anatomy.py`, `validate_hardware.py` and `package.py`. Run CAD export first, then `revise_clip.py` with the pinned FreeCAD Python. Run skull preparation, anatomy construction, hardware validation, and both native mesh checks. Review with `refresh_prints.FCMacro` before running `package.py` through the existing-window workflow in `docs/development.md`.

Skull attribution: **Rat skull + mandible**, **scienceminer**, Thingiverse 469391. The supplied license states **Creative Commons Attribution Share Alike**, without a version number. Retain `LICENSE-source.txt` with redistributed derivatives.
