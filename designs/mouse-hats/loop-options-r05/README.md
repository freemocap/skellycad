# R05 loop-space comparison

See [PRINT-NOTES.md](PRINT-NOTES.md) for the A/B/C comparison and printing files.

`build.py` runs in pinned FreeCAD GUI. `settings.json` pins the complete R04
checkpoint and all dimensions in mm. `geometry.py` is the R04 geometry routine
with variable curve handles. The source socket BRep and original emboss BReps
are saved here; emboss shapes are removal tools only, never model baselines.
`prepare.py` records how the parameter and routine snapshot was made; ordinary
replay uses `build.py` directly without refreshing the baseline.

Native files `R05-A.FCStd`, `R05-B.FCStd`, `R05-C.FCStd` are self-contained.
`R05-ABC-comparison.FCStd` displays the labeled alternatives together.
`validation.json` records geometry checks and dimensions; `print-validation.json`
records independent checks of every STL. Exports and the printable ZIP live in
`generated/mouse-hats/loop-options-r05/`.
