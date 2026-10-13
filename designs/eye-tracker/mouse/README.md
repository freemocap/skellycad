# Mouse monocular eye tracker

**Selected checkpoint: ET-MOUSE-MONO-R01.** This is the first mouse assembled
from the shared hardware library. It reproduces the Mouse Hats **MH-T3-EYE-R10**
geometry within the recorded CAD tolerances, with the same skull, eyes, baseplate,
PCB retention, cap, ribbon-loop supports and holder pose.

## Open and inspect

`open.FCMacro` opens the selected checkpoint in FreeCAD. Follow the existing
window procedure in [development](../../../docs/development.md). The document
contains a mouse-anatomy group, a baseplate group, and a named primary-eye-camera
group. The matching cap and PCB envelope are present but hidden initially, as
in the reference model; select them in the tree and press Space to inspect them.

The separate shared-hardware catalog is an exploded inspection view. Its
separated parts must not be exported as an assembled print layout.

## The files you will normally edit

| File | What you change there |
| --- | --- |
| `assembly.json` | Camera instances, their roles, camera/mount selections and whole-station placement. Currently one eye camera. |
| `anatomy.json` | Mouse reference anatomy, baseplate input and inherited target information. |
| `build.py` | Short entry point into the shared builder and mouse comparison check. |
| `active-model.json` | Selects a verified saved complete assembly for review and printing. |

`build.py` writes a fresh native model, manifest and comparison report to
`generated/eye-tracker/mouse/shared-r01/`. It does not overwrite the selected
checkpoint. The shared builder uses extracted assets, not the old whole assembly.
The comparison check separately opens frozen R10 to detect unintended changes.

`export_print.py` exports the selected checkpoint to
`generated/eye-tracker/mouse/print-shared-r01/`: carrier-and-holder together,
matching cap, camera clip and baseplate. Preserve the carrier/holder's relative
positioning for its print-in-place pair.

## Verification and history

`validation/shared-r01.json` records native comparison and two-instance tests;
`validation/shared-r01-meshes.json` records watertight exports. All five printed
parts have zero detected Boolean difference from R10. Carrier volume integration
differs by about 0.000479 mm³ after decomposition/refusion, within the recorded
0.001 mm³ tolerance. Anatomy topology/placement and sightline guides match.

`checkpoints/MH-T3-EYE-R10.FCStd` and its saved manifest remain the original
reference. `rebuild_legacy_r10.py`, `parameters.json` and the R09 input preserve
the earlier ledge-only replay; they are not the shared assembly recipe.
`shared-r01-lineage.json` records the new recipe and extracted input hashes.

The selected B loop received physical feedback in the original project. Later
B2, body-junction and ledge changes still need fit feedback. Angular travel,
ribbon bend clearance and durability remain open. The body junctions have no
added finishing fillets. The inherited holder gap is about 0.333165 mm and cap
contact about 0.002218 mm³.

Skull/eye targets remain geometric proxies, not verified pupil landmarks or an
established implantation placement. The separate skull print retains its R03
lineage because its embedded baseplate was unchanged.

[Collection overview and rat plan](../README.md) ·
[Original history](../../mouse-hats/INDEX.md) ·
[Skull print workflow](../../mouse-hats/skull-print/README.md)
