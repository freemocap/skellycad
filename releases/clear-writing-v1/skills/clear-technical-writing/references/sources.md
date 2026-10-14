# Sources and portable installation

This companion skill is an adaptation of general technical-writing guidance, not an official Google skill. Its procedural precision check is a local workflow choice.

- [Google style guide](https://developers.google.com/style): project conventions and editorial flexibility. [@googleDeveloperStyleWriting]
- [Google highlights](https://developers.google.com/style/highlights): tone, language and formatting. [@googleStyleHighlightsWriting]
- [Google procedures](https://developers.google.com/style/procedures): action order, context and commands. [@googleProceduresWriting]
- [Pinned STE skill](https://github.com/danyuchn/asd-ste100-skill/tree/32511c6992ecb5f1971e46a2943f2e6adceedafe): the companion STE implementation and its limitations. [@danyuchnSteSkill2026]

Google's documentation is generally CC BY 4.0, subject to the notices on each source page. This synthesis is an adaptation. The STE skill retains its upstream MIT license; local changes adapt metadata and invocation scope. The official ASD dictionary is not bundled, and the linter does not establish compliance.

Install both skill folders together as siblings. The bundle README explains personal and project installation. Citation review records are in the bundle's references.bib. This portable copy has no machine-specific links or background updater.

When updating the STE dependency, review the upstream diff, preserve the license, and reapply the metadata and invocation-scope adaptations. Treat the linter as advisory; its current implementation has known heuristic limitations. Run its self-test after updating.
