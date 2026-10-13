# Preservation and replay verification — 2026-10-08

## Cleanup checks completed

- All 25 endpoints listed in replay.py rebuilt in the pinned FreeCAD GUI from
  the relocated chapter folders: 4 cube, 8 plate, 2 coupon and 11 bracket stages.
- Existing geometry/constraint/volume checks ran within the chapter builders.
  Each resulting document was also checked for Error/Invalid object states.
- Complete bracket replay saved and reopened successfully. Motion, lower-tool
  access, and explicit leaf visibility checks passed after reopening.
- Native exploded separation was checked at 6, 3 and 0 mm against independently
  translated source shapes, including after saving/reopening the complete model.
- Tolerance study enumerated all 32 endpoint combinations per candidate and
  compared nominal current-screw protrusion to the modeled geometry.
- All 22 course Python sources parsed. The two scripts that inferred workspace
  location from folder depth now find tools/cad/toolchain.json in an ancestor.
- SHA-256 verification confirms all 33 native checkpoint/recovery/session files
  match history/checkpoint-sha256.json after relocation and replay checks.
- Five live documents were copied before relocation. The session snapshots are
  separate from historical checkpoints; the live session was reopened from them.

Fresh results and a machine-readable run list are under the disposable workspace
generated/cad-foundations directory. To repeat, load replay.py in the pinned GUI
and call main(lesson, stage) for entries in STAGES. Run stack_study.py using the
separate tools/cad/.venv/Scripts/python.exe for arithmetic-only checks.

## Scope of evidence

This cleanup exercised endpoint builds, not every legacy interactive runner or
every possible parameter combination. Historical session checks are described
in chapter CHANGE-NOTES.md; they are distinct from the checks rerun above.
Source snapshots need their documented refresh calls after edits. There is no
automatic audit of every interactive action and no complete joint/force solver.

No physical print, fit, strength, vibration or clamp-friction tests were done.
Fictional tool/camera/fastener dimensions are not manufacturing specifications.
The coupon font is a local dependency; it is not bundled. Historical checkpoint
11 intentionally preserves a display bug corrected by checkpoints 12 and 13.

## Reusable preservation check

From the workspace root, with tooling Python:

```python
from pathlib import Path
import hashlib, json
course = Path('designs/cad-foundations')
manifest = json.loads((course / 'history/checkpoint-sha256.json').read_text())
for relative_path, expected in manifest.items():
    assert hashlib.sha256((course / relative_path).read_bytes()).hexdigest() == expected
```

Do not save over these preserved artifacts if you want this manifest to remain
valid. Save new work to a new filename or use replay.py.
