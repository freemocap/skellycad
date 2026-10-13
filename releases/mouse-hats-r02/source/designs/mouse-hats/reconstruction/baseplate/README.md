# Uncut skull base plate — 58 candidate

Source: approved `old/58nassembly.step / Baseplate` (34 faces), not the skull-shaped
`Baseplatecut`. No originals, meshes or old arm geometry were modified.

## Review and controls

`BaseplateRebuild58` shows cyan rebuilt and gold source (+18 mm X). Saved file:
`generated/mouse-hats/reconstruction/baseplate/01-baseplate-candidate.FCStd`
relative to the playground.

Select Baseplate: `BoreRadius` is 1.45 mm; `SkullStockDepth` is 10 mm. Depth extends
the underside while leaving the seat fixed in assembly coordinates. The measured
2.9 mm bore is not a verified commercial insert specification. `DisplayStage`
shows Stock, Outer body, Receiving pocket or Finished; restore Finished for use.

This is a **scripted parametric feature**, not a native sketch/Pad history. Use
`open_model.py` in FreeCAD to load `baseplate_features.py` before opening/editing.
A plain FCStd open can display cached geometry but requires that module on its
Python path for recomputation. Measured construction data is embedded as JSON;
no imported solid is needed to rebuild. JSON on disk and manual edits are not
automatically synchronized.

## Construction

`baseplate_features.py` builds a stock prism, planar lug regions and rounded end;
then cuts the drafted socket, bore, mouth relief and tiny measured groove.
`plane_cell` intersects a stock box with measured half-spaces using
`normal dot point <= offset`. The two principal receiving planes retain the
45-degree cross-section and 5-degree insertion draft.

The discarded standard feature-chain experiment could initially pass but fail
after reopening at a cylindrical trimming junction. The retained scripted model
repeats the direct geometry operations deterministically and passed independent
rebuild/reopen, edits and stage tests. This is a persistence tradeoff, not a claim
of fully native editing or complete semantic simplification.

## Evidence and limitations

- Candidate: one solid, 33 faces, 603.6956708146521 mm³; deeper BOP check passes.
- Source: 603.6956710073913 mm³, but fails deeper checks. Exact Boolean parity
  is not established despite the ~0.000000193 mm³ volume difference.
- 240 samples each way: candidate-to-source maximum ~1.1e-11 mm;
  source-to-candidate maximum **0.200219 mm**. All sampled outliers above 0.0001 mm
  lie on source face 32: a small planar cap at the pocket mouth, Y=5, area
  0.215252 mm². This cap is absent from the valid candidate. Its association with
  the source's errors is a suspected explanation, not proof of intended geometry.
  Bounded sampling is not a global error bound.
- Critical receiving planes preserved; source-stem plane offsets are zero and
  ~0.000000081 mm. These are nominal contacting faces, not added print clearance.
- Rebuilt baseplate and tray/stem in the original assembly coordinates have zero
  interference volume at 0.001 mm Boolean tolerance. This does not validate
  physical fit, insertion-path clearance or retention force.
- Tested bore radius 1.45→1.55→1.45 mm and stock depth 10→10.5→10 mm; all four
  display stages pass geometry checks. See `validation-baseline.json`.

## Replay

Run with the playground's pinned FreeCAD Python:
`.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe`.

1. `inspect_source.py`: verify STEP hash and cache the selected source BREP.
2. `measure.py`: regenerate measured `parameters.json` and disposable study.
3. `build.py`: create the parametric FCStd using parameters alone.
4. `verify.py`: fresh rebuild/reopen, edits/stages, samples and mating-plane checks.
   Pair checking also expects the existing tray/stem checkpoint and source cache.

Source indices in measurement are specific to the hash-pinned 58 file. User has
visually accepted this candidate and requested continuing. The seated interface
has since been shown in the three-part assembly review and the cap reconstructed.
Keep the pocket-mouth discrepancy explicit; visual acceptance is not physical fit
validation or proof of exact source parity.
