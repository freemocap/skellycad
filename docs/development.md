# Development workflow

## Toolchain

Run `tools/cad/bootstrap.ps1` from PowerShell to create a fresh local environment,
verify and extract the pinned FreeCAD archive, and install the pinned bridge.
`tools/cad/toolchain.json`, `.python-version`, and `uv.lock` define the versions.
Set `CAD_BLENDER` when Blender is installed at a different location. Virtual
environments and runtime installations are rebuilt rather than moved.

Commands from the repository root:

```powershell
./tools/cad/cad.ps1 doctor
./tools/cad/cad.ps1 smoke
./tools/cad/cad.ps1 validate
python tools/migration/verify.py
```

`validate` runs an isolated, hidden FreeCAD GUI process for automated checks:
four completed course exercises, the mouse R10 rebuild against its frozen
baseline, and selected print export. It then checks exported meshes using the
tooling environment. It leaves the user's desktop FreeCAD session intact.
Reports go to `generated/verification/`.

## Design revisions

Each active species design selects its complete assembly through
`active-model.json`. Check the recorded hash before use. Keep immutable accepted
checkpoints, source lineage and parameters with explicit units beside the
design. Rebuild into `generated/`; review geometry and interfaces before selecting
a new checkpoint. Git hashes identify source history; checkpoint hashes identify
the exact native document. Large CAD assets use Git LFS.

For the mouse, `designs/eye-tracker/mouse/build.py` rebuilds the inherited R10
ledge change from a durable R09 input. `export_print.py` exports the selected
checkpoint with its matched cap, clip, holder and baseplate. Run these inside
the pinned FreeCAD GUI Python context using `runpy.run_path`, not ordinary Python.
`tools/cad/cad.ps1 validate` exercises both without changing the selection.

The existing Mouse Hats scripts preserve their historical relative paths. To
restore their older generated inputs after a fresh checkout:

```powershell
python tools/migration/restore_legacy.py
```

Restoration preserves existing files. Historical `CURRENT` notes and individual
arm revision numbers do not override an active complete-assembly manifest.

## Desktop review and MCP

Keep the running desktop FreeCAD window and its open-document history intact.
Send a native document or macro through `tools/cad/open_in_running.py`, using
`--expected-pid` with a freshly verified desktop listener PID. This uses the
existing native OpenFile pipe and never launches or closes FreeCAD. The mouse
review entry point is `designs/eye-tracker/mouse/open.FCMacro`.

The scripted RPC runtime is separate from desktop review. The inherited bridge
uses localhost:9875. `start-freecad` refuses to start when that port is busy;
`test-mcp` and `mcp` verify that the endpoint belongs to this repository. If the
CAD Playground runtime owns the port, preserve that session and resolve ownership
before starting SkellyCAD's bridge. The automated `validate` command needs no port.

For an available port, use `tools/cad/cad.ps1 start-freecad`, then `test-mcp`.
Register the optional bridge with
`tools/cad/.venv/Scripts/python.exe tools/cad/register_mcp.py` and reload MCP
servers in Codex. `CAD_PLAYGROUND_ROOT` remains the compatibility environment
variable for historical scripts; its value must be this SkellyCAD root.

Preserve Blender-style navigation. Geometry validity and watertight meshes do
not establish physical fit; record those results separately from print feedback.
