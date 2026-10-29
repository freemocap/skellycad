# R11 matched mechanical assembly

This is a complete offline packaging candidate for the routed R11 circuit.
Geometry checks do not demonstrate physical fit, optical performance or a
fabrication-qualified flex assembly. All dimensions are in millimetres.

## What the native document contains

`generated/ov9281-r11-mechanics/OV9281-R11-MATCHED.FCStd` contains the controller,
integrated flex, camera head, 104 populated package envelopes, supports, optics
space and connector. Its `ReviewStatus.BoardSHA256` identifies the matched PCB.
`native-geometry.json` transfers the saved KiCad geometry; `validation.json`
records dimensions, clearances, copper area/volume agreement and source hashes.

The flat span is 74.85 mm. The controller is 28 × 14 mm, the head is 14 × 14 mm,
and the free flex is 32.85 × 8 mm. Finished component regions are nominally
0.303 mm thick and the free flex is 0.166 mm. These are the selected published
construction dimensions, not an order accepted by a fabricator
[@wurthSlimFlex0302026; @wurthSlimRules2023].

The green and amber solids are finished construction envelopes. They already
contain the separately displayed copper. Adding their CAD volumes to the
copper volumes would double-count material. The gold shapes are actual routed
pads, tracks, planes and tapers from KiCad. Inner copper layers are available
in the model tree. Package bodies use conservative fabrication-outline bounds
and selected maximum heights; they are not exact manufacturer STEP models.

The default view shows the flat complete assembly and scale annotations.
Toggle `FlatAssembly` off and `BentAssembly` on to inspect the complete static
bend study. Keep the controller and head subgroups together. The Pupil R08
reference is a separate hidden complete assembly; its added black package
envelopes are approximate photo-derived shapes. The Pupil reference retains
its selected checkpoint and optical datum through `shared.camera.add_camera`.

## Supports, optics and access

The controller support uses 0.10 mm FR4 with 0.05 mm adhesive. Two windows clear
the underside bulk capacitors. The head uses the same support construction as
an 8 × 8 mm ring with a 6.5 × 6.5 mm opening. These support materials and their
bond process remain fabrication assumptions. The native checks found no
package/support intersections, and a 3 mm-deep probe approach volume below the
five programming pads is unobstructed.

The compact optics space reserves an 8 × 8 mm base, a 7.1 mm collar outside
diameter, a 6 mm lens envelope and a 5.2 mm filter envelope. The assumed sensor
plane is 1 mm above the board. The nominal sensor-to-filter gap is 0.28 mm;
filter-to-lens gap is 0.35 mm. Lens extensions of 0, 0.5 and 1 mm clear the
holder in this geometric model. The 0.025 mm radial space is a smooth-envelope
clearance, **not a verified threaded interface or tolerance allowance**.

The optical axis follows the U1 footprint datum. Die alignment, image-plane
height, a real lens thread, focus at 10–20 mm, the 800–1000 nm filter spectrum,
IR image quality and a locking method remain provisional. The model does not
establish those properties. The IR LEDs also require exposure qualification
before use near an eye.

## Static bend study

The free flex follows a 10 mm straight section, a 90-degree arc with 2.5 mm
neutral radius, and an 18.923 mm straight section. Its preserved neutral length
is 32.85 mm. The nominal inner radius is 2.417 mm; at the published upper flex
thickness it is 2.392 mm. This exceeds the selected 10× thickness static-bend
screen, subject to the fabricator's approval of the actual construction
[@wurthSlimRules2023].

The transformed head and controller clear the flex envelope. The bent neck
shows construction geometry only; its copper is not mechanically deformed or
strain-simulated. The flat native copper remains authoritative. No dynamic
flex, fatigue, adhesive stress, thermal expansion or assembly-tolerance result
is claimed.

## Prototype assembly sequence to qualify

1. Confirm the stack, filled/capped laser vias, drying features, stiffeners,
   mask and process tolerances with the selected fabrication process.
2. Assemble the two-sided electronics on a suitable support fixture; follow
   the agreed polyimide drying and reflow process. Inspect the sensor, fine
   pitch controller, hidden joints and supply rails before fitting optics.
3. Bond the supports with the capacitor and programming-pad windows aligned.
   Confirm the actual connector and cable exit clear their surroundings.
4. Fit a qualified filter and lens/holder set while protecting the sensor.
   Adjust focus under the intended IR illumination, then qualify retention.
5. Form the approved static bend using a controlled fixture. Inspect the
   transition and verify continuity before powered camera testing.

These are assembly planning steps, not a released manufacturing procedure.
