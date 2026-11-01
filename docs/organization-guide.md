# Working in SkellyCAD

Start at the [project catalog](../README.md). Choose the project, then the animal
and variant where applicable. Its README identifies the selected checkpoint,
current review candidate, source and matched print package separately.

## File ownership

| Location | Contents |
| --- | --- |
| `src/` | Current editable implementation and configuration for one variant. |
| `references/` | Supplied originals, licenses, provenance and immutable inputs. |
| `anatomy/` | Animal-specific derived anatomy and landmark work shared by variants. |
| `checkpoints/` | Saved native assemblies or matched electronics/mechanics bundles, manifests and evidence. |
| `history/` | Earlier studies and their explanations; links to canonical checkpoints. |
| `studies/` | Active experiments that do not yet belong in the maintained implementation. Create only when needed. |
| `releases/` | Identified portable packages, with exact source assemblies and layout revisions. A package can still be a trial. |
| `generated/` | Named working runs, temporary exports and recovery files. |
| `tools/` | Reusable execution, validation and migration tools. |
| `docs/` | Shared operating instructions and migration evidence. |

Camera modules live under `designs/cameras/`. Eye-tracker assembly, mounting and
targeting code lives under `designs/eye-tracker/shared/`. Keep an animal's anatomy
with that animal, rather than copying it into each hardware variant.

## Variants, revisions and selections

A variant is a meaningful alternative configuration, such as binocular versus
eye + world, or a different board architecture. A changed support or camera pose
is normally a revision of that variant. Routine source edits use Git history.

Use lowercase kebab-case and revision-first directory names, for example
`r043-lowered-cameras`. Pad revision numbers to at least three digits. Preserve
existing semantic IDs and distinct historical series such as A01, E01 and W06.
Use ISO dates for session records. A print layout has its own identity, for
example `r032/l004`, and remains tied to its geometry checkpoint.

Keep one authoritative selected manifest per variant. A root compatibility
selector can redirect to it. A candidate belongs in `review-model.json` until
explicitly selected; a higher revision number is not authorization to promote it.
Some projects have no selected complete assembly. Say so in their README.

Report geometry validation, electrical checks, fabrication status and demonstrated
physical fit separately. Preserve known limitations and withdrawn recommendations.
Keep matched parts together, including captive print-in-place holders.

## Start and finish work

1. Read the owning README and selection/candidate record. Verify the checkpoint
   hash before using it. Read [development](development.md) before CAD work.
2. Put editable code in its existing source owner. Put new working output in
   `generated/<project>/<animal-if-needed>/<variant>/<run>/`.
3. Preserve a new checkpoint for acceptance, a meaningful review or handoff, or
   native work that is not yet reproducible. Record its parent, units, interfaces,
   exact files and hashes. Keep immutable accepted checkpoints unchanged.
4. If another retained design needs a generated file, retain the exact input and
   adjacent required assets before creating that dependency. Record provenance.
5. Update the owning README's open/edit/review/print links and validation scope.
   Follow the CAD save-and-close policy, then run the affected checks.

Keep landing pages short. Put the full chronology in the history index. Preserve
original historical descriptions; label their context rather than appending a
new “current” paragraph above contradictory old instructions.

## Replaying pre-cleanup builders

Historical builders retain their original path assumptions and code. Run them
in an isolated original-layout workspace, not by executing a moved historical
script in the reorganized checkout. This preserves their input hashes and avoids
rewriting frozen design logic merely to change its directory.

From the repository root:

```powershell
python -B tools/migration/replay_cleanup.py prepare --name review
python -B tools/migration/replay_cleanup.py run --name review --runtime freecad --script designs/eye-tracker/mouse/build.py
```

The first command restores the preserved source and generated inputs into
`generated/replay/review/`, verifies their hashes, and adapts embedded references
to this repository's former absolute path in memory during execution. Source
files and evidence hashes remain unchanged. A second
prepare with the same name checks the prepared state; it does not reset edits.
Use a new name for a fresh run. The runner accepts an original script path or a
mapped current path. FreeCAD runs are isolated and preserve the desktop session.

For current variant source edits, prepare a fresh workspace with `--current`
and an explicit source owner. For example:

```powershell
python -B tools/migration/replay_cleanup.py prepare --name e01-review --current --source designs/cameras/ov9281/variants/three-board/src
python -B tools/migration/replay_cleanup.py run --name e01-review --script designs/cameras/ov9281/variants/three-board/src/validate_package.py
```

This overlays existing and newly added files from that owner at their original
logical paths. Nested source owners are included. Other variants remain pinned,
so an E01 check does not accidentally include R11 edits. Repeat `--source` to
include another owner, such as `designs/cameras/ov9281/shared` when editing those
utilities. Omitting `--source` overlays all current owners; use that only for an
intentional combined check. Frozen cross-project preservation checks can reject
such combined edits.

Historical eye-tracker shared dependencies stay pinned. New shared-library
work uses the maintained library in the main checkout and its regression checks.
It is not silently substituted into a historical replay.

Keep useful outputs before discarding a replay workspace. Restoration never
overwrites changed files. The inventory, move map, original sources, generated
inputs, repairs and verification evidence live in
[the cleanup record](migration/repo-cleanup-2026-10-31/README.md).

Mouse Hats and CAD Foundations retain their established paths. Their historical
generated inputs can still be restored with `tools/migration/restore_legacy.py`.
The untouched `old-cad-playground/` remains outside this cleanup.

## Retention and deletion

Check dependencies and unique work before removing a generated file or backup.
A matching filename is not proof of duplicate content. Preserve accepted native
files, supplied assets, licenses, matched bundles and required replay inputs.
Record each cleanup removal and its retained replacement or reproducible source.

Large retained files and archive volumes use Git LFS. Fetch LFS objects before
restoration. Version-control policy remains in [version control](version-control.md).
