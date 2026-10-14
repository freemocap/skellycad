# Clear writing skills — v1

A portable writing workflow for technical documentation and agent instructions.
Prepared 2026-10-14. No SkellyCAD checkout, account connection, or MCP server is required.

## How it works

- **Default:** `clear-technical-writing` uses a Google-style editorial profile for readable explanations and documentation. [@googleDeveloperStyleWriting; @googleStyleHighlightsWriting]
- **Precision check:** the main skill checks consequential procedures for explicit objects, conditions, action order and completion criteria. This is a local STE-inspired workflow choice, with procedural organization informed by Google's guide. [@googleProceduresWriting]
- **Requested STE:** `asd-ste100` applies the more restrictive profile when the user or project requests it. The bundled community skill is adapted from a pinned upstream release. [@danyuchnSteSkill2026]

Preserve technical meaning, quantities, identifiers, exceptions and uncertainty. Keep discussion and brainstorming natural. The shortest possible text is not always the clearest.

## Install in Codex

Extract this ZIP first. Copy **both folders inside `skills/`**, keeping their names and sibling relationship. Choose one scope: [@openaiBuildSkillsWriting2026]

| Scope | Destination |
| --- | --- |
| One project | `<project>/.agents/skills/` |
| Your projects on this machine | `~/.agents/skills/` |

On Windows, `~` means your user folder, usually `C:\Users\<username>`.
Create the destination if needed. If either skill already exists, compare or back it up before replacing it. The final paths must end in `clear-technical-writing/SKILL.md` and `asd-ste100/SKILL.md`; do not copy an extra `skills` nesting level.

Start a new turn after copying. If the skills do not appear, restart Codex.
The files are independent copies; moving the extracted bundle afterward will not break the installation.

## Use

Try these prompts:

- `Use $clear-technical-writing to revise this README. Preserve technical meaning and useful examples.`
- `Use $clear-technical-writing to check this export procedure for ambiguous objects, conditions, and action order.`
- `Use $asd-ste100 to rewrite these instructions. Preserve quantities, exceptions, and uncertainty.`

Automatic selection remains enabled with distinct scopes. For a consistent project default, append this snippet to the project's existing `AGENTS.md`:

```markdown
For technical documentation and agent instructions, use the
clear-technical-writing skill. Use its general profile by default and its
precision check for consequential procedures. Use the full ASD-STE100 profile
when the user or project requests it. Preserve technical meaning, identifiers,
units, exceptions, and uncertainty. Keep discussion and rationale natural.
```

Add your project's terminology separately. Do not replace an existing AGENTS.md with this snippet.

## Optional linter

Writing with the skills needs no Python installation. The optional STE linter needs Python 3:

```text
python skills/asd-ste100/scripts/ste-lint.py --selftest
python skills/asd-ste100/scripts/ste-lint.py your-document.md
```

Run these examples from the extracted bundle folder. Findings are heuristics, not compliance certification. The official controlled dictionary is not bundled. The skill's references describe the limits. [@danyuchnSteSkill2026]

## Contents and provenance

- `skills/`: editable skill instructions, references, and the upstream linter.
- `references.bib`: source metadata and review scope. Citation keys in this bundle resolve here.
- `LICENSE`: the SkellyCAD repository's AGPL-3.0 license for its original contributions.
- `skills/asd-ste100/LICENSE`: retained upstream MIT license.
- `SHA256SUMS.json`: checksums of all other bundle files.

The companion guidance credits Google's documentation, published under CC BY 4.0 as noted on its pages. This bundle is not endorsed by Google or ASD. Retain these notices when sharing.

The STE base is version 0.4.0, commit `32511c6992ecb5f1971e46a2943f2e6adceedafe`. Local edits adapt metadata and narrow invocation to requested STE work. The linter is unchanged. The companion skill and project snippet implement the agreed default-writing workflow.

This is a manual-install ZIP, not a published marketplace plugin. It includes the editable sources and requires no automatic downloads or updates.
