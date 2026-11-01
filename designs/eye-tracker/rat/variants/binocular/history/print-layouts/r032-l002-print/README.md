# RAT R32 L02 trial print pack - flat clips

Use these files at **100% scale in millimetres**. They reproduce the compact binocular R32 geometry for a trial print. The R32 assembly checkpoint and previous R27 print pack remain unchanged.

## The two main files

1. **`anatomy/RAT-R32-Snapmaker-U1.3mf`**: open as a project in Snapmaker Orca. This is the established four-color rat skull and connected eyes, updated with the baseplate 2 mm lower to match R32.
2. **`hardware/RAT-R32-all-hardware.stl`**: one STL containing the shared carrier, both movable sensor holders, and two detached clips arranged beside the mechanism. It contains five closed shells. The carrier and holders retain their matched positions; do not Boolean-union the moving parts or rearrange those three shells independently.

Layout L02 rotates both clips onto their broad U-shaped faces, with the crossbar and arms in the XY plane and the bottom face on Z=0. Each clip is 3.5 mm tall in this orientation. The main carrier and both holders retain their matched arrangement. Keep the supplied orientation when importing the all-hardware STL; do not auto-orient its separate shells. There is an 8 mm footprint gap beside the mechanism and 5 mm between clips. The electronics, lenses, LEDs and flexible ribbons are excluded. No cap is included.

These files are mesh-validated and unsliced. Check bed orientation, supports and the sliced preview before printing. In particular, supports must not permanently lock either ball/socket joint. Physical fit, ribbon bending, strength and joint movement remain trial-print questions; junction finishing remains deferred.

## Snapmaker U1 colors and settings

| Region | U1 slot | Material/color |
| --- | --- | --- |
| Skull and eye-connecting bar | 1 | Red PLA |
| Corneas | 2 | Black PLA |
| Sclera | 3 | White PLA |
| Embedded baseplate | 4 | Yellow PLA |

The project preserves the existing R27 **Snapmaker U1 (0.4 nozzle)** printer profile, four **Snapmaker PLA SnapSpeed @U1** filament profiles and **0.2 mm layer height**. All project settings are unchanged from that template. Check that your loaded spools match the slots. No new tuning or sliced toolpaths are supplied.

The printable skull derivative and eye geometry are retained from R27. The 2.25 mm eye-connecting bar remains skull material. Skull material is removed where the lowered plate and eyes occupy space, so the four material regions do not meaningfully overlap. The plate's R32 pose is retained; one common translation places the complete anatomy on the bed. The anatomy remains one connected printable body.

This embedded plate is part of a mock-skull print. It does not perform the deferred skull-contour cut on a separate plate for use on an animal.

## Alternatives: do not print duplicate sets

- `hardware/RAT-R32-carrier-and-two-holders.stl` contains the mechanism without the detached clips. Print it with one right clip and one left clip if you prefer separate jobs.
- Separate carrier and holder STLs are alternatives to the combined mechanism. They have independent bed placements and do not preserve the joint assembly arrangement when imported together.
- `hardware/RAT-R32-baseplate-optional.stl` is an optional separate, uncut baseplate. The four-color skull already includes its plate.
- `anatomy/RAT-R32-four-colors.3mf` is the portable material model without U1 project settings.
- The four material STLs share one anatomy print frame. Import them together as parts of one object; do not drop or center each region separately.
- `anatomy/rat-eyes-embedded-baseplate.stl` is a single-color alternative. `rat-eyes.stl` omits the baseplate.

## Validation and provenance

The R32 complete assembly hash is checked before export. Hardware geometry is unchanged apart from rigid print placement and numerical triangulation cleanup with at most 0.001 cubic millimetres of volume change per file. All exported STLs pass closed-surface and self-intersection checks. Shell counts, hashes, dimensions, material overlaps, embedded-plate pose and U1 settings are recorded in the included validation reports and `manifest.json`.

The hardware retains R32's 1.2 mm shared PCB spine and rearward support routes. Its carrier uses about 33% less solid volume than R31. This is not a measured mass or strength result.

Rebuilding requires this repository and its pinned runtimes, plus the recorded R27 print inputs. First reproduce or retain the verified R32 print pack. Run `layout.py` with the pinned FreeCAD Python, `validate_hardware.py` with the tooling Python, `check_meshes.py` and `render.py` with the pinned FreeCAD Python, then `package.py` with the tooling Python. Stop on a failed check. Outputs go to `generated/eye-tracker/rat/print-r32-l02/`. The original print-r32 pack is preserved. The U1 anatomy project is unchanged.

Skull attribution: **Rat skull + mandible**, **scienceminer**, Thingiverse 469391. The supplied license states **Creative Commons Attribution Share Alike**, without a version number. Keep `LICENSE-source.txt` with redistributed skull derivatives.

This pack uses existing local geometry and printer settings, with no new external technical sources.
