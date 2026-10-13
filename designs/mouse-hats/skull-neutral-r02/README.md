> SUPERSEDED AS A COMPLETE MODEL: this study used the older PCB tray. Its camera/arm work is incorporated into [the current model](../current/README.md). Use the current manifest for edits and printing.

# R02: neutral eye alignment with preserved ribbon loop

2026-10-11. User requested another version retaining room for the sensor-to-PCB
ribbon bend. R01 compressed the rear loop when only its socket endpoint moved.
R02 preserves the original R11B rear arm as a rigid translation with the camera
joint, then adds a smooth connection to the fixed PCB tray. Camera placement,
holder neutral pose, eye target, socket dimensions and top arm remain at R01.
R01 and the selected R11B source are preserved.

## Visible files

- `generated/mouse-hats/skull-neutral-r02/ribbon-space-study.FCStd`: complete
  candidate, with skull/eyes and unchanged aiming guide.
- `generated/mouse-hats/skull-neutral-r02/ribbon-space-comparison.FCStd`: static
  top view, R01 gray on the left and R02 cyan on the right. Both use the same pose.

The original R11B curved arm, including its sections, bend geometry and socket
approach, is translated by (-7.492981, +0.342848, -0.652235) mm in assembly coordinates.
The fixed tray root keeps its original straight lead, followed by a cubic transition
to the translated arm root. Connection length is 7.649934 mm, with 0.1 mm overlap.
The unchanged R11B main curve has length 34.787601 mm. No smoothing or scaling of
that curve is used. The widened loop reaches X=-16.2456 mm versus R01's -9.6556 mm.
This restores the loop's shape relative to the camera; it is not a ribbon simulation.

## Checks

- Final carrier is one deep-valid solid, volume 1267.236091 mm3. Saved document
  contains no invalid objects; fresh reopen retains the new feature implementation.
- Holder pose is identical to R01. Holder/carrier overlap 0 mm3 and minimum gap
  0.333165 mm. Carrier overlap with clip, cap and baseplate is also 0 mm3.
- Optical axis remains unchanged and unobstructed by the carrier.
- Translated rear-loop/holder separation 1.643332 mm; added connection/holder
  separation 5.940541 mm. These are part-to-part distances, not ribbon bend radii.
- Original inputs and previous candidates remain unchanged. No new print release.

The physical ribbon's width, length, thickness and minimum bend radius have not
been supplied or modeled. Full movement, cable fit and strength are unverified.
The existing provisional pupil-area target and implant seating assumptions remain.

## Rebuild and controls

Run `open_model.py` in the pinned FreeCAD GUI to load dependencies and open R02.
The saved model is self-contained except for Python feature code. Its JointShift
control regenerates the rear connection and moves the joint, holder, clip and
guide together; only the saved configuration has been validated here. Hidden
PreservedRearLoop and TrayExtension inspection shapes are static build snapshots.

`build.py` copies the saved R01 to a new R02 output, installs `RibbonSpaceNeutral`,
and rebuilds. `preserved_loop.py` reuses the R11B construction and adds the tray
connection. Settings and validation use mm, degrees and mm3. `compare.py` builds
the static comparison from the two open candidates. Rebuilding replaces generated
R02 files; save any desired manual variations separately first. No automatic
JSON synchronization with GUI edits is implied.
