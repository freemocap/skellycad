# Camera R08: U1 four-material print project

Run `package.py` with the CAD tooling Python to package the selected R08 geometry.
The script verifies the selected asset hashes and preserves the mesh data.
It uses the locally installed Snapmaker Orca U1 0.4 mm nozzle profiles.

The generated file is
`generated/eye-tracker/shared/camera-u1-tpu95ahf-r01/CAMERA-R08-U1-Red-Black-White-TPU95AHF.3mf`.
Open it as a project in Snapmaker Orca to retain part assignments and settings.

| Slot | Material | Parts |
| --- | --- | --- |
| 1 | Red PLA | Main PCB and camera PCB |
| 2 | Black PLA | Lens and holder |
| 3 | White PLA | JST connector and IR LEDs |
| 4 | Yellow TPU 95A HF | Ribbon |

Slot 4 uses the installed `Snapmaker TPU 95A HF @U1 0.4 nozzle` preset as a
starting profile; the spool brand was not specified. Both first and subsequent
layer heights are 0.125 mm, giving two layers through the unchanged 0.25 mm
substrate. The optical axis is excluded from the physical meshes.

Package integrity, slot assignments and unchanged mesh data are verified.
Desktop UI access to Snapmaker Orca was denied by automatic approval, so the
project has not been visually verified or sliced in that application. Check the
slice preview before printing. The thin PLA/TPU boundary has no mechanical
interlock; its bond and durability remain physical print tests.

`open.FCMacro` opens the hash-verified camera checkpoint in the existing FreeCAD
session and reuses an existing matching document. The selected geometry remains
R08; this is a print-settings derivative, not a new geometry selection.
