# Eye-camera roadmap

Updated 2026-10-29. The [approved R11 session](electronics/r11/CHECKLIST.md)
advances compact electronics, matching mechanics and offline bring-up software.
The resulting candidate is fully routed and reviewed, but the global qualification
items below remain open. Session completion is not product completion.

R11's immediate remaining gates are the 1.34 g mass estimate versus the under-one-gram
target, supplier/lifecycle gaps, sensor DVDD stress margin, actual IR optics,
fabrication qualification and physical operation. See [the current review](WORKING-REVIEW.md)
and [prototype gates](electronics/r11/PROTOTYPE-TESTS.md). Future work receives a
bounded checklist and approval before execution.

## Global roadmap

- [x] Establish the camera architecture and create initial electronics, mechanical and software designs.
- [x] Complete the PCB connections and pass the existing connectivity and spacing checks.
- [ ] Qualify the electrical design, including high-speed routing, power, clocks and illumination control.
- [ ] Finish the infrared optics and mechanical design, including focus adjustment, filter, holder and mounting.
- [ ] Complete the firmware and computer recording software, with all available offline checks.
- [ ] Prepare a consistent manufacturing package, parts list and prototype test procedure.
- [ ] Build and test physical prototypes, then revise the design from measured results.

## Earlier approved session: interconnect audit

- [x] Establish documented MIPI and USB routing requirements and candidate rigid-board and flex layer structures, explicitly identifying assumptions.
- [x] Audit all three MIPI pairs across the head, flex and controller for routing continuity, length differences, layer transitions and ground-return interruptions.
- [x] Audit the USB path from the ESP32-P4 to the four-contact connector and identify requirements for the external cable.
- [x] Save a review package that locates every identified issue on the actual boards and defines the complete corrective routing checklist.

## Earlier R10 milestone

The previous session connected the remaining head-board nets and passed the
existing spacing rules. That established a complete electrical connection map.
The audit then identified 21 high-speed interconnect findings. R10 repairs the
paired routes, reference planes and transitions, records nominal impedance
models, matches the planar routes and specifies a prototype USB cable. These
offline checks do not demonstrate working hardware.

The original [audit report](audits/2026-10-28-interconnect/REPORT.md) remains
preserved. The [R10 review](audits/2026-10-28-corrective-routing/REPORT.md)
records every finding's disposition and the matched native files. The exact
approved execution list is in [CHECKLIST.md](electronics/r10/CHECKLIST.md).
Power, clock and illumination qualification,
optics, software and physical validation remain separate parts of the global
roadmap; they were not silently added to this session.
