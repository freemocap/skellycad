---
name: clear-technical-writing
description: Write or edit technical documentation, engineering explanations, and agent instructions using Google developer documentation style. Use for clear-language rewrites; check consequential procedures for ambiguity and route requested STE writing to the companion skill. Excludes creative and marketing writing.
---

# Clear technical writing

Use Google developer documentation style for general documentation. Follow the user's requested style and project terminology first. These are editorial guidelines, not a certification of conformance.

## Choose the profile

- For READMEs, explanations, setup guides, and ordinary technical prose, use the guidance below.
- For procedures where a misreading could cause an incorrect build, export, assembly, data change, or agent action, also apply the precision check below.
- For an explicit STE or controlled-language request, read the companion [ASD-STE100 skill](../asd-ste100/SKILL.md). Apply its rules to the requested text. Preserve technical meaning even when that requires an exception to a style rule. Its linter is a heuristic, not a compliance check.
- For a request for formal ASD-STE100 compliance, identify the required edition and obtain access to its authoritative rules and dictionary. Report any unchecked vocabulary or rules. An STE-inspired rewrite alone cannot establish compliance.

## Edit for the reader

Determine what the reader needs to understand or do. Lead with that information. Use familiar wording while retaining necessary domain terms. Use one name consistently for each concept, and explain unfamiliar abbreviations when first used.

Address the reader as "you" in instructions. Prefer active voice when the actor matters. Use present tense for current behavior, while preserving past events, future behavior, and uncertainty accurately. Keep a natural, direct tone.

For procedures, put prerequisites before the steps and conditions before the actions they govern. Use numbered steps in execution order. Start each step with the action; put commands and their necessary explanations beside it. Separate independently meaningful actions. Keep required information in the steps instead of hiding it in notes. Preserve existing warnings before the actions they govern.

Use sentence case for headings, descriptive link text, code formatting for identifiers and commands, and bold for UI labels. Match established project spelling and formatting. Use lists for sequences or parallel items and prose for explanations.

Keep enough context for the reader to follow the reasoning. Shorten indirect expressions and unsupported promotional claims. Sentence length is a readability signal, not a hard cap in this profile. STE-specific vocabulary restrictions and grammar limits apply only when the STE profile is selected.

## Precision check for consequential instructions

After drafting, inspect each action for these properties:

- The actor and affected object are identifiable. Replace ambiguous pronouns and vague references such as "the latest" with the identifier or selection rule established by the source.
- Prerequisites, conditions, and exceptions appear before the actions they govern. The action order is explicit.
- Independently meaningful actions are distinguishable, and the same concept keeps the same name throughout.
- The reader can tell when the step succeeds and when to stop, where the source establishes those conditions. Flag missing criteria instead of inventing them.

Revise only the passages that need clarification. This is an STE-inspired ambiguity check within the general profile; it does not activate the companion skill's full grammar, vocabulary, or sentence-length restrictions. Use the companion skill when the task actually calls for STE.

## Check meaning before delivery

Compare the revision with the source. Preserve actors, conditions, exceptions, action order, quantities, units, negation, and requirement strength. In particular, "may", "must", "should", "only", and "at least" carry meaning. Preserve code, commands, paths, API names, quotations, and externally defined identifiers unless the requested change includes them.

Resolve ambiguous wording only when the available context establishes the intended meaning. Otherwise flag the ambiguity. Keep technical corrections distinguishable from editorial changes.

Keep discussion and brainstorming natural, including useful examples and uncertainty. Apply the procedural check to actionable instructions within a discussion, rather than converting the whole discussion into a procedure.

Return the requested artifact or rewrite. For an editing report, identify substantive changes and unresolved ambiguity. Cite a standard's rule number only after checking it against that edition.

For a style question beyond this short guide, consult the relevant official page linked in [sources and installation](references/sources.md). Fetch only the topic needed. This skill can handle ordinary edits without network access.
