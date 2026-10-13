# CAD foundations: box to adjustable camera bracket

A preserved, code-assisted FreeCAD exploration for a learner comfortable with
Python and geometry. All models are original teaching examples using fictional
hardware. Work through [CURRICULUM.md](CURRICULUM.md) one meaningful step at a time.

## Start here

1. Use the pinned runtime from the workspace root (see ../../README.md).
2. Open a saved checkpoint to inspect its tree and properties, or use replay.py
   to build a new copy. Do not overwrite the supplied checkpoints.
3. Explain the relevant code and predict the result before making a change.
4. Inspect the visible result, check dimensions/solid validity, and record what
   changed. Reconcile manual edits before claiming a reproducible build.

| Exercise | Learn | Useful endpoint |
| --- | --- | --- |
| [workflow-cube](workflow-cube/README.md) | Dimensions, expressions, Boolean cut, mesh export | 04-centered-hole.FCStd |
| [practice-mount](practice-mount/README.md) | Constrained sketch, Pad/Pocket, dependent holes, chamfer vs fillet | checkpoints/07-top-chamfer.FCStd and 08-top-fillet.FCStd |
| [fit-coupon](fit-coupon/README.md) | Nominal size, diametral clearance, embossed labels | checkpoints/02-embossed-labels.FCStd |
| [practice-camera-bracket](practice-camera-bracket/README.md) | Assembly references, adjustment, access, exploded view, tolerance study | checkpoints/13-screw-stack-study.FCStd |

## Safe fresh builds

Run this in FreeCAD's Python console or through the local synchronous MCP
execute_code tool, not the separate tooling Python interpreter:

```python
from pathlib import Path
import os, runpy
course = Path(os.environ['CAD_PLAYGROUND_ROOT']) / 'designs/cad-foundations'
replay = runpy.run_path(str(course / 'replay.py'))
doc = replay['main']('practice-mount', 'chamfer')
```

Each call creates a uniquely named document and saves into a unique directory
under generated/cad-foundations. Existing documents and supplied checkpoints
are preserved. Outputs there are disposable; use Save As into your own design
folder to retain an experiment. `STAGES` in replay.py lists supported endpoints.
For the complete bracket use `main('practice-camera-bracket', 'complete')`.
Replay builds an endpoint from scratch; it does not animate the entire lesson.

The four chapter folders retain the actual source and historical step scripts.
Use model.py functions for focused incremental teaching. Legacy step scripts
expect specific document names and ordering, and usually fixed checkpoint names;
use them only in a working copy. replay.py is the recommended fresh-build route.

## What is preserved

- Numbered native checkpoints and per-chapter CHANGE-NOTES.md: lesson history.
- Scripts and explicit parameters: reproducible specification.
- session-snapshots/: five live documents captured before cleanup, plus index.json.
  These may include interactive/display state beyond the named checkpoints.
- history/checkpoint-sha256.json: preservation inventory.
- history/documentation-before-cleanup.zip: original documentation before consolidation.
- [VALIDATION.md](VALIDATION.md): verification and known limits.

No printer calibration, physical fit or load testing was performed. The user's
printing workflow was already familiar and skipped. Assembly motion is scripted;
we did not set up a native joint solver or dynamic/friction simulation. The goal
is learning how to encode and inspect design intent, not distributing a finished
camera product. Native checkpoints open without rebuilding; coupon regeneration
needs the configured Arial Bold font, which is not redistributed.
