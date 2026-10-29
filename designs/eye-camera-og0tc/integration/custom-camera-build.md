# Custom OG0TC camera: superseded implementation direction

Superseded on 2026-10-27 by the [OV9281 camera](../../eye-camera-ov9281/README.md). The record below preserves the earlier decision; the vendor request is no longer the active next step.

Decision, 2026-10-27: design our own single-camera assembly around OG0TC1B.
Finding a matching stocked finished module is no longer a prerequisite. The
user's Pupil camera is the physical/function reference, not a verified circuit
to copy. Preserve the previous bare-sensor R01 and integrated-module R02 CAD.

## Assembly to implement

OG0TC1B + close-focus lens/visible-blocking NIR filter + controlled IR LEDs
-> short flex -> one thin receiver/USB PCB -> four-contact JST -> external USB hub.

The sensor is 1.64 x 1.64 mm, monochrome global shutter, 400 x 400, with one-lane
D-PHY output [@omnivisionOg0tcBrief]. First mode target is 400 x 400, 8-bit,
120 fps: 19.2 MB/s image payload. Actual sensor timing and USB mode must be tested.
No on-animal hub, stacked boards, or compulsory long evaluation cable.

Use the requirements in infrared-requirements.json: 10-20 mm optical working
distance, 940 nm baseline illumination, visible suppression, one physical board
with a provisional 0.4-0.6 mm thickness, and a short flex. These thicknesses are
fabrication targets, not an already approved stackup [@jlcThinPcbCapabilities].
Use a purchased miniature lens/holder assembly with adjustable spacing and lock
it after focusing in NIR. Exact thread, focal length and filter remain unselected.
Lens choice must also provide suitable image coverage, not merely sharp focus.

## What can be engineered, and what must be obtained

We can produce the carrier and head schematics, PCB layout, flex design, lens
mount, power/LED electronics, receiver firmware adaptation, capture software,
fabrication outputs and validation fixtures. Lens manufacture, PCB fabrication,
assembly and physical image tests remain physical work.

The current public OG0TC brief does not contain the component ball map/land
pattern or sensor initialization registers. The Leopard 24-contact module map
is not a substitute. Obtain the full OG0TC design package and actual sample
availability before releasing the sensor PCB. Do not invent pins or registers.

For USB, CX3 is a documented programmable candidate with an interface workflow
[@infineonCx3ApplicationNote], but neither compatibility nor the desired narrow
outline is established. Choose the supported controller/firmware route before
freezing board width. Four-contact USB output remains the requirement even if
the chosen chip also supports USB 3.0. Do not infer a firmware implementation
from an existing camera's package marking.

The supplied handoff identifies the Pupil controller marking as SONiX
SN9C5256AJG, but contains no verified controller datasheet or identified sensor.
This is useful evidence for a manufacturer inquiry, not a reproducible schematic.
Its approximately 0.7 g complete-camera mass is a user-supplied reference, not
a predicted mass for our design.

## Immediate dependency request

Ask OMNIVISION or an authorized module integrator for OG0TC1B samples and the
component pinout/land pattern, power sequence, reference schematic, clock/IO
requirements, mode-specific register initialization and MIPI timings. Ask for
an existing compatible USB 2.0 controller circuit/firmware if available. Request
price, quantity and an actual ship date, plus design/firmware access terms.
The request is prepared in custom-sensor-request.txt and remains unsent.

Success means a recorded physical-camera image at the intended IR wavelength
and distance, followed by measured frame rate, image quality, power and mass.
This decision record does not claim a routed circuit or functioning hardware.
