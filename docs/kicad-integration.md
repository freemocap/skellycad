# KiCad integration plan

Status: proposed workflow, with installation and file automation checked on
2026-10-27. Start with [KiCad foundations](../designs/kicad-foundations/README.md).
Keep setup small enough to begin the first lesson before building more tooling.

## Installation and control evidence

The user's KiCad 10.0.7 installation is at
`C:/Users/jonma/AppData/Local/Programs/KiCad/10.0`. The running manager uses this
installation. Its executable signature is valid and identifies KiCad Services
Corporation. The bundled Python, Device symbol library, resistor footprint
library, 3D-model directory and demos directory are present. This verifies
installation basics, not every library model or editor function.

The agent generated a disposable 30 x 20 mm rectangular board using bundled
`pcbnew`, saved and reloaded its four outline segments, and exported a STEP file
with `kicad-cli`. Outputs are in ignored `generated/kicad-verification/`.
The export returned success. Sandboxed CLI execution emitted Windows registry
access warnings; those warnings did not prevent this export. FreeCAD import,
component models, electrical checks and live editing were not tested here.
The running manager was inspected through Windows Computer Use.

| Route | Intended use | Current status |
| --- | --- | --- |
| `kicad-cli` | Electrical/design-rule checks, plots and manufacturing/STEP exports | Version and bare-board STEP export tested |
| Official IPC API with `kicad-python` | Read and edit the board shown in the PCB editor | API disabled in saved settings; client absent from bundled Python; not tested |
| Windows Computer Use | Editor navigation and schematic operations | Manager window inspection tested; design editing pending |
| Bundled `pcbnew` Python | Temporary, version-specific offline board automation | Create/save/reload tested; deprecated, not the long-term foundation |

KiCad 10's IPC API requires a running GUI, supports the PCB editor rather than
the schematic editor, and uses the CLI for exports. Use documentation matching
the installed version; newer API documentation can describe unreleased features.
[@kicadIpcDevelopers]
The CLI exposes schematic ERC, board DRC and export commands.
[@kicad10Cli]
The legacy Python bindings are deprecated; prefer IPC for new live automation.
[@kicadLegacyPython]

## Repository organization

Keep projects together by purpose. Do not move CAD Foundations, Mouse Hats,
eye-tracker designs or their accepted checkpoints. Add folders as real work
needs them, rather than creating a global electronics/mechanics hierarchy.

```text
designs/
  cad-foundations/                 existing course, preserved
  kicad-foundations/
    README.md                     course route and session status
    indicator-board/              create during lessons
      electronics/                KiCad project, schematic, PCB, local libraries
      mechanical/                 FreeCAD holder source and checkpoints
      integration/                interface dimensions and matched revisions
  <future-project>/               use the same three subfolders when useful
tools/
  cad/                            existing FreeCAD tooling
  electronics/                    add small wrappers after control proof
generated/
  kicad-foundations/              disposable rebuilds, reports and exports
```

Keep `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, custom design rules and project
libraries in ordinary Git. Keep library references project-relative where
possible. Record required standard library versions; preserve custom models
with their sources and licenses. Retained STEP/FreeCAD files already use Git
LFS. Ignore local editor state, locks and automatic backups when the first
project is created. Do not ignore native KiCad source files.

Do not commit an entire installed KiCad library tree. Add a small version record
and executable discovery under `tools/electronics/` when the first wrapper is
needed; support both user-local and system installations plus an explicit path
override. Keep KiCad's Python environment separate from FreeCAD's.

## Handoff contract

KiCad owns circuit connectivity, footprints and the manufactured PCB layout.
FreeCAD owns the holder and surrounding mechanical parts. The integration record
owns the agreed interface: units in mm, origin, axes, board plane, thickness,
outline, mounting holes, connector mating direction, height and cable keep-outs.
Record the transform from board coordinates into the mechanical assembly.

Export the reviewed KiCad board to STEP, import it into a new FreeCAD working
revision, and check the interface. A STEP export is a geometry snapshot; editing
it does not update the schematic or PCB source. Update the owning source and
regenerate after a design change. Missing or inaccurate component models must
remain explicit; a successful export alone does not prove clearance.
[@kicad10Cli]

Record source revisions/hashes, export settings and the matched board/mechanical
checkpoint together. Check electrical rules, PCB rules, geometric clearance and
demonstrated physical fit separately. Start with explicit file exchange; evaluate
StepUp only when repeated outline/placement exchanges justify another dependency.

## Next session: prove control, then teach

1. Create a new foundations project in its own directory. Verify the default
   symbol and footprint tables resolve the selected lesson components.
2. Enable the KiCad API in Preferences > Plugins. Use the official client in a
   separate local environment with a recorded version. Confirm the target editor
   and board path before editing; do not assume the first API endpoint is ours.
3. On a disposable board, read an object's position, move it visibly, read it
   back, undo the change and save/reload. Only then mark live PCB control tested.
4. Demonstrate adding and wiring a symbol in a disposable schematic through the
   GUI. Do not claim schematic IPC control on KiCad 10. If GUI operation is
   unreliable, guide the user's schematic edits while automating board work.
5. Begin the first course concept immediately after this bounded control check.
   Defer a general MCP server, StepUp and larger automation framework.

Never rewrite an open editor's source file behind its unsaved buffer. Reconcile
manual edits before replaying a build or claiming a reproducible checkpoint.
