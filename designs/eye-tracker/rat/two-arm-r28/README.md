# Rat R28: paired supports around the current ribbon

The working high-water mark is the accepted **ET-RAT-ALIGNED-TIP-R27** complete assembly. Its print derivative adds the RAT R27 emboss and revised C01 clip. On 2026-10-28 the user reported that the single arm positions the camera well but is too bouncy. Two-arm support, following the mouse structure, is the next design direction. R28 now contains the complete two-arm review assembly. It reuses the R21 paired supports with R27’s ribbon exit relief, while preserving R27’s camera pose, ribbon, anatomy, baseplate and optical axes. The C01 clip is recovered from the hash-verified R27 print archive. This is a review candidate, not a new print release.

## Verified inputs

`review-inputs.json` records the paths and verified SHA-256 hashes of:

- Rat R27: complete assembly and preserved camera/ribbon/anatomy arrangement.
- Mouse R19: selected complete assembly with paired supports.
- Rat R21: earlier paired oval supports in the rat geometry, before the single-arm revisions.

The rat top-level `active-model.json` still selects historical R01, whose file also differs from its recorded hash. It is not a geometry input for this work. R27 is identified explicitly through its own review manifest. The articulated-arm study is conceptual and is not a later accepted complete assembly.

The [R27 print pack](../print-r27/README.md) carries the C01 clip and embossed hardware; these matched print details must be carried into the next export. R27's frozen assembly contains the preceding clip, so do not silently substitute that clip for C01.

## Interface comparison

The CLI comparison (`compare.py`) found zero bidirectional Boolean difference and zero bounding-box center shift between R21 and R27 for the holder, retained socket, baseplate, sensor PCB and lens. The earlier two-arm attachment frame is therefore directly relevant. This does not assert ribbon equivalence: R27's ribbon route remains the fixed input for new supports.

## Built candidate and checks

Both supports have positive engagement with the tray and socket. Ribbon gaps are 0.952 mm for the upper support and 1.291 mm for the lower support. The carrier is a single valid solid, with a closed export and no detected self-intersections. Carrier/ribbon and carrier/holder overlaps are zero; the holder gap remains 0.333 mm. No carrier/skull surface crossings were detected, and 3,000 carrier surface samples lie outside each eye envelope.

Inherited connector contact (0.0590 mm³), cap contact (0.00222 mm³), and C01 clip/holder contact (0.00794 mm³) remain recorded separately. Full joint travel and physical stiffness remain untested. The arms retain the earlier rectangular-section geometry; this candidate does not claim new junction fillets.

Run `build.py` with the pinned FreeCAD Python, followed by `check_eyes.py` with the tooling Python. Submit `show.FCMacro` to the verified existing native FreeCAD listener to display **Rat R28 - two arms, current camera and ribbon**. The macro saves the first reviewed checkpoint and its hash in `review.json`. It never overwrites an existing frozen checkpoint.

The baseline-comparison macro `open.FCMacro` remains available for Rat R27, Mouse R19 and Rat R21. Reports are in `generated/eye-tracker/rat/two-arm-r28/`.

## Design direction

1. Hold the R27 camera head, ball/socket center, lens axis, ribbon route, main PCB and anatomical mounting pose fixed. Camera position already works according to the user.
2. Use two separated tray roots and two separated socket-collar attachments, following Mouse R19's paired-support structure. Start with the rat R21 interface locations, transformed into the R27 frame, and verify that the endpoints still match before reusing them.
3. Fit two compact, smooth arms around the current R27 ribbon. Preserve the ribbon's natural route; do not restore the earlier wrapping route simply to accommodate the arms. Use separation between the supports to resist rocking, rather than placing two strips immediately beside each other.
4. Blend both roots into the tray and both tips into the fixed socket collar with substantial engagement and fillets. Leave the movable holder and ball free. Avoid a thin terminal neck or abrupt section change. Choose section sizes after checking available space, not by blindly scaling the mouse.
5. Compare the R28 candidate with R27 in the same camera pose. Validate each arm's seating, fused carrier validity, ribbon clearance, holder travel, sensor/lens clearance, matched cap and clip, and skull/eye clearance separately. Freeze only after native review and closed-mesh checks pass.
6. Print a matched trial. Compare movement under the same small hand-applied load at the camera: first with the tray held fixed, then check whether motion comes from the arm, ball/socket or base mounting. Record observed improvement rather than claiming stiffness from a valid mesh.

The paired support is a mechanical design hypothesis; the source of the reported bounce has not yet been isolated. R27's 1.6 mm terminal thickness and long single curved span are relevant dimensions to inspect, not proof of the failure mechanism. The second arm should stabilize the fixed socket without sacrificing camera articulation.

## Review

Read `docs/development.md`, then submit `open.FCMacro` to the verified desktop FreeCAD listener. If FreeCAD is not running, open this macro in the pinned desktop application. It opens three distinct working copies and leaves Rat R27 active. The frozen inputs remain unchanged. The macro reuses existing tabs by physical file path.

No new research or anatomical changes are introduced here. Existing anatomy and optical datums retain their documented uncertainties.
