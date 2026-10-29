# Rat R32: compact binocular carrier and rearward protection

R32 lowers the complete hardware assembly 2 mm relative to the unchanged skull, shortens the central mount, and replaces the two thick tray backs with one windowed spine. Both support pairs sweep behind their ribbons. The upper and lower arms connect to the corresponding sides of each socket, with a separate ordering check to reject crossed routes.

This is a complete review assembly derived from hash-verified **ET-RAT-BINOCULAR-R31**. R31 remains preserved. The historical species selector still names R01; its known hash discrepancy is recorded in `lowering.json`, and it is not a geometry input. R30 supplies the recorded original matched hardware geometry. No source checkpoint or species selection was changed.

## Changes from R31

| Property | R32 change |
| --- | --- |
| Hardware relative to skull | 2 mm down along skull Z; skull and eyes unchanged |
| PCB section relative to baseplate | 5 mm down along mount Y |
| PCB back separation | 4 mm reduced to 1.2 mm around one shared spine |
| Central-mount solid volume | 1,482.20 to 616.08 cubic millimetres: 58.4% reduction |
| Finished carrier solid volume, including arms and sockets | 2,472.14 to 1,648.27 cubic millimetres: 33.3% reduction |
| Highest carrier point | 27.90 to 20.93 mm in skull Z: approximately 7 mm lower |
| Camera aiming | Both rays meet the retained eye-center targets, with 19.768 mm forward distance |

Solid-volume reduction is not a measured printed mass or strength result. The 1.2 mm windowed spine and retained catches need physical testing.

The left supports include a short departure past the PCB edge before curving rearward. This clears the oppositely facing board without sending the arm across its front. Both free arm routes are checked for rearward placement relative to sampled ribbon centerlines over the middle of their spans. Each pair also retains upper/lower order over the full sampled route. These geometric checks supplement the top-view inspection; they do not establish impact protection under load.

## Validation and remaining work

Native full-solid checks pass with one connected carrier and positive root/socket engagement for all four arms. The smallest arm-to-ribbon gap is 0.685 mm. All six arm-pair checks pass. Both holders, clips and sockets preserve their matched local geometry; the baseplate shape is unchanged apart from the requested translation.

All 19 checked hardware parts have zero detected skull-surface crossings and zero contained samples in either eye envelope, using 2,000 surface samples per part per eye. The baseplate is intentional Boolean-cut stock: lowering it increases its skull overlap. Only the baseplate is exempt from anatomy-clearance checks. The skull Boolean cut has not been performed.

Closed validation meshes have no detected self-intersections at the recorded settings. Native saved files contain `Document.xml` and pass ZIP integrity checks. Full-solid checks detect no new component interference; inherited lens/holder and holder/clip contacts remain recorded in `validation.json`.

Both ribbons retain 32.85 mm centerline length, 4 mm width and 0.25 mm modeled thickness. The routes are relaxed geometric strip approximations, with constrained endpoints and sampled curvature. They are not inextensible-sheet or physical strain simulations. Physical ribbon fit, strength, full joint travel, connector service access and retention without a cap remain unverified. The source skull mesh is open, so volumetric skull containment is not asserted.

Detailed root/socket fillets and chamfers, the skull Boolean cut and the cap are deferred. This is not a print release.

## Rebuild and review

From the repository root, use the pinned runtimes described in `docs/development.md`:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/rat/compact-binocular-r32/build.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/compact-binocular-r32/check_eyes.py
```

Stop if either command fails. Native validation must report `NATIVE_VALIDATION_PASS`, and containment validation must report `EYE_CONTAINMENT_PASS`. Outputs are under `generated/eye-tracker/rat/compact-binocular-r32/`.

The saved complete assembly and its hash are identified in `review.json`. Send `open.FCMacro` to the verified existing FreeCAD process using `tools/cad/open_in_running.py` and `--expected-pid`, following `docs/development.md`. The macro reuses an existing R32 document or opens a saved review under `generated/`, and leaves unrelated documents intact. Do not overwrite the frozen checkpoint with later edits.

Review [R32 overview](overview.png), [R32 top view](top.png), [R32 front view](front.png), and [R32 rear view](rear.png). Compare them with [R31 overview](../binocular-r31/overview.png) and [R31 top view](../binocular-r31/top.png). `comparison.json` records the measured differences.

This revision uses existing local design records and geometry, with no new external technical sources. Geometry validation remains distinct from demonstrated physical fit.

