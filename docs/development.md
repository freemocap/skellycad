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

## Design revisions and validation

Use [the organization guide](organization-guide.md) to choose a project, animal
and variant. Its `active-model.json` selects a complete assembly; a separate
`review-model.json` identifies a candidate without promoting it. Root species
selectors redirect to the authoritative variant manifest.

`tools/cad/cad.ps1 validate` rebuilds the four preserved CAD lessons, compares the
historical shared mouse reconstruction to its frozen R10 baseline, and checks
and exports the separately selected R19 complete assembly. Mesh checks use the
same selected export manifest. Reports go to `generated/verification/`.

For additional camera-instancing regression checks, run `tools/cad/validate_shared.py`
with the pinned FreeCAD Python. `tools/cad/validate_rat.py` checks the original
monocular rat against an independently verified R10 reconstruction, not the newer
mouse R19 geometry. Both run in isolated hidden processes.

To inspect a selected or candidate native file without changing it, use the
pinned FreeCAD Python from the repository root:

```powershell
& '.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe' -B tools/cad/model.py designs/eye-tracker/rat/variants/binocular/review-model.json --report generated/verification/rat-r43.json
```

`model.py` accepts `--export` with a fresh directory under `generated/` only when
the manifest explicitly defines matched print groups. Candidate-specific print
layouts still use their recorded exporters; W06 requires the corrected captive
print-in-place package.

Moved historical builders retain their original code and run through the
isolated replay workflow in [the organization guide](organization-guide.md).
Use a fresh replay workspace for a new reconstruction. Preserve inputs and
checkpoints; do not overwrite an accepted checkpoint with a rebuild.

Mouse Hats and CAD Foundations retain their existing source paths. Restore their
older generated inputs with `python tools/migration/restore_legacy.py` when needed.
Historical `CURRENT` notes do not override selected complete-assembly manifests.

## Desktop review and MCP

Keep the running desktop FreeCAD window intact. Reuse an already-open document
when its normalized absolute file path matches the requested review. Do not
create multiple live documents that save to the same physical path. Build new
revisions outside the review session where possible, then open the result once.
Keep only documents needed for the current review. Frozen checkpoints provide
history; open tabs do not.

### Save-and-close policy

Agents must give new working documents a unique native `.FCStd` path under
`generated/` as soon as they contain useful work. Save after each meaningful
edit or successful build, before exports, and before handoff. Save changes to
accepted checkpoints as new revisions, preserving the original files.

Before finishing a CAD task, save and verify every document the task created or
modified. Check that each saved file contains `Document.xml` and passes a ZIP
integrity check; these checks establish file integrity, not geometry or physical
fit. Close finished task-owned documents and temporary comparison tabs after
their saves succeed. Leave only the saved current review and any explicitly
requested comparisons open. Preserve unrelated user work. Report any save
failure and leave the affected document open.

Enable automatic recovery with a 2-minute interval in **Preferences > General >
Document**, with recovery at startup enabled. FreeCAD writes recovery files;
this does not replace the explicit saves above [@freecad114AutoSaver]. The
interval is in minutes, and applying the Document preferences updates the live
timer [@freecad114DocumentPreferences; @freecad114DocumentPreferencesUi].
To apply these settings in a running session, send
`tools/cad/configure_recovery.FCMacro` through `open_in_running.py` as described
below. Verify `generated/session-recovery/recovery-settings.json` reports
`applied_in_running_session: true`; an error means the live setting is unverified.

### Existing session cleanup

For user-requested session cleanup, first save each live version to a unique
recovery filename and verify the saved document. Close a document only after its
backup succeeds. Keep a manifest linking each recovery file to its original
path; never overwrite an accepted checkpoint to clear an unsaved indicator.
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

## Species anatomy workflow

For anatomy audits, landmark review, eye registration, anatomical mounting and print derivatives, follow [the species anatomy workflow](species-anatomy-workflow.md). It separates source evidence, user-reviewed candidate landmarks, camera fitting and physical print validation.
