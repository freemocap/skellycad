# Selected packaging direction: candidate C

The user selected candidate C on 2026-10-28: use the better-documented SLIM.flex
construction as the basis for the next design phase. The small size difference
from candidate B is acceptable. This supersedes the earlier recommendation to
pursue B first; the completed comparison and its checkpoint remain historical
evidence.

The planning envelope is a 26 x 12.5 mm controller, a 12.5 x 12.5 mm camera head,
and a 32.85 x 8 mm free inter-board flex. The estimated complete module mass is
1.27 g nominal, with a screening range of 0.84–1.87 g. The under-one-gram target
remains open and excludes the external tether. OV9281 and ESP32-P4 remain on the
module. These dimensions are checked packing envelopes, not manufacturing
tolerances or a completed routed design.

Wuerth's published FLEX6_6F_030_12_2V13 template provides a concrete construction
basis: a 0.303 mm six-layer component region, a 0.166 mm two-layer flex option,
and a standard microvia process [@wurthSlimFlex0302026]. That reduces uncertainty
about the layer construction. It does not qualify our component substitutions,
added stiffeners, lens support, routing, cost or final mass. The added local
supports belong to our study, not to a manufacturer-approved camera assembly.

The next phase should select compatible real components and resolve the
construction constraints for C before revising placement and routing. Do not
continue optimizing B unless new evidence justifies revisiting this decision.
R10 remains the working electrical baseline and R08 remains the selected
electrical release. This decision does not change either selector or approve
fabrication.

Source comparison: `../size-mass-r01/`. Preserved study checkpoint:
`../../checkpoints/2026-10-28-size-mass-r01/`.
