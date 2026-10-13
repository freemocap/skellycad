# Sources and installation

Reviewed on 2026-10-13. This companion skill is an original, concise synthesis; it does not reproduce a complete style guide.

## Authoritative editorial references

- [Google developer documentation style guide](https://developers.google.com/style): project-specific guidance takes priority over the general guide.
- [Highlights](https://developers.google.com/style/highlights): default language and formatting conventions.
- [Procedures](https://developers.google.com/style/procedures): step order, context, and commands.
- [Active voice](https://developers.google.com/style/voice) and [present tense](https://developers.google.com/style/tense): consult for specific grammar questions.
- [ASD-STE100](https://www.asd-ste100.org/): authoritative source for the required edition and dictionary. The installed community skill targets Issue 9, dated 2025-01-15.

Google's documentation is generally available under CC BY 4.0 as specified on its pages. The links above credit the source; this companion is an adaptation, not an official Google skill.

## Existing tools evaluated

Maintenance dates below are latest default-branch commit dates checked through the GitHub API, not evidence of correctness or a future maintenance guarantee.

| Candidate | Evidence and fit | Decision |
| --- | --- | --- |
| [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) | Created July 2026; latest commit October 4, 2026. MIT. Includes rules, examples, and a Python linter; explicitly acknowledges missing dictionary verification. | Installed at commit `32511c6992ecb5f1971e46a2943f2e6adceedafe` (version 0.4.0). Useful for explicit STE requests; its stronger prose restrictions are not the everyday default. |
| [blagoySimandov/asd-ste100-writer-skill](https://github.com/blagoySimandov/asd-ste100-writer-skill) | Created July 2026; latest commit August 1, 2026. Includes writing references and evals. GitHub did not identify a license. | Alternative, not installed. |
| [loic-bellinger/google-developer-style-markdown](https://github.com/loic-bellinger/google-developer-style-markdown) | Created August 2026; latest commit October 12, 2026. Advertises weekly refreshes, Markdown pages, and llms.txt. Unofficial mirror. | Useful AI-readable reference; use Google's pages as authority. |
| [vale-cli/Google](https://github.com/vale-cli/Google) | Created February 2019; latest commit September 28, 2026. MIT rule implementation, fixtures, and coverage checks. Not maintained or endorsed by Google. | Best-established linting candidate of those checked; not installed in this instruction-only setup. |
| [stuffbucket/vale](https://github.com/stuffbucket/vale) | Created July 2026; latest commit July 30, 2026. Offers an STE linter and stdio MCP server; README disclaims certification and full dictionary coverage. | Not installed: limited maintenance history. This is a different project from the established Vale linter behind vale-cli/Google. |

The plugin directory search for technical writing did not surface a relevant standards-specific plugin. That is not an exhaustive statement about all MCP servers.

## Local and personal discovery

Both skill folders live in this repository's `.agents/skills`. Personal directory junctions under `C:/Users/jonma/.agents/skills` point to these same folders. This keeps one editable copy and makes the sibling STE link work in either scope. Moving or deleting this checkout requires updating the personal junctions.

[Codex skill discovery](https://learn.chatgpt.com/docs/build-skills) supports repository and personal skill directories and linked skill folders. Matching names can appear twice in a selector when both scopes are discovered; they refer to the same content here. Newly installed skills should be available on the next turn. Restart Codex if they do not appear.

Invoke `$clear-technical-writing` for general documentation or `$asd-ste100` for STE. Automatic selection remains enabled for both skills, with distinct scopes. The main skill handles ordinary writing and a focused precision check for consequential instructions. The STE skill applies when the user or project requests that profile. SkellyCAD's AGENTS.md supplies project-specific terminology and preservation rules.

## Updating the STE dependency

The upstream files and MIT license are retained. Local adaptations move the upstream `version` field into `metadata.version`, narrow the description and usage section to requested STE work, and clarify that its two modes apply after the STE profile is selected. The general writing skill owns the lightweight precision check. No executable logic was changed.

Check upstream changes and its open issues before updating. In particular, [issue 17](https://github.com/danyuchn/asd-ste100-skill/issues/17) reports sentence segmentation, position, and argument-parsing limitations. Treat linter output as suggestions to inspect, not proof of correctness. Do not make it a CI gate without evaluating those limitations.

Install a new commit into a temporary directory, compare it with this pinned copy, reapply the metadata and selection-scope adaptations described above, and run the skill validator and linter self-test before replacing the files. Retain the license and update the recorded commit. The personal junction follows repository updates automatically; no scheduled or unattended updater is configured.
