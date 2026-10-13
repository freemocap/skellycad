# Version-control policy

Keep the repository sufficient to reproduce the selected complete assembly and
recover meaningful design history. Use `.gitignore` for disposable local files
and `.gitattributes` for retained large assets.

| Material | Treatment |
| --- | --- |
| Build scripts, parameters, manifests, documentation, dependency locks and project skills | Ordinary Git |
| Supplied CAD/anatomy sources, accepted checkpoints and required binary inputs | Git LFS |
| Historical release packages and the frozen migration archive | Git LFS |
| Root `generated/`, runtime installations, virtual environments and caches | Ignored; rebuild or restore locally |
| Original `old-cad-playground/` copy | Ignored; migration evidence lives in retained files and the archive |
| Editor state, process logs, local credentials and new automatic CAD backups | Ignored |

The initial import is approximately 696 MiB before Git compression and LFS
deduplication: 5.5 MiB of ordinary files and 691 MiB of LFS-managed assets.
These are audit measurements, not an upload-size or account-quota guarantee.

The largest retained items are the 228 MiB historical artifact archive and a
172 MiB supplied Fusion source. Keep both for the initial baseline. The archive
contains historical replay inputs as well as preserved experiments; removing it
would break the documented restoration workflow. The Fusion source preserves
editable source information beyond its STEP export. Two supplied `.blend1`
snapshots remain explicit historical exceptions to the automatic-backup rule.

Keep the migration archive frozen. Each changed LFS file version consumes its
full size in hosted storage, so do not repack it on every build. See
[GitHub's LFS storage and bandwidth guidance](https://docs.github.com/en/billing/concepts/product-billing/git-lfs).
Put new replay inputs beside their design and send new disposable exports to
root `generated/`. Evaluate future distribution packages for release attachments
rather than accumulating redundant ZIPs in the source tree.

Avoid a blanket rule that ignores every nested `generated/` folder: some supplied
historical folders contain durable inputs under that name. Similarly, do not
ignore all STL or STEP files; reference anatomy and source geometry use them.

## Before the first push

1. Run `python tools/migration/verify.py` to verify retained migration evidence.
2. Stage the intended repository files, then inspect the staged file list and
   `git lfs ls-files`. Confirm the large retained assets have LFS pointers.
3. Commit the baseline and push it with Git LFS enabled. Hosted LFS availability
   and the repository owner's remaining allowance have not been checked locally.
4. Verify a fresh clone can fetch LFS objects, pass the migration verifier and
   rebuild the mouse design before deleting the original local playground copy.
