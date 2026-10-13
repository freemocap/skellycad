# R02 release tooling

Frozen deliverable: ../../../releases/mouse-hats-r02 (from playground root:
releases/mouse-hats-r02). Begin with its README and START-HERE.pdf.

build_assembly.py creates five named solids from accepted R02, without changing
geometry. export_release.py runs in FreeCAD GUI for AP242, names and colors.
verify_step.py runs with pinned FreeCAD Python; records deep-check warnings rather
than misreporting a clean test. snapshot.py copies sources/checkpoint inputs.
build_guide.py runs with reportlab/Pillow; rendered PDF pages were visually checked.

Preserve released files. Use a new revision for subsequent geometry changes.
No commit, printer submission or slicer configuration is part of this release.
