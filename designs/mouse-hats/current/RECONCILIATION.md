# Baseline reconciliation — 2026-10-11

The skull work incorrectly treated the original R11B arm selection as the latest
complete model. The supplied R02 STL therefore omitted subsequent PCB retention
changes. It has been superseded and moved out of the live output folder.

Both source chats were read:

- **Design an original 3D shape**: user chose B as in Buffalo; establishes R11B arms.
- **Design an original 3D shape - pcb spring catch**: user chose +1 mm height, then
  requested the relocated/wider catch and deeper cap grip (T2), followed by the
  raised tray rail (T3). T3 was its final delivered revision. Source turn and chat
  IDs are recorded in inputs.json. No additional physical test result is inferred.

The current request explicitly directs using that latest PCB model. T3's complete
tray and matching cap are now integrated with the eye/ribbon study. Whole-shape
coincident Boolean differences gave unreliable results on the historical shapes;
the integration instead retains exact T3 tray geometry and replaces only the arm
region across straight root sections. All source geometry remains preserved.

The current export contract checks the revision ID, checkpoint hash, catch, rail
and PCB clearance. Independent mesh checks validate the carrier/holder two-shell
pair and each one-shell accessory. This avoids selecting whichever old document
happens to be open or whichever isolated study has the largest revision number.

## Cleanup performed

- One current/ folder contains the manifest, durable checkpoint, source snapshot,
  build/export scripts and validation.
- Current prints live only in generated/mouse-hats/active/print/.
- Earlier HANDOFF/TRANSFER/README/AGENTS/CURRENT texts are archived with hashes in
  ../archive/2026-10-11-baseline-reconciliation/.
- Root/project instructions and historical CURRENT entry point now route to the
  single manifest; skull-neutral R01/R02 are explicitly superseded as assemblies.
- The wrong STL is quarantined, and its obsolete exporter refuses to run.
- Historical geometry and source folders stay in place because scripts contain
  relative imports and recorded paths. INDEX.md classifies them; no source loss.

No commit, push, printer submission, or messages to other chats were performed.
