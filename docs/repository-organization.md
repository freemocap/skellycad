# Repository cleanup plan

Proposed on 2026-10-31. This replaces the rat-only proposal with a repository-wide
plan. No design files have been moved or deleted. The directory names below are
proposed destinations, not existing paths or runnable instructions.

## Outcome and reasoning

Make the repository understandable without an agent: choose a project, choose an
animal and variant when relevant, then find what to open, edit, review or print.
Keep current work small and visible. Preserve useful history without making it
compete with current work.

The main problem is mixed responsibilities, not simply disk usage. A variant is
an alternative configuration we intend to distinguish, such as binocular versus
eye + world. A revision is a change within that configuration. An anatomy study
is evidence or an input; a print layout is a manufacturing arrangement of a
specific assembly. These should not all appear as sibling projects.

OSHWA recommends an overview, editable original files, auxiliary manufacturing
files, a BOM and assembly instructions. Stanford recommends consistent names,
directory structure and a top-level README. These support a clear front door
and explicit file roles, not a particular mandatory CAD layout.
[@oshwaSharingPractices; @stanfordDataOrganization]

Git records routine source edits. Native checkpoints preserve meaningful saved
assemblies, especially interactive work that cannot yet be reproduced. LFS
handles retained large binaries; it does not solve navigation. Distribution
bundles can eventually use tagged releases, with their LFS contents verified.
No publishing or Git-history rewrite is part of this cleanup.
[@githubAboutLfs; @githubAboutReleases]

## Repository-wide findings

The counts below describe local files on 2026-10-31, including untracked work and
some ignored files. They exclude directories named `__pycache__`, `.venv`,
`managed_components`, and `.git`. They are orientation measurements, not a
complete retention inventory or a promised storage saving.

| Current area | Files | What needs attention |
| --- | ---: | --- |
| `designs/eye-tracker` | 1,297 | Mouse and rat mix anatomy, assembly revisions, print layouts and selectors; shared camera assets also contain their own studies. |
| `designs/eye-camera-ov9281` | 1,550 | Electronics, firmware, packaging and mechanical work must remain matched; R08 baseline, R11 candidate and three-board E01 draft are different states. |
| `designs/eye-camera-og0tc` | 39 | Historical camera direction; README retains several formerly current recommendations. |
| `designs/enclosure` | 44 | Six revision folders and no project README; R06 hardware recommendation is explicitly withdrawn. |
| `designs/kicad-foundations` | 70 | Teaching route and example artifacts should be easy to find separately from product engineering. |
| `designs/cad-foundations` | 78 | Preserved lessons, checkpoints and replay scripts; existing paths are protected. |
| `designs/mouse-hats` | 484 | Preserved source/history collection; existing paths and replay inputs are protected. |
| `tools`, `docs`, `releases` | Scope reviewed | Keep executable tooling, operating guidance, migration evidence and packaged artifacts distinct. |

The root README omits the enclosure and both camera-development projects.
Several READMEs prepend new status notes while leaving obsolete current-state
instructions below them. Navigation needs rewriting as well as folder moves.

Rat alone contains 65 immediate directories and 766 files excluding caches,
about 968.9 MiB. SHA-256 comparison found 17 duplicate groups with 29 extra
byte-identical copies, mostly validation records and some scripts. Most of its
complexity survives simple deduplication.

The rat historical R01 file does not match `active-model.json`'s recorded hash.
R43 and W06 native files match their review-manifest hashes, but live under
ignored `generated/`. R43 also consumes sibling BREP files from R42's generated
output. OV9281's R11 working-review manifest likewise names generated native
files and separately points to a preserved snapshot. Generated files therefore
need dependency and snapshot checks before deletion; their folder name alone
is not evidence that they are disposable.

## Proposed full structure

Keep the familiar `designs`, `docs`, `tools`, `releases`, and `generated` roots.
Group camera projects together. Keep animals directly under `eye-tracker` to
avoid an extra `species/` level. Each project README acts as its catalog.

```text
skellycad/
  README.md                         # All projects and their current status
  AGENTS.md                         # Short operating rules, links to guidance
  CITATIONS.md
  references.bib
  LICENSE
  .gitignore
  .gitattributes
  .agents/skills/                   # Retained project skills

  designs/
    eye-tracker/
      README.md                     # Animal/variant comparison and entry points
      shared/                       # Reusable assembly, mounts, targeting, optics code
        cameras/                    # Compatibility adapters, no second camera asset store
        mounts/
        targeting/
      mouse/
        README.md
        references/                 # Original anatomy, provenance and licenses
        anatomy/                    # Derived registration/landmark studies and selections
        variants/
          monocular/                # Common variant structure shown below
        history/                    # Cross-variant and historical reconstruction records
      rat/
        README.md
        references/
        anatomy/
        variants/
          monocular/
          binocular/
          eye-world/
        history/                    # Unassigned concepts and cross-variant history
      marmoset/
        README.md                   # Explicitly: no complete assembly selected
        references/
        anatomy/                    # Includes skull print derivatives and their status
      human/
        README.md                   # Explicitly: placeholder
        references/

    cameras/
      README.md                     # Camera models and development projects
      pupil-core-eye/                # Complete measured mock-up and optical datum
      pupil-core-eye-inherited/      # Historical approximate fit profile
      ov9281/
        README.md
        references/                 # Licensed inputs and provenance
        shared/                     # Only code/assets actually reused across variants
        variants/
          slim-flex/                # Includes preserved R11 candidate lineage
          three-board/              # Includes architecture/electrical draft lineage
        history/                    # Earlier common architecture/optics investigations
      og0tc/
        README.md                   # Historical direction, linked to OV9281
        history/                    # Preserved concepts and supporting records

    enclosure/
      README.md
      src/                          # Current editable frame/capture configuration
      references/
      studies/                      # Open investigations, only while active
      checkpoints/
      history/                      # r001-starter-cube ... r006-usb-baseline

    mouse-hats/                     # Existing paths retained; indexed as historical
    cad-foundations/                 # Existing paths retained; indexed as learning
    kicad-foundations/               # Keep lesson URLs and example organization

  docs/
    repository-organization.md      # This proposal and migration decisions
    organization-guide.md           # Working rules, created during implementation
    development.md                  # Setup, builds, session ownership, save/close
    version-control.md              # Git/LFS/retention policy
    eye-tracker-targeting.md
    species-anatomy-workflow.md
    kicad-integration.md
    migration/                      # Existing import evidence stays in place
      repo-cleanup-2026-10-31/       # Inventory, move map, checks, unresolved items

  tools/
    cad/                            # FreeCAD runtime, bridge and verification tools
    electronics/                    # KiCad/electronics tooling
    migration/                      # Existing replay tools plus cleanup verifiers
    check_references.py
    test_references.py

  releases/
    README.md                       # Distribution index with status and source hashes
    mouse-hats-r02/                  # Existing package retained
    MouseHats_R02-release.zip        # Existing distribution artifact retained
    clear-writing-v1/               # Existing tooling package retained and labeled
    clear-writing-v1.zip
    <project>/<variant>/<revision>/<package>/  # Future packages only

  generated/
    <project>/<species-if-needed>/<variant>/<run>/
    verification/
    session-recovery/

  .cad-tools/                       # Local runtimes; keep working installation
  .codex-remote-attachments/         # Local supplied material; audit provenance first
  .idea/                            # Local editor state; ignored
  old-cad-playground/               # Untouched import source; user controls removal
```

This is an ownership map, not a request to create empty folders. A human or
marmoset assembly variant is added only when that design exists. Enclosure does
not need a `variants/` layer until genuinely distinct configurations exist.
Learning projects stay in their established locations; the root README groups
them visually without breaking their paths.

### Common variant structure

```text
variants/binocular/
  README.md                         # Open/edit/review/print links and limitations
  active-model.json                 # Selected complete assembly; never guessed
  src/                              # Current editable scripts, recipes and native sources
  checkpoints/
    r043-lowered-cameras/
      assembly.FCStd                # One canonical native assembly
      manifest.json                 # Identity, hashes, parent, inputs, units, matched parts
      validation/                   # Evidence for this exact saved assembly
      preview.png
  studies/                          # Named active experiments; omit when unnecessary
  history/
    README.md                       # Ordered index of purpose, outcome and lineage
    r041-clear-view/                # Preserved study code/notes; links to checkpoints
    r042-orthogonal-arms/
```

For OV9281 variants, `src/` can contain `electronics/`, `mechanical/`,
`firmware/`, and `integration/`. A checkpoint manifest identifies the matched
schematics, PCB projects, local libraries, mechanical assembly, firmware source
revision, configuration and required build artifacts. A firmware directory is
shared only when the variants actually use the same maintained implementation.
Do not merge incompatible board contracts merely to reduce duplication.

A checkpoint folder and history folder do not both get a copy of the same
assembly. History explains the work and links to the canonical checkpoint.
A distribution package is an intentional, separately identified copy for use
outside the source tree. Native current source files may be editable working
copies; accepted checkpoint files are immutable.

## What moves, stays, or can be removed

| Material | Proposed treatment and reason |
| --- | --- |
| Animal-specific anatomy sources | Keep with the animal, preserving original bytes, licenses, units and provenance. |
| Derived anatomy and landmark studies | Group under that animal's `anatomy/`; preserve selections and rejected-study labels. Do not duplicate per hardware variant. |
| Mouse/rat assembly studies | Assign to verified variant lineage, then move into revision-first history/checkpoints. Do not classify from names alone. |
| Pupil camera assets | Move canonical profiles and complete module to `designs/cameras/`; keep `shared.camera.add_camera` as the supported loader and preserve historical geometry selections. |
| OV9281 and OG0TC project roots | Group under `designs/cameras/`; retain existing identifiers and historical records. Map OV9281 common ancestors separately from its alternatives. |
| Current reusable code | Maintain in one appropriate shared module, with regression checks for affected consumers. Consolidation is a separate step after path migration. |
| Repeated per-revision scripts | Preserve required historical replay code; move routine future edits into Git history. Do not assume similarly named scripts are equivalent. |
| Accepted checkpoints and required native/BREP inputs | Preserve byte-for-byte, with complete dependency sets and hashes. Promote unique generated inputs into retained storage before cleanup. |
| Print/manufacturing packs | Keep source checkpoint, matched parts, print-in-place constraints, layout identity, slicer settings and validation together. Explicitly mark superseded packs. |
| Native KiCad projects | Keep schematics, boards, project settings and needed libraries together; preserve contracts with firmware and CAD. |
| Reports and previews | Keep evidence/previews associated with meaningful checkpoints; remove reproducible intermediate copies only after reference checks. |
| Temporary trials, caches, logs, automatic backups | Removal candidates after dependency, recovery and reproducibility checks. A backup with unique edits is retained work. |
| Existing release trees and ZIPs | Preserve initial historical packages; index their purpose. Do not assume expanded package plus ZIP is accidental duplication. |
| Mouse Hats, CAD Foundations, migration archive | Keep paths and frozen content; improve navigation around them. Do not repack the frozen archive. |
| Skills, environments and attachments | Keep project skills and working tools. Audit attachments for unique supplied inputs before any cleanup; do not edit installed/global skills. |
| `old-cad-playground/` | Leave untouched; removal remains the user's existing migration decision. |

No directory-wide deletion of `generated/` is proposed. No flattening of matched
assemblies, silent checkpoint promotion, rewriting of accepted records, or
renumbering of semantic IDs is part of organization work.

## Working guidance to adopt

The following rules become `docs/organization-guide.md` during implementation,
with a short link from `AGENTS.md`. They are proposed here so the policy and
folder changes can be reviewed together.

1. **Choose ownership before writing.** Name the project, animal if applicable,
   variant, and whether the work is source, reference, experiment, checkpoint or
   output. Extend an existing home when it already fits.
2. **Use a variant for a configuration, not an edit.** Camera role/count or a
   materially different board architecture can justify a variant. A lowered
   camera or revised support is normally a revision of that variant.
3. **Use sortable directory names.** Lowercase kebab-case; revision first with
   at least three digits, such as `r043-lowered-cameras`. Preserve distinct
   historical series: `a001-architecture` and `e001-electrical-draft` remain
   separate, and W06 can retain `w006` within eye-world history. Preserve semantic
   checkpoint identifiers verbatim. Use ISO dates for session records.
4. **Separate assembly revision from print layout.** For example, an R32 layout
   package can be `r032/l004`; changing orientation does not invent new geometry.
5. **Keep status explicit.** A README distinguishes selected checkpoint, current
   review candidate and available manufacturing package. Also report validation
   scope and demonstrated physical fit separately. Use “none” when no selection
   exists. Highest revision is never a selection rule.
6. **Keep selection authoritative in one place.** Variant manifests own assembly
   selection. Species/project pages summarize and link to them. Existing root
   selectors become explicit compatibility redirects only after their consumers
   support redirects; retain the old behavior until that migration is verified.
   Candidate and package records link by checkpoint ID/hash rather than copying
   another full selection manifest.
7. **Make the README a short entry point.** Give a description, representative
   preview when available, status, what to open/edit/print, and history link.
   Move superseded “current” prose to labeled history without changing its meaning.
8. **Use Git for ordinary edits.** Create a frozen checkpoint for acceptance,
   meaningful review, handoff, or otherwise irreproducible native work. A new
   prompt, view angle, export or minor script edit does not require a copied tree.
9. **Treat generated inputs as a retention defect.** Working outputs go to a
   named run under `generated/`. Before another retained design depends on one,
   preserve the exact required inputs under checkpoints/references and record
   hashes. Keep recovery files until their useful work is reconciled.
10. **Reuse by reference and declared interface.** Record units, coordinate
    frames, optical datums and compatible revisions. Reference an immediate
    parent manifest plus hash rather than recursively copying its full ancestry.
    Existing frozen manifests stay intact; normalize through new indexes.
11. **Record evidence with its artifact.** Report source/tool versions, checks,
    limits, lineage and matched-part relationships. Mesh validity is not physical
    fit; ERC/DRC success is not a demonstrated camera or fabrication approval.
12. **Finish by checking navigation and preservation.** Update the owning README,
    validate manifest paths/hashes and links, run affected checks, and follow the
    existing CAD save-and-close policy whenever native documents are touched.

## Execution plan and completion gates

The scope is the whole repository from the start. Execution uses bounded batches
so failures can be traced and reversed; it is not a rat-only pilot.

| Phase | Work | Reason and completion gate |
| --- | --- | --- |
| 1. Capture the starting state | Record tracked, untracked and relevant ignored files; sizes/hashes; Git changes; selections; supplied inputs; required generated dependencies. Record existing failures separately. | Preserve ongoing work. No affected untracked or unique generated file is unaccounted for. |
| 2. Build the ownership and move map | Assign every in-scope subtree to keep, move, retain-as-history, consolidate-later, or removal-candidate. Record old/new path, reason, consumers and validation needed. | Names alone cannot establish lineage. Unresolved items remain retained and visible. |
| 3. Establish retention before cleanup | Verify checkpoint/snapshot contents; preserve required generated files and adjacent assets; investigate R01 mismatch without blessing its new hash. | Selected and required historical assemblies have an intact, explicit input set. |
| 4. Add navigation and status | Update root/project/species/variant entry points; label historical, rejected and withdrawn work; introduce guidance. | Every project can be found, including enclosure/cameras, without guessing a filename. No candidate is silently promoted. |
| 5. Migrate the agreed layout | Apply the map across cameras/shared consumers, animal variants/anatomy, enclosure and supporting docs/releases. Keep protected paths in place. Update imports, manifests, macros, CLI scripts, links and generated destinations in each batch. | No dangling active reference, changed preserved binary, or accidental selection change; record rollback map and checks. |
| 6. Consolidate current implementations | Extract truly shared operations and remove avoidable current-source copies after comparing behavior. Preserve historical replay implementations when needed. | Affected geometry/interface or electronics/firmware regression checks pass. This is not an architectural rewrite of every builder. |
| 7. Remove verified clutter | Produce an exact removal list; remove only reconciled temporary files and verified redundant copies. Keep unique recovery work and uncertain dependencies. | Every removed file has a recorded reason and, where relevant, retained replacement and recovery location. |
| 8. Verify and hand off | Validate links, selectors, hashes, LFS attributes, replay and representative builds/exports. Test fresh-checkout/restoration behavior for supported workflows. Report residual exceptions. | Navigable root, intact matched assemblies, working supported entry points, honest validation scope and before/after inventory. |

A matching file hash proves preservation, not CAD equivalence after a rebuild.
Geometry builds need geometry/interface checks; electronics changes need the
relevant KiCad, board-contract and firmware checks. Use code-based FreeCAD
interaction and the session ownership/save-and-close policy in `development.md`.
Do not start or close the user's applications merely to organize files.

Run the bibliography checker and its tests when source-backed documentation is
changed. Update migration verifiers intentionally for moved files; do not weaken
preservation checks to make the new layout pass. Preserve the historical mapping
and add the cleanup mapping rather than silently replacing the old audit record.

## Decisions and limits

Recommended defaults are: keep the existing major roots; group camera projects;
keep species directly under eye-tracker; use variant-local checkpoints/history;
keep frozen historical paths where required; and prefer explicit file roles to
aggressive deletion. Variant names for OV9281 and ambiguous early rat studies
remain provisional until the detailed lineage map is reviewed.

The retention inventory, dependency graph, exact move/deletion list and supported
replay coverage are implementation deliverables, not completed work in this
proposal. No storage-saving estimate or complete rebuild claim is made. The
cleanup changes where work is found; it does not decide which engineering
candidate is accepted or erase unresolved design limitations.

## Evidence and review scope

Primary-source guidance is recorded in `references.bib`:

- [OSHWA sharing best practices](https://oshwa.org/resources/sharing-best-practices/): overview, editable originals, auxiliary files, BOM and assembly documentation. [@oshwaSharingPractices]
- [Stanford organizing data](https://laneguides.stanford.edu/DataManagement/Organizing): naming, directories and README conventions. [@stanfordDataOrganization]
- [GitHub releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases): tagged milestones, downloadable assets and LFS archive behavior. [@githubAboutReleases]
- [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage): pointer/object storage. [@githubAboutLfs]

Local review covered all seven design roots, project and species README files,
mouse/rat/shared subtrees, enclosure study introductions, OV9281 working-review
and E01 records, releases, tools/docs organization, ignore/LFS rules, current Git
status and the prior migration policy. Earlier rat hash/duplicate findings are
retained above. This was a filesystem/documentation review, not a native-geometry,
electrical, full duplicate-content or exhaustive dependency audit.
