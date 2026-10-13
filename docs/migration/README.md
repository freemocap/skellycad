# CAD Playground migration — 2026-10-13

SkellyCAD now owns the imported design history, pinned tooling and active
eye-tracker collection. `old-cad-playground/` remains untouched and ignored for
the user's review and later removal. It is not a runtime dependency.

## Retention decisions

| Source material | Destination / treatment |
| --- | --- |
| CAD Foundations | `designs/cad-foundations/`, retaining course checkpoints and replay paths |
| Mouse Hats sources and studies | `designs/mouse-hats/`, retaining supplied CAD assets, revision inputs, settings and evidence |
| Selected R10 assembly | Frozen baseline and independent R09 build input in `designs/eye-tracker/mouse/` |
| Human, rat and marmoset | Separate design folders with reference-asset placeholders |
| Camera/assembly infrastructure | Shared manifest and export helpers; geometric extraction remains incremental |
| Historical generated artifacts | `playground-artifacts.zip`, with checksums and safe restoration to original paths |
| Automatic FreeCAD backups | Archived, rather than mixed into active design folders |
| R02 release | One expanded tree and distribution ZIP; second expanded tree verified identical and omitted |
| Reference photos | 12 unique images under `designs/mouse-hats/references/photos/`; 16 original paths mapped in the inventory |
| Superseded root handoffs | Archived as historical evidence; current workflow lives in `docs/development.md` |
| Edited imported entry points | Originals retained in `original-docs/`; revised hashes recorded in `changes.json` |
| Runtimes, environments and caches | Recreated locally from the pinned toolchain and dependency lock |
| Old Codex configuration, logs and process state | Excluded as machine/session-specific data |

The archive deliberately retains useful historical generated geometry and
experiments conservatively. Some builders consume those files as inputs, even
though the old top-level documentation called all generated output disposable.
Quarantined wrong-baseline exports stay historical; they are not selected models.

## Inventory and replay dependencies

`inventory.json` accounts for 1,872 retained source-file records, including exact
duplicate mappings. There are 840 unique directly retained destination files,
plus archived evidence. Every record includes the original SHA-256 and size.
`changes.json` records the few intentionally revised imported entry points.
Git LFS covers large native assets and the approximately 228 MiB historical archive.

`dependencies.json` audits 281 direct repository-relative Python path literals.
Every audited historical path that existed in the source is present after
restoration. Computed paths are covered by the conservatively retained archive;
this is not a claim that every historical experimental script has been rerun.

Notable dependencies:

- R10 builds from R09. The new mouse design has its own hash-verified R09 input.
- Historical R09 uses `model/`, `rear-arm-r11/` and
  `loop-options-r05/CarrierEmboss.brep`; those paths are preserved.
- Historical T3 and skull-neutral session documents live under `generated/`.
- Legacy `current/build.py` rebuilds R03. The active manifest selects R10.
- Skull/baseplate print lineage remains R03 because the baseplate was unchanged.
- Recorded absolute paths in old validation reports describe past sessions;
  active mouse builders use paths rooted in this repository.

Restore historical generated inputs on a fresh checkout with:

```powershell
python tools/migration/restore_legacy.py
# Or restore only a study:
python tools/migration/restore_legacy.py --prefix generated/mouse-hats/skull-placement/
```

Restoration checks archive-member hashes and skips existing files. Source backups
and old root documents stay archived; the command only restores `generated/`.

## Verification

```powershell
python tools/migration/verify.py
./tools/cad/cad.ps1 doctor
./tools/cad/cad.ps1 smoke
./tools/cad/cad.ps1 validate
```

Completed migration checks:

- Fresh pinned Python environment, FreeCAD extraction and bridge checkout;
  FreeCAD/Python/Blender version checks passed.
- Native parameter edit, FCStd reopen and STEP round-trip smoke check passed.
- Final stages of all four CAD Foundations exercises rebuilt successfully.
- New mouse R10 rebuild matched all five baseline parts with zero measured
  Boolean symmetric-difference volume; skull/eye topology and placements matched.
- Four selected mouse print exports were watertight with consistent winding,
  positive shell volumes, and expected shell counts (two for carrier/holder).
- Selected checkpoint remained byte-identical; migration and copied reference
  assets passed SHA-256 verification.
- Retained imported destination files are not accidentally ignored by Git.

The native run emitted an element-map/hasher diagnostic while loading the
inherited document. Shape validity, geometric comparisons and exports still
passed. Physical fit and motion limitations remain documented in the mouse README.

The recorded native and mesh results are in `validation/`; current reruns write
to `generated/verification/`. Review this record before removing the old copy.
No commit, push, printer submission or change to the existing desktop session
was made during migration.
