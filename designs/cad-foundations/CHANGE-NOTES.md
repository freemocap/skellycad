# Course curation — 2026-10-08

- Consolidated four exercises, curriculum and native milestones under
  designs/cad-foundations. Runtime/tooling and disposable outputs remain shared
  at workspace level. No client files accessed or new real-part project created.
- Captured five live FreeCAD documents with saveCopy before moving folders, then
  reopened those session snapshots. Historical checkpoints were not resaved.
- Preserved old documentation in history/documentation-before-cleanup.zip and
  recorded hashes for 33 native files. Kept the original FCBak recovery artifact.
- Replaced stale current-state prose with a course guide, checkpoint map, source
  responsibilities, known limits, and explicit transition instructions.
- Added replay.py: builds any taught endpoint into a unique disposable output
  and unique document without overwriting preserved checkpoints or open work.
- Updated two workspace-relative output paths and added no-overwrite guards to
  the three historical cube scripts. Their original lesson structure remains.
- Verified all 25 replay endpoints and final save/reopen/control behavior;
  see VALIDATION.md. No commit or push performed.

Next action belongs to the user: add the new source files/folder here, then agree
on reconstruction scope. The course is preserved as a reference, not a prerequisite
for more invented exercises.
