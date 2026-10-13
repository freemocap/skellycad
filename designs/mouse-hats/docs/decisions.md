# Scope and decisions

2026-10-08, tray/stem review: user emphasized that the stem's sloped surfaces
are functional mating geometry for seating in the skull base plate. Preserve
their measured angles and positions and check the assembled interface; do not
simplify the stem into a straight extrusion. User identified the circled notch
at the former arm end of the PCB tray (Right/X-axis view) as a suspected artifact
of the old arm attachment, not an intentional requirement. Exact notch parity
is not a priority; defer cleanup with the arm interface. This is user-recalled
design intent, not independently proven provenance. No geometry changed in
response to this clarification.

Latest, 2026-10-08: 58 STEP is the user-approved source, superseding 53 below.
During carrier reconstruction the user explicitly deprioritized the old arm and
junction; these will be replaced in a later phase. Focus on PCB tray, mounting
stem and skull base plate. Tray/stem checkpoint is documented under
reconstruction/main_carrier. No STL/two-arm work has been resumed. The single
custom tolerance-union feature and its loader requirement are explicit technical
limitations, not a claim that the whole model is native or fully simplified.

2026-10-08: User explicitly corrected the active scope to STEP reconstruction.
Authoritative source for this phase:
old/df-hardware/camera-assembly/cad/53nassembly/53nassembly.step

The earlier interpretation that generation 57 STL should control the first
rebuild was incorrect and is superseded. Two-arm V5 and all STL comparisons
are deferred until the user explicitly resumes them. Disregard the earlier
question about STL scale/hardware identifiers for mesh registration.

Preserve originals; reconstruct readable native features and constraints;
compare resulting solids to the STEP geometry. Retain source coordinates until
an explicit documented local part frame is established. Use stable working
part names; assign identities after understanding the STEP components. No
production revisions or physical validation claims at this stage.

The supplied 53 STEP hash matches the prior report, which describes three valid
solids and 43,959 faces. Those are prior inspection findings, not a fresh import
or proof that the solids already have clean parametric feature histories.

The prior exploratory mesh outputs remain as inactive generated artifacts.
They are not accepted baselines or requirements for this phase.
