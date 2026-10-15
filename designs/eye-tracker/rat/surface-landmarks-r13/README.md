# Rat R13: outer cheek and arch references

R13 retains the visually accepted R12 rigid skull placement. The cheek audit uses lateral rays from outside the skull at each original atlas marker's anterior-posterior and dorsal-ventral coordinates. The first surface intersections are 0.399 mm outward on the left and 0.616 mm outward on the right. This is different from the previous nearest-triangle distance, which did not identify the outer face specifically. The discrepancy is local geometry disagreement, not proof that the whole registration should shift.

Blue working-skull cheek points now mark those outer intersections. Original atlas markers and their coordinates are preserved but hidden. Bregma, lambda and nasion remain unchanged. Purple points add a left/right arch reference pair near AP +8 mm relative to bregma. They are lateral extrema in a declared narrow AP/DV crop, not author-labeled sutures or independently validated anatomical landmarks.

Each visible marker has a `SurfacePosition` and an `Evidence` property. Its sphere is displayed 0.65 mm outward for visibility, with a leader ending at the actual surface point and a small surface dot. The display offset is not included in the anatomical coordinate. This prevents marker burial from being mistaken for a misplaced landmark.

`cheek-audit.json` records the checks and offsets. `landmarks.json` records local coordinates and definitions. `prepare.py` verifies the R12 checkpoint hash; `open.FCMacro` creates a new review document. The working mesh and its registration are unchanged. The complete camera assembly is unchanged.
