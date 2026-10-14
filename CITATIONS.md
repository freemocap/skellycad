# References and evidence

Keep the repository bibliography in [references.bib](references.bib). Register
sources when they inform research, geometry, algorithms, implementation or design
decisions. Put a stable citation key beside the supported statement, for example
`[@hughes1979RatEye]`. Retain useful background references with an honest review
record even when they are not inputs to the current design.

This follows the common FreeMoCap and SkellySpeak approach, using FreeMoCap's
more explicit review vocabulary [@freemocapCitations2026; @skellyspeakCitations2026].

## Entry format

Use UTF-8 BibTeX, stable ASCII keys and braced field values. Protect proper names
and corporate authors with braces. When exporting through Zotero/Better BibTeX,
preserve existing keys and custom provenance fields. The checker supports nested
braces and escapes; normalize quoted values, macros and concatenation before use.

Every entry requires `title`, `author` or `editor`, `url`, `urldate` in YYYY-MM-DD
form, `review`, and `claim`. Include verified year, venue, pages, DOI and version
where available. Use a bare DOI in `doi`, a stable HTTP(S) address in `url`, and
`@misc` for repositories/websites. An access date is not a publication year.

- `review`: `metadata`, `abstract`, `excerpt`, `full-text`, or `source-code`.
  This identifies what was inspected, not scientific endorsement.
- `claim`: the specific proposition supported or reason for retaining the source.
- `note`: review scope, secondary access, cohort, limitations or local adaptations.
  Required for `metadata`, `abstract`, and `excerpt` reviews.

Merge duplicate sources. Record uncertainty rather than filling missing metadata
from memory. Distinguish reported measurements, derived quantities, chosen CAD
constraints and geometry validation. For anatomical dimensions, state units,
measurement endpoints and population. A mesh hash establishes file identity,
not anatomical correctness.

## Citations and validation

Use `[@hughes1979RatEye]` in Markdown or code comments; group citations with a
semicolon. Structured JSON/YAML `sources: [key]` fields may accompany these, but
the checker only resolves bracketed citation markers, including markers embedded
in JSON strings. Keep structured provenance linked to a cited design note.
These markers do not install a bibliography renderer.

From the repository root, using Python 3.11+ (the CAD tools environment works):

```powershell
python -B tools/check_references.py
python -B -m unittest discover -s tools -p test_references.py -v
```

Run both checks when adding research or changing bibliography infrastructure.
The checker rejects malformed entries, duplicate keys/fields/URLs/DOIs, missing
metadata, invalid dates/reviews and unresolved bracketed citations in source and
documentation. It preserves unused entries. It skips generated/dependency folders,
the untouched `old-cad-playground`, `.cad-tools`, and vendored `.agents`/`.codex`
resources. Historical design documents remain included; uncatalogued older
literature is migrated when reviewed. Checks cannot verify scientific support
or live URL availability; inspect the evidence during review.

The checker and regression tests were adapted from FreeMoCap's pinned revision
in the bibliography, under AGPL-3.0; local scan exclusions and the XPath predicate
exception are documented in code and covered by regression tests.
