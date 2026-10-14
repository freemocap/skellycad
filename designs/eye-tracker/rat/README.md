# Monocular rat

**Binocular exploration: [concept study R01](binocular-study-r01/README.md).** Three back-to-back board and removable-cover options; not print designs.

**Print pack: [RAT R04](print-r04/README.md).** Connected eyes, embedded-baseplate anatomy, four-color U1 project, and labeled matched camera hardware.

**New review: [targeted R03](targeted-r03/README.md).** Restores intentional baseplate/skull overlap for a later Boolean cut and hides overlapping construction geometry. Uses the aligned dense skull and colored eyes, measured mouse R08 camera, solved ribbon, and regenerated supports aimed at the right-eye center. The selected R01 checkpoint below remains preserved.

**Selected checkpoint: ET-RAT-MONO-R01.** This complete assembly replaces mouse
anatomy with the supplied rat skull and mandible. It reuses the shared R10
carrier, holder, cap, clip and inherited mouse baseplate at their original
dimensions and relative positions. Rat mounting fit and camera aim are not
established; this is the starting point for anatomical review.

## Open and rebuild

Run `open.FCMacro` in the existing desktop FreeCAD session. It opens the selected
checkpoint without closing the mouse or other documents. The document is named
**Monocular rat**. The skull and mandible form one reference mesh. The orange
marker is a provisional orbital target; the red line is the unchanged mouse
camera sightline. No rat eyeball or pupil geometry is claimed.

`assembly.json` selects one eye camera and the shared `r10-monocular` mount.
`anatomy.json` selects the rat reference and inherited baseplate. Run `build.py`
inside the pinned FreeCAD GUI Python context to rebuild into
`generated/eye-tracker/rat/monocular-r01/`. It does not overwrite the selected
checkpoint. The PCB remains an approximate fit envelope until measured camera
geometry is supplied.

For an isolated build, hardware comparison and saved-file check, run from the
repository root in PowerShell:

```powershell
$env:FREECAD_USER_HOME = Join-Path (Get-Location) '.cad-tools/validation-profile'
& '.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe' tools/cad/validate_rat.py
```

The validator opens a hidden GUI and leaves the desktop session intact. Its
report and preview go to `generated/eye-tracker/rat/monocular-r01/`.
`validation/monocular-r01.json` records the selected checkpoint's checks.

## Skull source and registration

[Rat skull + mandible](https://www.thingiverse.com/thing:469391) by **scienceminer**,
supplied in `Rat skull + mandible - 469391.zip`. The creator describes a microCT
scan processed with Mimics, Magics and 3-matics. The supplied license states
**Creative Commons — Attribution — Share Alike**, without a version number.
Original files, README, license and archive remain unchanged under
`references/skull/thingiverse-469391/`. Retain that attribution and license with
the scan and derived reference geometry; this note does not relicense the scan.

The selected `9_19_14_rat_skull.stl` has 110,116 triangles and passes the
trimesh watertightness check, with 31 connected components. The two other
variants fail that check. Nothing has been repaired, joined, simplified or
removed. Watertightness does not establish anatomical accuracy or printability.

STL and the supplied notes do not establish units. R01 assumes one coordinate
unit is one millimetre: the source spans approximately 46.74 × 23.32 × 24.44 mm.
Scale stays 1.0 and needs confirmation against a known specimen dimension.

The registration maps source coordinates to the inherited hardware frame:

```text
assembly (x, y, z) = (source x + 12, -source z - 2, source y)
```

This is a 90° rotation around X and translation of (12, -2, 0) mm. Rostral is
approximately +X, dorsal +Y, and lateral Z. The posterior cranium is positioned
below the inherited plate by visual comparison, not measured mounting landmarks.
The target at (13, -10, 9) mm is a visual orbital-region estimate. Source hashes,
mesh audit and registration rationale are in `references/skull/provenance.json`.
`prepare_reference.py` reproduces the registered anatomy into `generated/`
without overwriting the frozen reference.

The inherited sightline passes about 8.6 mm from that provisional target. This
is a review diagnostic, not a measured aiming error or a prescribed arm offset.

## Next design steps

[User-aligned skull frame](references/skull/aligned-r01/README.md) contains the
recovered rigid transform, preserved dense STL variants and colored-eye review.
It uses +X nose, +Y left and +Z up. This separate study does not change the selected
R01 hardware assembly's older coordinate frame.

[Schematic rat-eye STLs](references/eyes/README.md) provide three literature-grounded
exterior models for manual placement. They are separate review assets; the selected
R01 assembly still contains its original provisional marker and no eyeball mesh.

1. Confirm skull scale, mounting position and eye target in this monocular assembly.
2. Use the forthcoming camera sketches and dimensions for a proper shared camera
   profile: PCB, mounting interfaces, sensor/lens position and cable exit.
3. Revise the arms and holder pose around those measured interfaces and the rat
   target. Recheck matched-part clearances and the route around the skull.
4. Create a separate binocular variant, with two eye cameras and a central
   holder accommodating back-to-back PCBs. Review physical camera handedness
   before mirroring printed geometry.

R01 contains one camera only. It does not implement the binocular holder or claim
clearance through the skull, soft tissue, ribbon or full sensor/lens body.

[Collection overview](../README.md) · [Shared hardware](../shared/README.md)
