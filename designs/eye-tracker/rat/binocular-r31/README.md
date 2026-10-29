# Rat R31: uncapped binocular review

R31 places two real camera modules on opposing faces of a shared carrier, with one sensor aimed at each eye. It preserves the R30 anatomy, baseplate, sensor-holder interfaces and separated protective-arm style. The cap and the second two-camera configuration are deferred.

The PCB section is raised 4 mm along mount Y, with a 4 mm gap between the modeled bare PCB backs. The lower stem interface remains unchanged. A central bridge joins the raised trays to that stem. Connector pockets and ribbon-exit relief remove carrier contact. The left board uses a proper 180-degree rotation; no physical camera geometry is reflected. Its sensor and holder also use a proper rigid rotation, so the two arm and ribbon routes differ.

## Source and selection

`baseline.json` records the hash-verified complete source assembly **ET-RAT-SEPARATED-ARMS-R30** and the selected **CAMERA-DUMMY-R08** assets. The camera modules are loaded through `shared.camera.add_camera`, then articulated using the source assembly's rigid component geometry and new ribbon routes. Optical datums stay with their respective modules.

The species selector still names historical **ET-RAT-MONO-R01**. Its file hash differs from the recorded manifest hash; R01 was inspected but was not used as a geometry input. This pre-existing discrepancy is recorded in `baseline.json`. No selected manifest or source checkpoint was changed. R31 is a separate review candidate, not a new selected checkpoint or print release.

## Verified scope

- Both optical axes pass within 0.001 mm of the retained R14 eye centers, with positive forward distances of 20.839 mm. These targets remain anatomical estimates.
- The finished carrier is one valid solid. The baseplate, both sockets, both holders and both clips preserve their source geometry and matched relative interfaces.
- Each support engages its tray and socket. All six arm-pair checks pass, including at least 0.3 mm between free spans. The smallest arm-to-ribbon gap is 0.944 mm.
- Both ribbons have 32.85 mm centerline length, 4 mm width and 0.25 mm modeled thickness. Their sampled minimum centerline radii are 6.930 mm and 9.338 mm.
- Full-solid checks detect no new component interference. Each side retains the source lens/holder overlap of about 2.042 cubic millimetres and holder/clip overlap of about 0.00794 cubic millimetres. These inherited contacts are not a demonstrated physical fit.
- All 19 checked hardware parts have zero detected skull-surface crossings and zero contained samples in either eye envelope, using 2,000 samples per part per eye. The unchanged baseplate remains intentional skull-cut stock and is excluded from these clearance claims.
- Validation meshes are closed without detected self-intersections at the recorded settings. Saved native files contain `Document.xml` and pass ZIP integrity checks.

The ribbons use the source design's relaxed geometric strip approximation: centerline length, endpoint frames and sampled curvature are constrained, but sheet inextensibility, twist strain and fatigue are not established. Physical ribbon routing, retention without a cap, connector/cable service access, stiffness, total mass, balance, full joint travel and anatomical fit require review or bench testing. Skull volume containment is not asserted because the source design skull is open. Do not infer print readiness from static geometry checks.

## Rebuild and review

Run these commands from the repository root after the pinned runtime is installed as described in `docs/development.md`:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/rat/binocular-r31/build.py
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/binocular-r31/check_eyes.py
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/rat/binocular-r31/render.py
```

Stop if any command fails. The native build verifies inputs, creates placement and carrier stages, fits both ribbons and arm pairs, and validates the complete assembly. `check_eyes.py` must report `EYE_CONTAINMENT_PASS`; native validation must report `NATIVE_VALIDATION_PASS`. Generated outputs remain under `generated/eye-tracker/rat/binocular-r31/`. The renderer uses an isolated hidden GUI and saves review views without changing another desktop session.

`review.json` identifies the frozen complete assembly and its SHA-256 hash. Open that checkpoint for inspection, and save subsequent edits under a new revision. Use `overview.png`, `top.png`, `front.png` and `rear.png` beside this document for the recorded review views. The task's isolated rendering sessions were closed after verified saves; no task-owned documents remain open.

This revision uses local design records and supplied geometry only; no new external technical sources informed the change.
