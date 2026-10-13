# From reconstruction to controllable design

Accepted reconstruction checkpoint: `8709351` (rebuilt in freecad).
The user visually accepted the six-part assembly. This is our geometry reference
for the next phase, subject to the existing per-part discrepancies and fit limits.
The commit stores reconstruction code and measurements. Ignored generated FCStd
files and local Fusion archives are not preserved by that commit alone.

## Sequence

1. Inventory existing controls and preserve baseline evidence. The assembly's
   `audit_checkpoint.py` reads saved files without modifying them, recording their
   hashes, final geometry statistics, and current user-facing length controls.
   `control-inventory-baseline.json` records this checkpoint's saved models.
2. Refactor the stem/baseplate interface as one shared geometric specification.
   Give its frame, mating planes, insertion direction, seat and stops names.
   Preserve measured nominal geometry first. Then introduce an explicit clearance
   parameter with a documented direction and ownership: grow the receiving pocket
   while leaving the mating stem fixed. Confirm the affected surfaces before
   implementing this rule; do not apply a blanket offset to every pocket surface.
3. Give the PCB tray and cap shared board-envelope and retention dimensions.
   Separate board clearance, cover thickness and retaining-lip engagement. Actual
   PCB dimensions are not yet verified: request measurements when needed rather
   than interpreting inherited geometry as the hardware specification.
4. Give the camera head explicit ball/seat and clip/holder interface descriptions.
   Preserve the inherited nonconcentric ball placement until an intentional change
   is requested. Record which controls reposition a mating component and which do not.
5. Once default reproduction and controlled variations pass, bring in the user's
   mesh fixes as design requirements, one change at a time. Mesh comparisons and
   two-arm reconstruction remain deferred until that phase is explicitly started.

## Model organization

Keep existing reconstruction builders and their measured inputs as the baseline.
New maintained design code should live in a sibling `designs/mouse-hats/model/`
folder, with shared interfaces, part builders and a build entry point. Establish
that folder when the first interface refactor is implemented, not as empty scaffolding.
Use a separate generated output root so baseline FCStd files and links remain usable.
Reuse stable construction helpers where useful; avoid copying entire builders by default.

Persisted configuration is the reproducible source of design variants. FreeCAD
properties provide interactive previews. An explicit export/apply operation must
reconcile UI changes with configuration; do not imply that JSON updates itself.
Every public parameter needs units, ownership, geometric meaning, dependencies,
and a tested operating range. Until tested, ranges are unknown, not unlimited.
Keep kernel tolerances and measured coordinate data separate from design controls.
Do not tie two bore sizes together merely because their current values match.

## Acceptance of each refactor

- Default dimensions reproduce the accepted reconstructed component within an
  explicitly stated tolerance. Compare against this checkpoint, not just the STEP.
  Check critical mating surfaces separately; volume agreement alone is insufficient.
- Each intended control has a meaningful edit test: change it, verify the intended
  geometry and its neighboring interface, restore it, and reopen the saved result.
- Check solid validity, expected solid count, component placement, seated overlap
  and intended clearance. Treat failed Boolean operations as failed evidence.
- Confirm linked-assembly update behavior. Fixed placements are not a joint solver;
  edits that require repositioning need an explicit rule and test.
- Report unsupported input values clearly. A successful small edit probe does not
  establish a whole safe range or manufactured fit.
- Show baseline and candidate together at a completed-part checkpoint, with concise
  code excerpts and current line links. Keep the user involved in functional choices.

## How we measure improvement

Track supported design edits and whether they preserve interfaces; count the places
that must be changed for one intended adjustment; track duplicated interface data
and unexplained fixed coordinates. These are more useful than reducing face count.
The immediate goal is one definition for the stem/pocket relationship, with a
repeatable default build and verified clearance adjustment. We have not achieved
that refactor yet; the current checkpoint has independent measured descriptions.

## Current commands

Run from the playground using the pinned FreeCAD Python:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/mouse-hats/reconstruction/assembly/audit_checkpoint.py
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/mouse-hats/reconstruction/assembly/verify.py
```

The inventory reports saved-file state. The verifier opens linked files in a
separate process and restores temporary edit probes without saving source models.
A complete one-command clean rebuild of all six parts is still work to do: the
assembly builder currently requires the individual generated models to exist.

First mount-interface candidate now implemented: see ../model/README.md. Shared
bearing geometry and clearance probes pass; slope controls and broader variant
integration remain future work. Earlier sequence above records the overall plan.
