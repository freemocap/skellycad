# Mouse-hats reconstruction â€” first-pass checkpoints

The visually accepted assembly is checkpoint `8709351`. See [DEVELOPMENT.md](DEVELOPMENT.md)
for the next phase: control inventory, shared stem/pocket geometry, then tray/cap controls.
The saved-file audit records 12 existing length controls across six parts.

Approved source: 58 STEP. User has visually accepted the clip, holder, socket,
tray/stem and baseplate candidates and requested continuation. This is not physical
fit acceptance or a waiver of the recorded geometric discrepancies. User also
visually accepted the cap and authorized assembly consolidation. Old arm reconstruction and later mesh work are deferred.

| Part folder | Implementation | Main qualification |
| --- | --- | --- |
| camera_clip | Native sketches/lofts | Recorded whole-clip Boolean agreement |
| camera_holder | Native geometry | Analytic root blend; sampled deviation up to 0.058823 mm |
| socket | Native revolve/collar | Approximated measured profile; source BOP errors |
| main_carrier | Native features plus tolerance-union proxy | Tray/stem only; old arm omitted; measured profile detail retained |
| baseplate | Scripted parametric feature | Uncut alternative; small source pocket-mouth cap omitted; sampled deviation 0.200219 mm |
| pcb_cap | Native sketches/extrusions/holes | Surface samples and common volume agree; reverse Boolean difference invalid |

Read each folder's README and validation record. Generated FCStd files are under
generated/mouse-hats/reconstruction. For scripted parts, use their open_model.py
loaders so the feature modules are available for recomputation. Scripts, measured
parameters and evidence live here; supplied originals are preserved under old/.

The assembly folder now supplies six live external links in original 58 placements.
Use assembly/open_model.py to open it. Fresh reopen, placement checks, two live edit
propagation checks and all 15 pairwise seated-overlap checks pass. See its README.
Next: review this assembly and define functional edit controls. Do not reintroduce
old-arm reconstruction or the two-arm mesh phase without the user's direction.
