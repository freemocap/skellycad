# Preserved OG0TC / OC0TC camera concepts

**Current development has moved to the [OV9281 camera](../eye-camera-ov9281/README.md), selected on 2026-10-27.** The decisions and CAD below describe earlier alternatives and remain historical records.

# Eye-camera development / preserved OC0TC concept — current R02

**Active direction: our own OG0TC1B camera assembly.** See [custom build](integration/custom-camera-build.md). A stocked complete module is no longer the prerequisite; actual sensor samples and the full electrical/register documentation are required. Previous module candidates and CAD below remain historical alternatives.


**Conditional hardware candidate: LI-OC0TC1B-MIPI assembled camera plus a vendor-confirmed USB receiver and matching firmware.** See [first camera build](integration/first-camera-build.md) and the [unsent matched-kit request](integration/leopard-evaluation-request.txt). The vendor publishes 8-100 mm focus and the connector pinout [@leopardOc0tcModule; @leopardOc0tcDatasheet]. USB compatibility, delivery and IR filtering still require confirmation. Current requirements are 10-20 mm working distance, a thin single USB board and four-contact JST output; see [sourcing disposition](integration/compact-camera-sourcing.md). R02 remains the earlier packaging concept, not the Leopard assembly.



**Selected direction: OC0TC integrated sensor and optics.** Current design data:

[integration/current-design.json](integration/current-design.json).

R02 removes the separate sensor, threaded lens and holder from the new head.

The reviewed product page lists the monochrome OC0TC1B-RAVA-001A 16-pin variant

[@omnivisionOc0tcProduct]. Exact ordering and availability need confirmation.



The module has a published 1.7 mm height [@omnivisionOc0tcBrief]. Its XY package

size is not specified in the reviewed material: R02 reserves 3 x 3 mm and labels

this as an allowance, never as the actual module dimensions. Do not reuse the

bare sensor's 1.64 mm dimensions as module dimensions. The head remains 8 x 8 mm

until the module land pattern, LED layout and assembly constraints are known.



R02 files are under electronics/r02 and mechanical/r02; the current rendered

explanation remains integration/explainer.html. The flat envelope stays 58 x

14 mm, with a 30 mm flex. New solids are valid and pairwise volumetric overlap

is zero. The selected complete Pupil reference is imported with hash checks.

R01 below is historical and remains unchanged.



OC0TC still outputs MIPI, so receiver/USB electronics remain required. CX3 is a

candidate; no working pair is established. Package drawing/pinout, power/IO,

register initialization, mode timing, close-focus performance and an evaluation

path remain required before a complete circuit. The unsent request is now

focused on OC0TC and existing vendor reference designs. Nothing was sent or bought.



## Infrared application requirements



The current design explicitly targets **indoor active near-infrared eye imaging**:

monochrome global shutter, visible-light suppression, and associated IR LEDs.

The user's spectral region is approximately 800-1000 nm. The proposed minimal-

assembly baseline is a factory-filtered module matched to 940 nm LEDs. A narrow

940 nm passband is within that region but does not transmit the entire range;

do not assume compatibility with 850 nm illumination.



The OC0TC brief claims a 940 nm lens coating for sunlight suppression, but gives

no transmission curve, blocking level or passband width [@omnivisionOc0tcBrief].

Our interpretation is that spectral filtering may reject unwanted ambient light;

that is not confirmation of the coating type. A matched narrow bandpass is an

established way to improve contrast against ambient illumination

[@midopt940Bandpass]. Neither monochrome operation nor NIR sensitivity alone

establishes visible blocking. An IR-cut filter would reject the light we need.



OC0TC remains a candidate pending optical qualification. Prefer the vendor's

existing NIR-filtered, close-focus module and supported receiver. Request the

exact monochrome variant's transmission curve, angular response and focus data

before adding an external filter or designing custom optics. Ambient rejection

can also matter indoors; light inside the passband remains visible to the camera.



The electrical plan reserves an adjustable current-limited LED driver with

hardware default-off control and provision for exposure synchronization. The

LED parts, currents, duty cycle and exposure limits are not selected. The CAD

blocks are space allowances, not a verified illuminator. See

[integration/infrared-requirements.json](integration/infrared-requirements.json)

for the requirements and unresolved qualification items. This update changes

requirements only; R02 geometry and historical artifacts remain unchanged.



## Preserved R01 rationale



R01 starts a new single-sensor camera design, separate from the completed KiCad

foundations coupon and from all selected Pupil/species checkpoints. It recreates

the functional arrangement of the user's reference, not its unknown circuit.



## Architecture and scope



OG0TC1B sensor -> 30 mm MIPI flex -> CX3 receiver/USB firmware -> four-wire

USB 2.0 through a proposed JST SH connector -> external hub/computer.

The public sensor brief specifies 1.64 x 1.64 mm, 400 x 400 global shutter,

one-lane D-PHY, and nominal 2.8 V analog / 1.1 V D-PHY core rails.

IO voltage, sequence, package height and pin map remain unknown

[@omnivisionOg0tcBrief].



CX3 is a documented bridge candidate, not a verified working pair. Its

10 x 10 x 1.7 mm package makes a 10 mm-wide board impractical as an assumed

layout. The provisional main-board allowance is 20 x 14 mm; full length is

20 + 30 + 8 = 58 mm. All support circuits may not fit after actual placement,

BGA escape and decoupling. USB 2.0 capability is published, but actual stream

support depends on firmware and sensor timing [@infineonCx3Datasheet].



R01 includes native KiCad architecture and placement drawings, a FreeCAD

packaging concept, STEP envelope and a comparison with the complete selected

CAMERA-DUMMY-R08. Its native and physical-part hashes are verified by the shared

camera loader. The reference optical datum moves with its complete group.

No species placement or existing geometry is revised.



**This is not a full electrical PCB design.** The KiCad schematic contains

functional boxes, not a sensor symbol with guessed pins. The PCB contains the

main-board outline and drawing-layer allowances; no sensor pads or copper routes.

No ERC/DRC pass is used as evidence of circuit completeness. No Gerbers are issued.



## Remaining circuit work



The full implementation needs sensor land pattern and pinout; decoupling and

power sequencing; compatible IO levels; external sensor/bridge clocks and reset;

boot configuration and flash; MIPI/USB routing constraints; USB protection and

power input; sensor register initialization; USB streaming firmware; and an IR

LED driver. Main-board power and underside flash boxes reserve space only.

Infineon's AN90369 provides a practical firmware/interface starting point and

calls for an external sensor clock in the production design

[@infineonCx3ApplicationNote].



Local connector proposal: pin 1 VBUS, pin 2 D-, pin 3 D+, pin 4 GND. This is our

new convention, not a verified Pupil cable assignment. The connector candidate

is SM04B-SRSS-TB, 1 mm SH series [@jstShCatalog]. Four signal contacts support the

proposed USB 2.0 route; they do not carry USB SuperSpeed lanes. Harness shielding,

pair geometry and strain relief still need design.



400 x 400 x 120 x 8 = 153.6 Mbit/s (19.2 MB/s) image payload. Ten-bit packed

payload is 192 Mbit/s; a host format padded to 16 bits is 307.2 Mbit/s.

These are arithmetic budgets, not measured USB throughput or supported modes.



## Optics and mechanical limits



The head is an 8 x 8 mm allowance with a 6 x 6 mm holder and M4-scale barrel.

No real lens, thread, working distance or image-circle prescription is selected.

The barrel/holder overlap represents an intended threaded interface, not a

validated mate. The 0.4 mm sensor height is explicitly a placeholder. The two

1 mm LED blocks are also allowances. No optical or illumination safety test

has occurred; LED current and duty cycle remain unset.



OC0TC is an alternative integrated sensor/optics module with a published

1.7 mm height. It could remove the separate threaded-lens assembly; focus,

package drawing and availability still need confirmation [@omnivisionOc0tcBrief].



## Files and validation



- electronics/r01: native KiCad functional schematic and placement study.

- mechanical/r01: native comparison, concept STEP, previews and geometry report.

- integration/design.json: dimensions, assumptions, proposed interface and gaps.

- integration/explainer.html: rendered project overview.

- integration/vendor-information-request.txt: unsent information request.



All new solids validate. The concept envelope measures 58 x 14 x 5.8 mm including

underside flash allowance. These results establish geometry only, not component

fit, heat dissipation, mass, functional optics or working video. Review scope is

recorded beside each source in references.bib. The user's supplied handoff informs

the product direction; SONiX markings do not establish a reproducible schematic.



Builders use KiCad and FreeCAD bundled Python respectively. They preserve an

existing R01; create a new revision before further geometry or circuit work.

