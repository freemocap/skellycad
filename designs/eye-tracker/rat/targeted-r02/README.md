# Monocular rat R02: camera aimed at the right eye

This review revision brings the measured mouse R08 camera, flexible ribbon and
rectangular-arm design into the aligned rat skull-and-eyes frame. The target is
the existing right-eye geometric center at (0.75, -8.35, 0) mm. It preserves the
mouse baseplate geometry and the camera's matched holder/ball/clip interfaces.

The inherited mount position penetrated the skull. The complete mount is raised
3.6 mm along skull +Z. The lens position and orientation are then solved around
fixed-length ribbon reach while aiming through the eye center. The socket and
cradle move together; both arms regenerate between their original tray roots
and the new socket pose. Full 2.2 mm terminal thickness is retained.

`recipe.json` is the reproducible input. `review.json` identifies the frozen
complete assembly and its validation. The selected rat checkpoint remains
ET-RAT-MONO-R01; R02 is a separate review candidate. The earlier checkpoints,
user-aligned skull and independently defined eyes remain unchanged.

## Rebuild and inspect

Follow [the targeting workflow](../../../../docs/eye-tracker-targeting.md).
The shared `targeting/run.py` command rebuilds this recipe into a new output
folder. The individual scripts here are stage entry points for troubleshooting.
`search_pose.py` proposes a new rest pose but does not change the recipe.

Run `open.FCMacro` through the existing FreeCAD window procedure. It opens a
separate review copy, preserving the earlier open documents. The red segment
runs from the nominal lens reference point to the right-eye center. Both eyes
retain their independent right-handed frames and material regions. Toggle the
eye-axis groups in the tree when needed.

## What validation establishes

Validation checks the aimed ray, fixed endpoint frames, unstretched ribbon,
finite-thickness collision volumes, one-solid carrier, attachment finishing,
matched-part clearances, STL topology and anatomy interference. Exact reported
values are in `review.json` and the generated validation report. Sampled
collision planes guide optimization; they do not replace the solid checks.

The inherited nominal JST model overlaps the tray by approximately 0.0590 mm³;
that conflict already exists in mouse R08 and is recorded separately. Its exact
connector variant and physical clearance still require confirmation. The
inherited cap contact is also tracked separately from newly introduced overlap.

The anatomy and eye placement remain schematic. The copied mouse baseplate has
not been contoured or physically fitted to the rat skull; removing penetration
does not establish stable seating or attachment. This is a first geometric fit,
not evidence of print strength, camera focus, biological fit or cable fatigue.

The complete assembly retains the dense skull's triangle geometry. Rat skull
source: scienceminer, Thingiverse 469391, Creative Commons Attribution Share
Alike (version unspecified in the supplied license). See the retained skull
provenance and license under `../references/skull/thingiverse-469391/`.

## Print groups

The generated print package contains carrier-and-holder together, matching cap,
camera clip and baseplate. The carrier and holder retain their mating pose in
the mount frame. The separate unchanged cap, clip and baseplate use their
original kit print poses; their STL positions are not an assembled skull-frame
layout. Use the native complete assembly to inspect placement.

A fresh rebuild in `generated/eye-tracker/rat/targeted-r02/replay-check` matched
the reviewed hardware vertices, volumes and areas. Five pose/frame regression
tests and the bibliography checker with eight tests passed. Skull/eye surface
crossings were zero; sampled skull containment found zero interior samples.
The nearest sampled baseplate/skull distance was about 0.50 mm, which is a
sampled clearance estimate rather than a guaranteed minimum gap.
