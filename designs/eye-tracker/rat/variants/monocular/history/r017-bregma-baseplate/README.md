# Rat R17: baseplate tip at bregma

This placement study puts the rostral top point of the unchanged R09 baseplate
above the R16 bregma design reference, with the plate body extending caudally.
Caudal means toward the tail; rostral means toward the nose. The anatomical
reference is the symmetric R16 derivative with its existing eyes and axes.
The selected complete assembly remains R01; R09 supplies the later matched
hardware baseline. Neither complete assembly is modified by this study.

## Placement convention

The point is the most rostral vertex on the top mating face (face 5 of the
extracted R09 solid). Its dorsal projection is X = 0, Y = 0. This does not put
the elevated top point physically against the skull. The bregma design reference
is the R16 midline at atlas-derived AP = 0 projected onto the skull surface,
(0, 0, -0.055) mm. It is not a newly identified suture in a measured specimen.

A symmetric local roof plane is fitted over X = -11 to -2 mm, Y = -3 to +3 mm.
Of 368 ray hits, 362 lie within 0.8 mm of the median height and are retained;
the filter excludes rays passing through holes onto internal geometry. The
roof-fit RMS is 0.161 mm. The mating face follows this plane with zero roll.
The lower-face center is placed 0.25 mm below the fitted plane as contact stock.
This is a CAD seating convention, not a cement thickness recommendation.

The plate's top point is at (0, 0, 10.089) mm. Overall bounds are approximately
X = -11.477 to +0.175, Y = ±5.043, Z = -0.303 to 11.297 mm. A slightly rostral
lower edge remains because of the fitted pitch. The solid is valid and its
442.128 mm³ volume is preserved. The sampled minimum distance from 5,000 rear
hole-wall samples to the skull is 6.977 mm; it excludes any unspecified screw
projection, screw head or tool-access envelope and is not a continuous bound.

## Attachment evidence and design implications

Schwarz and colleagues describe frontal bone as relatively firm and lateral
bone as thinner/softer. For their head-post configuration they favor the midline
above lambda when compatible with the experiment, and warn against overhanging
positions that impose asymmetric torque [@schwarz2010RatHeadFixation]. This
supports reviewing a centered caudal layout, but does not establish that the
parietal region is strongest or validate this printed adhesive-mounted plate.

Hadlock and colleagues distributed attachment over cranial plates while keeping
bone screws away from sutures and dural sinuses [@hadlock2007RatHeadFixation].
Thus bregma is useful as a registration reference, not a prescribed anchor hole.
For our adhesive footprint, broad intact bone support and load distribution
are engineering goals; neither paper supplies an optimum footprint or measured
strength map for this model. Adhesion and strength cannot be inferred from the
surface mesh. The cited screw designs are not screw-depth prescriptions for
this implant; the Hadlock study reported brain penetration by some screw tips.

Review scope: Schwarz implant-section excerpts indexed from the primary paper
and publisher PDF; Hadlock implant design, figure 1, cohort and postmortem
results. Bibliography entries record this scope. No source establishes the
proposed placement as an implantation protocol or validates the printed material.

## Review and reproduce

Use the checkpoint identified in `review.json` for the visual review. The red
surface marker identifies the bregma proxy; the dashed line projects to the blue
plate tip. Plate size and mating interfaces are unchanged. The underside has not
been trimmed to the skull and the camera/arms/ribbon have not been reattached.
Those require a separate complete-assembly revision and targeting validation.

From the repository root, run `measure.py` then `extract.py` with the pinned
FreeCAD Python, and `fit.py` with `tools/cad/.venv/Scripts/python.exe`. Submit
`open.FCMacro` through `tools/cad/open_in_running.py --expected-pid <verified PID>`
to the existing desktop session. Submit `capture.FCMacro` after the view updates.
Preserve the R09 and R16 checkpoints and the recorded transform in `placement.json`.
