# Maintained model: first mount interface candidate

**Start with [CURRENT.md](CURRENT.md): the canonical six-part working view.**


This is the first bounded refactor after reconstruction checkpoint 8709351.
Baseline part models and the six-part linked assembly remain unchanged.
The user confirms the existing fit works. Preserve that geometry; a demonstrated
control is not a reason to adopt a changed fit. Nonzero probes are tests only.

## Control

`Baseplate.PocketClearance` is an additional distance in mm normal to each of
TWO drafted bearing faces and their two entry faces. Positive values enlarge
these parts of the receiving pocket. The stem, floor, round relief, bore and
outer stock are fixed. This is not uniform clearance around the entire stem.
It is not a diametral allowance or a printer compensation recommendation.

The implementation currently permits 0 through 0.1 mm. Geometry probes passed
at 0, 0.025, 0.05, 0.075 and 0.1 mm; the continuous interval is not exhaustively
validated. Negative, above-limit and nonfinite values are rejected. If a GUI
recompute fails, do not trust a retained last-good shape; restore a valid value.

## Shared definition

`mount-interface.json` owns the two bearing plane normals and stem offsets,
plus tiny nominal pocket allowances and the measured entry planes. These feed
both the stem section vertices and baseplate pocket. The approximately 8e-8 mm
positive-side residual is retained from reconstruction, not meaningful print clearance.
`mount_interface.py` solves the affected stem vertices on those planes and adds
clearance to pocket offsets. Remaining measured profiles are reused from reconstruction.

Only pocket allowance is live. Plane orientations and other dimensions are build
inputs, and slopes are NOT yet supported interactive controls. Changing slopes
would require updating adjoining geometry and testing it. This first step does
not claim a fully parameterized stem, insertion-path validation, or assembly joints.

The candidate reuses the existing baseplate construction kernel and tray builder.
The tray builder gained an optional profiles_data input; its default remains the
original measured JSON. Existing baseline outputs are never saved by this workflow.

## Run

From the playground, with the pinned FreeCAD Python:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/mouse-hats/model/build_mount.py
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/mouse-hats/model/verify_mount.py
```

The default candidate is generated/mouse-hats/model/mount/mount-fit.FCStd at zero
clearance. Run `open_mount.py` inside FreeCAD for a separate saved review at zero added clearance,
with a fixed gold checkpoint comparison and cyan stem inspection section. The
section is an inspection snapshot, not another manufactured part. The review
opens with Baseplate selected so its Mount fit / PocketClearance property is available.
Use build_mount.load_modules() before reopening these scripted candidate files.

The CAD document embeds the measured data and interface for recomputation. Editing
its property saves to FCStd only; it does not change JSON or the zero-clearance build
default. A full variant configuration/export workflow is still future work.

## Evidence

See validation-baseline.json. At zero allowance, tray and baseplate each show zero
missing/excess volume against checkpoint models at 0.001 mm Boolean tolerance.
Tray volume differs by about 4e-10 mm3 after resolving vertices from shared planes.
Every clearance probe passes deeper solid checks, has zero seated stem overlap,
adds no baseplate material and removes material monotonically. The actual planar
bearing faces agree with requested offsets within 1e-7 mm. Edit/restore and saved
0.05 mm candidate reopen/recompute pass. At 0.05 mm, 1.75065 mm3 is removed.
All six baseline FCStd hashes were checked unchanged after the review was created.

This candidate is not yet substituted into the six-part assembly. Physical fit,
retention, hardware dimensions and insertion path are not established by these tests.
Next: review the control, then add variant persistence and integrate verified controls
before moving on to tray/cap board-envelope and retention dimensions. Mesh fixes deferred.

## Requested lip trim (pending location confirmation)

User requests removing the two projecting shoulder corners they previously snipped
by hand, with cuts parallel to the stem. preview_lip_trim.py highlights a proposed
4.686875 mm3 removal in red, finishing flush with the flat stem sides. This is a
separate inspection proposal, not an applied change to the working assembly. Confirm
the highlighted locations/cut depth with the user before promoting the trim.

## Confirmed lip edit (current)

User confirmed the two highlighted corner snips, then canceled the front extension.
Only the corner trims remain. build_lip_trim.py produces native Common/Cut features;
TrimmedTrayAndMount is the final solid. The front, stem and baseplate are unchanged.
PocketClearance is zero. Output: generated/mouse-hats/model/lip-trim/trimmed-mount.FCStd.
The displayed section is an inspection aid. Extension geometry and highlight have
been removed from the saved candidate. Source assembly remains unchanged.

Checks: one valid solid, no added material, zero seated baseplate overlap, preserved
stem region Y<4.999 mm by Boolean differences at 0.001 mm tolerance. Corner tool
volume is 4.686875 mm3; volume accounting tolerance is 1e-5 mm3.
