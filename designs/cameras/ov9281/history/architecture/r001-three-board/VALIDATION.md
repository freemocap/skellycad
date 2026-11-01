# A01 validation record

Reviewed 2026-10-29. This record applies only to the three-board architecture package. It does not qualify manufactured hardware.

| Check | Result | Scope |
| --- | --- | --- |
| R11 preservation | 2,811 hashes unchanged | R11 records, checkpoint snapshot, selected native/generated files and working-review selection |
| KiCad CLI export | Four native sheets parsed and exported | Functional diagrams only; no electrical pins, ERC or DRC claim |
| KiCad visual review | All four rendered PDF pages inspected | Text readable; no clipping or overlapping blocks |
| Placement | 99 body envelopes, all within assigned boards | 28 head, 40 interface, 31 base; all front-side |
| FreeCAD geometry | 111 valid solids per variant, no volume intersections | FR4 and steel complete placement assemblies; does not prove pad clearance, routing or physical fit |
| Native integrity | Both saved files reopened with matching object volumes; ZIP integrity passed | Final hashes and placement-source hash recorded in `cad-validation.json` |
| View review | Front, backing-only underside and full assembly inspected | Orthographic cameras corrected during review; diagram tether is explicitly not to scale |
| Budgets | Mass sums, dimensional coupling and DC conservation pass | Analytical scenarios only; high mass cases exceed one gram |
| HTML | HTTP 200, no script errors, four view switches exercised | Images load; no horizontal overflow at 390 px; desktop screenshot inspected |
| Bibliography | 176 references, zero errors; eight tests pass | Repository source keys and required review metadata |
| Desktop review | Verified A01 native file opened through FreeCAD IPC macro | Unrelated documents preserved; current review remains open |

The native builder emitted temporary FreeCAD cache rename warnings. The saved documents nevertheless passed ZIP integrity and reopened-volume checks. Finished task-owned build documents were closed before the isolated process wrapper was stopped. Only the saved current review was subsequently opened; unrelated desktop work was not closed or modified.

Source review covers public manufacturer interface, clock and package excerpts; distributor listing observations; and saved R11 calculations/firmware records. It is not a complete silicon register review or supplier qualification. See `COMPONENT-CHAIN.md` for the sources and procurement uncertainty. Every citation key is checked against the repository bibliography.

Missing demonstrations remain explicit: no powered sensor, qualified RF tether, continuous capture, USB throughput benchmark, optical focus measurement, thermal test, final weight, manufacturer-approved new stack or animal-mounted fit. Completion means the approved **architecture package** is ready for the next design decision.
