# 1. Workflow cube

Final checkpoint: **04-centered-hole.FCStd**, a 24 × 20 × 36 mm block with a
centered 8 mm through hole. No physical print was performed.

| Historical script | Inputs | Checkpoints |
| --- | --- | --- |
| build.py | parameters.json | 01-cube.FCStd (20 mm cube) |
| 02-link-height.py | 02-parameters.json | 02-linked-height.FCStd (height = length × 1.5) |
| 03-centered-hole.py | 03-parameters.json | 03-resized-block.FCStd, 04-centered-hole.FCStd |

Use ../replay.py stages `cube`, `linked`, `resized`, `hole` for safe fresh builds.
The historical scripts require WorkflowCube and the stated order; run only in
a working copy without the named checkpoints. They now refuse existing outputs.

Inspect Cube.Height's expression and BlockWithHole.Base/Tool. A native document
retains that relationship; STL contains triangles, without embedded units/history.
export_mesh.py expects a document named WorkflowCube with the reviewed final cut;
it writes generated/workflow-cube under the workspace root. Import STL as mm.
The original mesh inspection passed; slicing/printing was deliberately skipped.
See CHANGE-NOTES.md for historical operations and checks.
