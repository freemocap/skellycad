# Mouse skull and eye registration study R01

This first study places matched Digimouse eye-label regions into our existing
mouse skull frame and compares a conditional adult-eye envelope with the current
assembly. It opens as a separate FreeCAD document. The R13 camera assembly and
selected checkpoint are unchanged. **The new eye centers and gaze directions
are study hypotheses, not approved anatomical placements.**

## See the stages

1. [Labeled CAD overview](assembly.png): six named landmark candidates with
   leader lines, adult eye envelopes and orange candidate axes.
2. [All 45 landmark IDs](landmarks-all.png) and [coordinate/name index](landmark-index.csv).
   Source IDs are preserved. Anatomical names for six IDs remain tentative;
   the other IDs are numbered, not falsely assigned names. Individual bones
   have not been segmented or named. In FreeCAD, group 05 toggles all 45 labels.
3. [Skull registration comparison](registration-comparison.png): our gray skull
   and cyan Digimouse head, with transferred orange eye-label regions.
4. [Eye direction comparison](eye-comparison.png): purple previous axes and
   orange conditional candidate axes.
5. [Source tissue check](eye-label-slices.png): cyan atlas contours over six
   registered cryosections. This check exposed a limitation in the eye label.

## Evidence and assumptions

Digimouse is one 28 g male nude specimen. Its 0.1 mm registered atlas provides
skeleton label 2 and eye label 3 [@dogdas2007Digimouse; @uscDigimouseDownloads].
The small label-3 components measure 1.5–2.0 mm across. Their contours closely
follow white internal regions in the tissue sections, consistent with lenses.
The provider calls these regions eyes; we have not established their full
anatomical boundary. Their centroids are therefore **not verified globe centers**.
The adult envelopes in this study are anchored there only to expose the
consequences of that assumption. No outer-globe segmentation is claimed.

The earlier Maga atlas study supplies 45 transferred point estimates
[@maga2017MouseSkullAtlas; @magaMouseCTAtlasRepository]. Bregma (ID 13), lambda
(ID 16), and four other names still require source-definition verification.
The named points and inferred skull frame carry question marks in the display.
The roll reference also uses the existing assembly's approximate lateral axis;
it is not a newly measured midsagittal plane. Meshes do not reveal sutures that
were lost from our supplied low-poly model.

For the gaze comparison, Oommen and Stahl report an inferred ambulatory direction
of 64 degrees lateral and 22 degrees above the horizon with lambda–bregma pitched
29 degrees nose-down [@oommenStahl2008MouseOrientation]. This is a behavioral
condition, not a universal standard pose. We interpret those directions as
spherical azimuth/elevation, rotate the vectors back into a level skull frame,
and then apply our tentative bregma–lambda basis. We do not add pitch and eye
elevation as scalar angles. The conditional vectors and all transforms are in
`comparison.json`. Absolute ocular torsion is not modeled.

## Results and what they mean

- Skull registration uses a proper similarity transform (scale 1.04643), an
  explicit head crop excluding forelimbs, and 80% trimmed nearest-point ICP.
  The original skull is never scaled or changed.
- Independent surface samples give median disagreement 0.202 mm and 95th
  percentile 0.864 mm. These measure surface mismatch, not landmark error.
- Repeating local fits at 70%, 80% and 90% retained fractions with different
  surface samples shifts transferred eye anchors by at most 0.13 mm. This
  tests local numerical sensitivity; it is not a confidence interval for anatomy.
- The transferred label anchors differ from previous eye origins by 0.70 and
  0.57 mm. Conditional gaze axes differ by 23.1 and 20.0 degrees.
- Both candidate eye envelopes are closed and have no detected skull surface
  crossings. This does not validate their positions, tissue boundaries, gaze,
  containment, camera clearance or physical fit.
- All 45 landmark point/label pairs reopen in FreeCAD. The basis is orthonormal,
  registration has no reflection, and visible axes match the saved recipe.

`registration.json`, `sensitivity.json`, `comparison.json` and
`geometry-validation.json` keep those checks separate. `review.json` pins the
native checkpoint and comparison assembly hashes.

## Rebuild and review

Read `docs/development.md`. Use the repository root as the working directory.
With `tools/cad/.venv/Scripts/python.exe`, run `extract.py`, `prepare.py`,
`register.py`, `compare.py`, `check_slices.py`, then `sensitivity.py` from this
study directory. These commands use the reader already installed under the
preceding skull study's generated `python-deps`; restore that study dependency
as described in its README if absent. Archive hashes are checked at extraction.

Send `build.FCMacro` through the existing FreeCAD pipe to create a separate native
study under `generated/eye-tracker/mouse/registered-eyes-study-r01`. Run
`validate.py` using the pinned FreeCAD bundled Python after saving. For the
frozen review, send `open.FCMacro` instead. Display groups independently toggle
original matched atlas anatomy, previous eyes, candidate eyes, named candidates,
all numbered landmarks and the conditional skull frame.

Digimouse source archives and derived Digimouse geometry retain CC BY-SA 4.0
attribution to Dogdas and colleagues / USC Biomedical Imaging Group. The
included license is preserved under `sources/`. Extracted images live under
`generated/`, avoiding duplicate raw volumes in the repository. Maga-derived
landmark provenance and its supplied license remain in the previous study.

## Next anatomical milestone

Trace and review outer-globe boundaries across the downloaded cryosections,
then fit a globe center separately from the internal lens center. Verify the
bregma/lambda ID dictionary and bilateral orbital landmarks; use independent
held-out landmarks to assess the skull fit. Re-run the gaze comparison with
that verified skull frame. Only then propose eye pose changes to the complete
camera assembly and refit hardware if needed. This study intentionally makes
those unresolved steps visible instead of silently accepting the candidate.
