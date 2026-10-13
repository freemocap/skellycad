# Mouse eye tracker

`active-model.json` selects the preserved **MH-T3-EYE-R10** complete assembly.
Use its matched carrier, holder, cap, clip and baseplate together. This retains
the T3 tray/cap rail, deeper-hook cap, flat PCB ledge, revised vertical ledge,
B2 plugward loop, body-mounted arms and neutral camera pose.

- `checkpoints/`: immutable selected R10 native document.
- `inputs/`: hash-verified R09 input required to rebuild the R10 ledge change.
- `parameters.json`: inherited R10 measurements in millimetres.
- `references/skull/`: skull and eye print references, including the separate
  baseplate and original Orca project; see `lineage.json`.
- `build.py`: rebuilds into `generated/eye-tracker/mouse/rebuild-r10/`.
- `export_print.py`: validates and exports the manifest-selected matched parts.
- `open.FCMacro`: opens the selected checkpoint for desktop review.

See [development](../../../docs/development.md) for the pinned runtime and
validation commands. The baseline and R09 input live here; the new mouse build
and export do not read `old-cad-playground/` or generated historical inputs.

## Decisions and remaining work

The selected B loop received physical feedback in the original project. Later
B2, body-junction and ledge changes still need physical fit feedback. Angular
travel, ribbon bend clearance and durability remain open. The body junctions
have no added finishing fillets. The modeled holder gap is approximately
0.333165 mm; the inherited cap contact is approximately 0.002218 mm³.

Skull and eye landmarks describe a geometric placement study. They are not
verified pupil landmarks or an established implantation placement. The skull
print's R03 lineage is intentional: it embeds the unchanged baseplate only.
Its cornea regions use the smaller corneal spheroids. Preserve this evidence
when extracting common hardware and developing additional camera arrangements.

[Original history](../../mouse-hats/INDEX.md) ·
[Skull repair and registration](../../mouse-hats/skull-placement/README.md) ·
[Skull print workflow](../../mouse-hats/skull-print/README.md)
