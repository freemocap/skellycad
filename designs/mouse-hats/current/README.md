# Preserved Mouse Hats baseline

`active-model.json` selects **MH-T3-EYE-R10**, with its matched Carrier, Holder,
Cap, Clip and Baseplate. It is the final imported complete assembly; older
study revision numbers and historical CURRENT notes are not assembly selectors.

New development starts in [the mouse eye tracker](../../eye-tracker/mouse/README.md).
This folder preserves the original checkpoint lineage and historical entry points.

The selected builder is `../side-ledge-r10/build.py`; `current/build.py` rebuilds
R03 only. Export the selected legacy baseline with `export_print.py` in pinned
FreeCAD. Exports go to `generated/mouse-hats/active/print-r10/`.

[R10 parameters and decisions](../side-ledge-r10/README.md) ·
[Validation](validation.json) · [Source/history index](../INDEX.md) ·
[T3 reconciliation](RECONCILIATION.md)

Native and mesh checks are recorded; later physical fit and angular travel are
still unverified. The superseded accumulated README is retained in
`docs/migration/original-docs/designs/mouse-hats/current/README.md` at the repo root.
