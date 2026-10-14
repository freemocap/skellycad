# SkellyCAD working context

When research or external technical sources inform a change, follow CITATIONS.md:
add the source to references.bib, cite its key beside the supported claim, record
review scope and run the bibliography checker and its tests before handoff.

Before CAD setup, builds, exports or desktop review, read docs/development.md.
For eye-tracker work, read designs/eye-tracker/README.md and the species README.
Use that design's active-model.json to select a complete assembly and verify its
checkpoint hash before geometry changes or exports. Keep matched parts together.

Preserve supplied assets and accepted checkpoints. New revisions go beside the
baseline, with explicit units, lineage and interface validation. Historical
Mouse Hats and CAD Foundations remain replayable at their existing paths.

For migration audits or historical replay inputs, read docs/migration/README.md.
The old-cad-playground folder is the untouched import source; the user will
remove it after reviewing the migration. Work from the new repository paths.

For new or revised technical documentation and agent instructions, read
.agents/skills/clear-technical-writing/SKILL.md. Use its Google-style default,
with its precision check for setup, build, validation, export, and assembly
procedures. Use the full STE profile when the user or project requests it.
Keep discussion and design rationale natural and explanatory.

Use checkpoint, complete assembly, and matched parts consistently with the
design records. Distinguish the selected checkpoint from the latest revision,
and geometry validation from demonstrated physical fit. Preserve units,
identifiers, uncertainty, and checkpoint lineage. Apply editorial changes to
new writing and requested revisions; preserve historical records and accepted
checkpoints.

For camera-to-eye placement, species adaptation, or ribbon/support refitting,
read docs/eye-tracker-targeting.md. Use an explicit targeting recipe and validate
aim, fixed interfaces, ribbon collisions, arm seating and anatomy separately.

For new Pupil Labs eye-camera geometry or camera mock-ups, read
`designs/eye-tracker/shared/cameras/pupil-core-eye/README.md` and use its
`active-model.json` selection through `shared.camera.add_camera`. Verify asset
hashes and preserve the optical datum with the complete module. Existing species
checkpoints retain their selected geometry; adaptations require a new revision.
