# Cleanup verification

The cleanup separates projects, animal variants, current source, checkpoints,
anatomy, references and historical studies. It preserves the selected assemblies
and records review candidates separately. No candidate was promoted to an
accepted design.

## Preservation and navigation

The [full preservation audit](verification.json) verified every one of the
28,073 starting files against the retained archive members, including 19,168
generated inputs. It checked all archive-volume hashes, 65 checkpoint records
(64 distinct native files), and 145 retained matched-package files.
The [final checkout check](verification-quick.json) is recorded separately. A
fresh scoped replay also restored all 28,073 files with hash verification and
passed E01 validation while keeping unrelated variants pinned.
[Restoration record](reports/current-replay-restoration.json),
[source scope](reports/current-replay-workspace.json).

The migration moved 7,778 files. The final camera audit assigned another 183
already-migrated files to their specific owners; those are not additional
starting files. There are 79 intentional source/documentation edits, recorded
with exact before/after hashes in [source-changes.json](source-changes.json).
All other inventoried source bytes remain unchanged at their mapped locations.

The removal ledger contains 16,572 archived generated files, 146 disposable
bytecode files, and two temporary whole ZIPs replaced by identical ordered
volumes. It retains 2,596 local native, recovery, protected historical, changed
or read-only files. Existing desktop ownership was not inferred from filenames.
These counts describe file handling, not a net disk-space saving.

The selected rat R01 had a pre-existing hash mismatch. Its exact selected bytes
were recovered from a matching backup, and the later edited native file was
retained separately. [repairs.json](repairs.json) records both hashes and paths.
Supplied attachments are also preserved in `supplied-attachments.zip`.

Mouse Hats, CAD Foundations and KiCad Foundations keep their historical source
paths and bytes. The original import archive still verifies against all 1,872
migration records. `old-cad-playground/` was not modified.

## Executed checks

| Check | Result and evidence |
| --- | --- |
| Canonical CAD validation | Pass: four course exercises rebuilt, shared mouse geometry compared with the frozen R10 baseline, selected R19 reopened and four matched print groups exported. [CAD report](reports/cad.json), [mesh report](reports/meshes.json). |
| Shared assembly library | Pass: independent camera instances, transformed placements, duplicate-ID rejection and invalid-rotation rejection. [Report](reports/shared.json). |
| Rat reconstruction | Pass: native save/reopen, source anatomy preservation and matched-part comparison. [Report](reports/rat.json). |
| Pupil R08 camera | Pass: exact assets, corrupted-hash rejection, connected material regions, independent instances and transformed optical datum. [Report](reports/camera.json). |
| Targeted R03 recipe | Pass: rebuilt from the relocated recipe, checked aim, ribbon/hardware collisions, fixed interfaces and arm seating; exported the matched parts. [Report](reports/targeting-r03.json). |
| Native review assemblies | Pass: mouse R19, rat R01/R43/W06, Pupil R08, OV9281 E01 and R11 reopened through the shared loader with checkpoint hashes unchanged. [Index](reports/native-models.json). |
| Native KiCad files | Pass: the retained R11 board and both E01 placement boards loaded without changing their hashes. [Report](reports/kicad-native.json). |
| E01 electrical/package verification | Pass: 595 pin connections, 420 electrical contracts, zero ERC violations and zero placement DRC violations; 488 unrouted connections remain. [Original-layout log](reports/cleanup-e01.log), [fresh scoped-current log](reports/current-e01-validation.log). |
| Preserved R11 firmware | Pass: both original build records, source/binary hashes, board bindings, host tests and three synthetic frames. [Report](reports/preserved-r11-firmware-validation.json). |
| Fresh firmware builds | Pass: sensor and synthetic variants compiled from the new source location using the pinned local toolchain. Both new source/binary hash sets verified. [Report](reports/fresh-firmware-validation.json). |
| Historical native replay | Pass: original-layout mouse builder compared successfully with its frozen baseline; task-owned native work was saved and no documents remained open. [Geometry](reports/historical-mouse.json), [session record](reports/historical-session-finalization.json). |
| Regression tests | Pass: 12 restoration/mapping/scoped-overlay tests, 5 selector tests, 12 firmware-host tests, 12 camera-utility tests and 8 bibliography tests: 49 total. |
| Bibliography and navigation | Pass: 208 references, no bibliography errors, and maintained landing-page/guide links resolve. Historical narratives retain their original-layout context. |

The replay checks include refusal to overwrite changed files, archive traversal
rejection, split-volume restoration, new source modules, scoped current-source
overlays and collision rejection before copying. A native hard-exit probe also
confirmed that a task-owned document is saved before its process exits.

The Windows ESP-IDF build stalled at CMake startup inside the sandbox. The same
pinned build completed outside it. FreeCAD emitted cache/ElementMap diagnostics;
the geometry, ZIP integrity, save/reopen and mesh assertions passed. All FreeCAD
checks used isolated code-driven processes and preserved the desktop session.

## Limits and retained design status

- The older R08 firmware checker still finds pre-existing source drift in
  `camera_main.c` and `sdkconfig.defaults`. Its preserved binaries match their
  recorded hashes, but the expected older source hashes were not found in the
  starting inventory or available file history. This was not introduced by the
  move. [Drift record](reports/historical-r08-firmware-drift.json).
- E01 remains an unrouted draft and misses its nominal head-mass target. Neither
  E01 nor R11 is an accepted manufacturing release or demonstrated camera.
- Targeted R03 retains a baseplate/skull intersection finding. Successful aim,
  ribbon and arm checks do not establish anatomical mounting fit.
- Software compilation, native-file identity and geometric validation do not
  demonstrate physical fit, camera capture, electrical performance or safety.
- Every original file was preserved and verified; every historical experiment
  was not rebuilt. Fresh-clone LFS retrieval and physical hardware operation
  were not tested. Installed runtimes remain local and use their existing pinned
  setup procedures.

## Reproduce the checks

From the repository root:

```powershell
python -B tools/migration/verify_cleanup.py
python -B tools/migration/verify.py
./tools/cad/cad.ps1 validate
python -B -m unittest discover -s tools/migration -p test_cleanup.py
python -B -m unittest discover -s tools/cad -p test_selection.py
python -B tools/check_references.py
python -B -m unittest discover -s tools -p test_references.py
```

Use [the working guide](../../organization-guide.md) for historical replay and
scoped current-source checks. The firmware README documents direct builds from
its new location. Useful native replay outputs remain under
`generated/verification/historical-replay/`; disposable restored workspaces are
removed after their verification records are retained.
