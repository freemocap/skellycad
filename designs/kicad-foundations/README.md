# KiCad foundations: circuit to fitted board

**Current route:** [From circuit to camera module](lessons/walkthrough.html).
The user condensed the tour into four stages and made the camera the target.
The longer learning route below is retained as a topic inventory, not the active
sequence. No quizzes or prediction prompts; keep explanations concise.

Learn enough electronics design to create, inspect and revise a small PCB, then
fit it into a FreeCAD holder. Follow the existing CAD Foundations teaching rhythm:
explain intent, predict the result, make one visible change, inspect it, validate
it and preserve a checkpoint. A completed automated build is not evidence that
the learner has completed a lesson.

Status on 2026-10-27: [lesson 01](lessons/0001-circuit-and-board.html) and its
[editable indicator schematic](indicator-board/README.md) are ready for discussion.
KiCad parsed the generated schematic, exported the three intended nets and
reported zero ERC violations. Learner understanding has not yet been assessed.
See [integration plan and control evidence](../../docs/kicad-integration.md).

## Teaching project

Use one small, fictional indicator board: a power connector, current-limiting
resistor and LED, followed by mounting holes and a matching holder. Begin with
the circuit and choose actual ratings from component datasheets during the
lesson. Do not treat a teaching assumption as a validated component choice.
Later introduce a second branch or alternate connector to exercise revision.

Keep the electronics in `indicator-board/electronics/`, the holder in
`indicator-board/mechanical/`, and their shared dimensions and matched revisions
in `indicator-board/integration/`. Create these directories as work begins.

## Learning route

| Step | Major concepts | Visible exercise and completion evidence |
| --- | --- | --- |
| 0. Project and control | Manager, schematic editor, PCB editor, libraries, native files | Generate native files with Python; verify with CLI; user opens the project for inspection |
| 1. A circuit is connectivity | Voltage, current, resistance, polarity, symbols, pins, wires, nets and labels | Explain the LED current path; wire one branch and predict an open connection |
| 2. Parts have multiple representations | Symbol vs footprint vs 3D model; references, values and pin-to-pad mapping | Inspect one component across all three representations; verify its pin mapping |
| 3. Schematic checks | Electrical rules check (ERC), power intent, intentional unused pins | Introduce one known error, read its diagnostic, fix it and save a checkpoint |
| 4. A board is a physical layout | Outline, board thickness, layers, pads, placement and unrouted connections | Transfer the schematic; place parts within an explicit board envelope |
| 5. Copper implements the circuit | Tracks, widths, clearance, vias and copper zones | Route the branch; explain each connection; introduce and resolve a design-rule violation |
| 6. Review and manufacturing | Silkscreen, polarity marks, DRC, bill of materials, Gerbers and drill files | Inspect exports in the appropriate viewer and reconcile them with the native design |
| 7. Mechanical integration | STEP, datums, mounting holes, connector access and cable space | Import into FreeCAD, build a simple holder, check dimensions and record missing model limits |
| 8. Revise without losing agreement | Source ownership, stale exports, matched checkpoints | Move a connector in KiCad, regenerate STEP and update/check the holder |

This sequence follows KiCad's documented schematic-to-board workflow, with a
FreeCAD handoff added for this repository. [@kicad10GettingStarted]

## Session rhythm and records

Work on one meaningful step per teaching exchange. Explain terms as they appear;
do not present a finished board before teaching the decisions that created it.
Use code where it makes intent clearer and the GUI to inspect the resulting
design. Ask a short prediction or interpretation question before moving on.
Adapt the pace to the user's answers rather than treating the table as a quiz.
The user operates the desktop. Agent work uses Python and files; live PCB IPC is
optional, not a prerequisite for lessons. Do not use desktop automation.

Preserve numbered native checkpoints with the source files required to reopen
them, brief change notes and validation results. Record learner progress only
after discussion or demonstrated understanding. Disposable replay/export files
belong in root `generated/kicad-foundations/`. Keep accepted checkpoints unchanged.

Electrical-rule checks and design-rule checks help find mistakes but do not
establish electrical performance, manufacturability for every supplier or
physical fit. Fabrication, assembly and powered testing are later activities.

The first lesson ends when the user can distinguish the schematic, footprint,
PCB and 3D model, and identify which representation should change for a different
electrical connection versus a moved connector.
