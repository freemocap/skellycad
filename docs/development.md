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
four completed course exercises, the shared mouse rebuild against its frozen
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

For the mouse, `designs/eye-tracker/mouse/build.py` composes the shared camera and
mount library using `assembly.json`, then compares the result against frozen R10. `export_print.py` exports the selected
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

### Logitech G502 HERO thumb-button rotation

The rear thumb button (G4) uses **Middle Click** in the existing G HUB `freecad`
application profile. FreeCAD must also use **Blender** navigation, selected from
the navigation menu at the bottom right of its window.

G HUB matches executable paths. Moving the repository or changing the pinned
FreeCAD version can leave the profile pointing at the previous installation.
To restore detection:

1. Open G HUB and select **Profiles > freecad**.
2. Scroll to **Settings > Path**, then select **Add**.
3. Select the running installation's `bin/FreeCAD.exe` inside this repository's
   `.cad-tools/` directory. Keep existing paths if those installations are still used.
4. Keep **Enable profile switching** enabled and the persistent profile set to
   **None** so this assignment applies when FreeCAD is active.
5. Return to FreeCAD, verify **Blender** navigation, then hold the rear thumb
   button and drag in the 3D view to check rotation.

On 2026-10-13, the SkellyCAD FreeCAD executable was added to the existing profile
and Blender navigation was restored. The saved G4 assignment matched the wheel's
middle-click assignment; physical thumb-drag verification remained a user check.
These device settings live locally in G HUB and FreeCAD, outside the repository.

## Shared hardware regression checks

The mouse build compares shared geometry with the preserved R10 baseline. For
the additional two-camera placement and configuration-rejection checks, run
`tools/cad/validate_shared.py` with the pinned FreeCAD bundled Python executable
identified by `tools/cad/toolchain.json`. It uses a hidden test GUI and does not
change the desktop review session. Reports go to `generated/verification/shared/`.

Camera profiles, mount presets and camera instances are described in
[the eye-tracker overview](../designs/eye-tracker/README.md).
