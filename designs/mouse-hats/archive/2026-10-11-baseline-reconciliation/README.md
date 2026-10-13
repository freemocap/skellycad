# CAD playground

Workspace for reproducible FreeCAD learning and explicitly scoped design work.
Start with [HANDOFF.md](HANDOFF.md) and [TRANSFER-STATUS.md](TRANSFER-STATUS.md).

## Preserved course

[CAD foundations](designs/cad-foundations/README.md) contains the completed
learning exploration: box dependencies, sketches, fit coupons, a fictional camera
bracket, assemblies, motion, exploded views, tool access and tolerance studies.
Its checkpoint history is preserved. Fresh replay builds go to `generated/`.

The user will add a new folder and source files for the next real-part project
in this same workspace. Wait for those files and the scope discussion. Do not
search the old DF checkout or import its models on that basis alone.

## Runtime

Run these from this directory in PowerShell. If the local runtime already exists,
check it rather than starting another process on port 9875.

```powershell
./tools/cad/cad.ps1 test-mcp
./tools/cad/cad.ps1 show-freecad
# Only if it is not running:
./tools/cad/cad.ps1 start-freecad
```

For a new machine, use `./tools/cad/bootstrap.ps1`, then
`./tools/cad/cad.ps1 doctor` and `./tools/cad/cad.ps1 smoke`.
Bootstrap needs Windows x64, Git, uv, Windows tar with 7z support, network access,
and installed Blender. Versions/checksums are in `tools/cad/toolchain.json`;
Python packages are locked. Do not move virtual environments or the pinned runtime.
Register MCP with `./tools/cad/.venv/Scripts/python.exe tools/cad/register_mcp.py`.

| Folder | Purpose |
| --- | --- |
| `designs/cad-foundations/` | Curated tutorial, editable checkpoints, recipes and history |
| `designs/` | Design sources and retained artifacts |
| `generated/` | Disposable exports, replay builds and verification reports |
| `tools/cad/` | Shared pinned runtime setup and inspection tools |
| `.cad-tools/` | Ignored local runtime, dependencies and logs |

Save documents before `./tools/cad/cad.ps1 stop-freecad`.
This is part of the parent Git repository; scope changes here. Nothing has been
committed or pushed by this cleanup.
