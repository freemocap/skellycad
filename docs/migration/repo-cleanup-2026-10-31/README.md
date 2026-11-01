# Repository cleanup — 2026-10-31

The approved cleanup reorganizes projects, animals, variants and history while
preserving native checkpoints and complete replay inputs. Execution and final
verification are recorded here; the original import archive stays unchanged.

- `inventory.json`: starting file hashes, sizes and Git classification.
- `move-map.json`: original and destination paths.
- `checkpoint-catalog.json`: verified native checkpoints and retained destinations.
- `repairs.json`: exact R01 recovery, with the later local edit preserved separately.
- `retained-packages.json`: matched E01 files and corrected W06 print package.
- `archive-volumes.json`: source/generated archive hashes and ordered volume hashes, plus the supplied-attachment archive.
- `baseline-*.json` and `baseline-migration.txt`: pre-existing discrepancies.
- `generated-references.json`: historical consumers of generated paths.

Use `tools/migration/restore_cleanup.py` for hash-verified recovery into a named
workspace under `generated/replay/`. Use `replay_cleanup.py` for an executable
historical workspace. Archive volumes are binary ZIP segments: fetch all volumes
through Git LFS; the restoration tool reads them as one archive.

The original selected rat R01 was recovered from a matching backup. Its later
local edit remains a separately named native file. No candidate was promoted.

[Working guide](../../organization-guide.md) · [Approved plan](../../repository-organization.md)

## Results and maintenance

Read [verification and limitations](verification.md) for the checked workflows.
`removals.json` records removed files and retained replacements.
`retained-local-files.json` records native, recovery, protected, changed and
read-only files kept in place. `source-changes.json` fixes the exact hashes of
intentional source and documentation edits; archived originals remain available.
`navigation-finish-map.json` records the final ownership of camera tooling.

From the repository root:

```powershell
python -B tools/migration/verify_cleanup.py
python -B tools/migration/verify.py
```

The first command reads every archive volume and original member, then checks
current sources, selectors, packages and maintained navigation. `--quick` skips
the archive-byte pass. Full preservation verification is distinct from running
every historical experiment. One-time inventory and migration scripts are audit
records; do not rerun them against the completed layout.

`current-source-owners.json` defines scoped replay overlays, including newly added
source files. Use `--source` with `--current` to keep unrelated variants pinned.

[Execution checklist](CHECKLIST.md)
