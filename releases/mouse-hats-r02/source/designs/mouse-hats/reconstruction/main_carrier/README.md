# PCB tray and mounting stem — 58 reconstruction candidate

The user explicitly deprioritized the old arm and its junction during this pass:
it will be replaced when the later two-arm mesh work is authorized. This checkpoint
rebuilds the PCB tray, retaining lips, locating ramp, lower PCB stop and mating stem.
The skull base plate is a separate part and is next. No mesh comparison was done.

Review clarification: the user considers the stem slopes important to the mating
fit. Preserve their measured geometry and validate against the base plate before
changing them. The circled notch at the old arm end of the tray is believed by
the user to be an incidental arm-attachment artifact. Exact reproduction of that
notch is not required; cleanup is deferred. The current checkpoint is unchanged.

## Open and inspect

Saved model: `generated/mouse-hats/reconstruction/main-carrier/01-tray-mount-candidate.FCStd`
relative to the playground. GUI document: `TrayMountRebuild58`.

- Cyan: rebuilt tray + stem, old arm omitted.
- Gold: source region below assembly Z=17.76629685 mm, shifted +26 mm in Y.
  It still contains some old arm-root geometry near the upper edge.
- `OriginalCarrierReference` is the full original carrier, hidden by default.
- `Dimensions.VentRadius` and `Dimensions.VentSpacing` are live controls.

Run `open_model.py` through the pinned FreeCAD session to load the saved file with
the custom union implementation available. A plain FCStd open can display cached
geometry but cannot reliably recompute the custom union if its Python module is
not on the import path. Do not describe this as a wholly native feature graph.

## Construction and reproducibility

`build.py` builds independently of imported solids, using measured `profiles.json`
and editable `parameters.json`, both in millimetres. Profiles become constrained
native sketches and ruled solid lofts. The rear stem is bounded by measured planes
using native boxes and cuts. These preserve its draft and relief geometry.

`carrier_features.py` supplies one small Python union feature. Its explicit
0.001 mm join tolerance resolves near-coincident source details; an ordinary
zero-tolerance union failed the deeper geometry check. Two native cylinders and a
native cut make the vents. The other profile coordinates are reconstruction data,
not yet a compact set of semantic design dimensions. A fully constrained measured
sketch is not the same as a fully redesigned, conveniently parameterized part.

Run from the playground with the bundled FreeCAD Python:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/mouse-hats/reconstruction/main_carrier/build.py
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/mouse-hats/reconstruction/main_carrier/verify.py
```

`measure.py` regenerates profiles from the hash-pinned 58 STEP. Its face indices
apply only to that source. It also writes the disposable source BREP used by the
verification script. Run it first if the generated source cache is missing.
Build and verification do not overwrite or alter the supplied STEP/F3D files.

## Evidence and limits

Independent reopen/recompute/edit/restore passed. The result is one solid,
volume 766.79885442 mm³, with 94 faces, and passes the deeper BOP check.
Tested vent radius 2.0→2.1→2.0 mm and spacing 25→26→25 mm.

Within assembly Z≤10 mm (away from the old arm), both missing and excess Boolean
volumes are zero **at 0.001 mm tolerance**. The independently computed regional
volumes differ by ~0.0028293 mm³, so this is tolerance-based agreement, not exact
identity. Across the whole candidate, the excess-volume check also returns zero
at that tolerance. The complete original carrier has more material because the
arm is intentionally absent. Upper tray/root separation is not exact parity.

No claim of fewer faces, full carrier parity, physical fit or print validation.
The useful improvement is named, replayable construction with explicit controls;
the measured profile detail still needs later simplification where fit permits.
See `validation-baseline.json` for the recorded numbers.

The rejected whole-carrier section approach is archived under `experiments/`:
it produced 915 faces and was deliberately not promoted to the working model.
