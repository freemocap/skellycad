# Observed failures and next changes — 2026-10-09

User reports practical failures and earlier manual mesh fixes. The accepted arm
finishing candidate remains unchanged during this inspection/planning step.

## Priority order

1. **Stem-to-tray junction**, circled in the user's side-view screenshot. Add a
   gradual local reinforcement at the taper into the backing. Preserve the stem
   mating faces, baseplate seating lip and PCB/cap clearances. Inspect the seated
   baseplate before selecting a rib/blend footprint. Backing thickness is
   5.287064 - 3.706774 = 1.580290 mm. This is the backing thickness, not a complete
   measure of the irregular stem junction or a strength estimate.
2. **Camera-holder walls.** User reports walls breaking and thickened them in mesh.
   Baseline rail thickness is approximately 1 mm on both sides. Prefer outward
   reinforcement while preserving board seating, ribbon passage and clip fit;
   exact walls/segments still need visual identification with the holder shown.
3. **Ball neck and matching socket.** User thickened the neck and saw binding.
   Baseline ball radius is 2 mm; toroidal neck major/minor radii are about 4/3 mm
   (nominal narrow radius about 1 mm before trims). Redesign as a coupled interface,
   not a global scale: neck, ball, socket cavity/opening, collar and arm attachment
   boundaries must remain compatible. Verify actual holder motion, not just an
   empty ball-seat sphere. Preserve sensor/clip features and fastener dimensions.
4. **Weight reduction.** User proposes another tray hole or longitudinal rounded
   slot, and an opening in the raised cap region over the connector. Choose openings
   after reinforcement and keep material around the stem load path, arm roots,
   locating features and connector/cable protection. Track added/removed solid
   volume by feature. Printed mass depends on material and toolpaths; increased
   open area does not by itself establish improved operating temperature.

User clarified: failures happened during support removal. Support adjustments
helped, but user wants the exposed weak points reinforced as well.

## REJECTED first candidate: raised stem patch

`build_stem_reinforcement.py` now creates a separate full-carrier candidate from
the accepted arm finish. `stem-reinforcement.json` defines a 6 mm wide rear patch,
0.6 mm extra thickness, beginning at Y=8.3 mm within the stem and tapering from
Y=10.5 to 12.5 mm into the backing. Exposed longitudinal patch corners have R0.3
rounds. The PCB-facing surface and all seated stem material below Y=6 stay intact.

Output: `generated/mouse-hats/arms/stem-reinforced/stem-reinforced-carrier.FCStd`.
Final feature `ReinforcedCarrier` includes the arms and their fillets. Gold
`AddedMaterial` is an inspection overlay only, not an additional printable part;
it must be refreshed if the reinforcement control is edited. Export the final
feature alone. Load `stem_reinforcement_features`, `arm_finish_features` and
`attachment_arm_features` before reopening for edits.

Checks: one valid solid, deeper geometry check passes, added 10.1611 mm³, removed
zero; full candidate has zero cap/baseplate overlap at 0.001 mm tolerance. No
addition in the seated region or on the PCB side. Fresh reopen and 0.6 -> 0.5 ->
0.6 mm edit/restoration pass. Reports are alongside the generated file.
This demonstrates geometric compatibility, not a measured strength increase.

User rejected this patch as an abrupt, poorly blended addition. Keep it only as
history; it is not the current reinforcement candidate.

## Replacement: direct stem-to-tray blend

`build_stem_blend.py`, `stem_blend_features.py` and `stem-blend.json` replace the
pad with a **3 mm radius concave fillet directly on the original junction**.
It is tangent to the existing stem slope and tray rear plane. There is no raised
pad, 0.6 mm thickness step, or independent overlay geometry. Measured surface
normal mismatch at both main transition edges is zero degrees at their midpoints;
see `verify_stem_blend_tangency.py` and generated `tangency-validation.json`.

Output: `generated/mouse-hats/arms/stem-blend/stem-blended-carrier.FCStd`.
Run `show_stem_blend.py` in the live GUI to open it. `BlendedCarrier` is the whole
printable candidate. `RootBlendRadius` controls the junction radius. Source edge
selection uses its measured center and width, not a persistent edge number.

One valid solid; deeper geometry check passes. Added 0.913429 mm³; removed zero
at 0.001 mm Boolean tolerance. Zero cap/baseplate interference; no added material
in the seated stem region or on the PCB side, and no changes outside the local
root region. Fresh reopen, R2 edit and R3 restore pass. This is a local stress
concentration treatment, not the previously proposed 0.6 mm backing thickening;
no measured strength increase is claimed. Original arm-finishing file unchanged.

Enlarged ball/socket, holder walls and openings remain pending. Neither CURRENT
nor the accepted arm-finishing checkpoint was overwritten. Next review this stem
patch, then identify the holder wall sections to reinforce before resizing the
ball/neck/socket together. Holder pose and print evaluation remain pending.
