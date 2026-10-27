# SkellyCAD

**Preferred Pupil Labs eye camera:** [selected complete R08 module](designs/eye-tracker/shared/cameras/pupil-core-eye/README.md), including the notched lens, optical axis and flush TPU ribbon. Use it for new camera geometry; historical species checkpoints remain pinned.

Reproducible CAD designs, reference anatomy, and tools for long-term development.

- [Eye tracker](designs/eye-tracker/README.md): shared tooling and human, mouse,
  rat, and marmoset designs. The mouse starts from the preserved R10 assembly.
- [Mouse Hats](designs/mouse-hats/README.md): original design history and studies.
- [CAD Foundations](designs/cad-foundations/README.md): completed learning course
  with editable checkpoints and safe replay scripts.
- [KiCad Foundations](designs/kicad-foundations/README.md): planned circuit-to-board
  walkthrough and [electronics integration](docs/kicad-integration.md).
- [Development](docs/development.md): setup, validation, exports, and desktop review.
- [Version control](docs/version-control.md): what to retain, ignore, and store with Git LFS.
- [References](CITATIONS.md): citation conventions and evidence in `references.bib`.
- [Migration record](docs/migration/README.md): retained files, exclusions,
  checksums, and restoring historical replay inputs.

## Setup

Windows x64, Git with Git LFS, uv, Windows tar with 7z support, and the Blender
version recorded in `tools/cad/toolchain.json` are required.

```powershell
git lfs install --local
git lfs pull
./tools/cad/bootstrap.ps1
./tools/cad/cad.ps1 smoke
./tools/cad/cad.ps1 validate
```

Keep durable inputs, parameters, checkpoints, and validation evidence under
`designs/`. Fresh builds and exports go to ignored `generated/`. Runtime binaries
and environments are local and reproducible; the dependency lock is retained.

The original `old-cad-playground/` copy remains untouched for migration review.
Active development uses the new root-level directories.
