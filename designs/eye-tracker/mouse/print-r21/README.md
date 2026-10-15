# Mouse R21 print pack

Print candidate derived from the selected **ET-MOUSE-RAISED-TARGET-R19** complete assembly. Units are millimeters. The accepted R19 checkpoint and its selection remain unchanged.

## Files to print

- `anatomy/MOUSE-R21-Snapmaker-U1.3mf`: four-material skull, eyes and embedded baseplate. Open as a project in Snapmaker Orca. Keep the four regions in one assembled object at 100% scale.
- `hardware/MOUSE-R21-carrier-and-holder.stl`: matched carrier and ball holder in their print-in-place relationship. Keep both shells together at 100% scale; do not independently arrange them.
- `hardware/MOUSE-R21-camera-clip.stl`: separate camera retention clip.

The hardware excludes the real camera, PCBs, ribbon, optical axes and camera case/cap. The skull project includes the baseplate, so do not add another copy of that baseplate.

| U1 slot | Region | Display color |
| --- | --- | --- |
| 1 | Skull and connecting bridge | Red |
| 2 | Corneas | Black |
| 3 | Sclerae | White |
| 4 | Baseplate | Yellow |

The project uses four PLA profiles. Assign each region to the actual rigid filament loaded in your printer; if your yellow spool is TPU, use another PLA spool for the baseplate or explicitly change the material profile before slicing. Display colors do not identify the loaded material.

The portable `MOUSE-R21-four-colors.3mf` and individual region STLs are alternatives. STL files do not store colors. `mouse-eyes-embedded-baseplate.stl` is the monochrome union; `mouse-eyes.stl` is the monochrome skull and eyes without the baseplate. Do not print these alternatives on top of the four-part project.

## Geometry and provenance

The new skull uses the retained atlas bone segmentation and the existing atlas-to-assembly registration [@magaMouseCTAtlasRepository; @maga2017MouseSkullAtlas]. Review scope for this revision: local segmentation, registration matrix, existing design records and mesh checks; no new anatomical inference. A print-only derivative retains the largest connected bone component, removes 571 isolated voxels, applies one voxel of binary closing and simplifies at 0.01 mm in source coordinates. The supplied atlas and accepted CAD checkpoints are preserved. Source license and segmentation accompany the pack.

The eyes retain the R19 geometry and placements. The baseplate retains the accepted raised, surface-aligned R18/R19 placement. The connecting cylinder follows the two eye centers and has a **2.25 mm diameter**, 25% smaller than the 3 mm diameter in mouse print R20. It belongs to the skull region. Material boundaries are Boolean-trimmed to avoid positive-volume overlaps.

The carrier and holder retain their matched pose and approximately 0.333 mm minimum CAD gap. Both receive the same rigid print transform. The clip is exported separately. Mesh validation establishes closed geometry, not successful physical fit or freedom of movement after printing.

## Slicing and validation

These files are unsliced. Confirm the U1 nozzle and filament profiles, inspect the layer preview, and choose supports for the skull and hardware as needed. Keep support material out of the ball-joint clearance. Do not enable geometry merging that closes the joint gap. Check the four part-to-filament assignments before sending the job.

`anatomy-validation.json`, `skull-derivative.json` and the hardware reports record the geometry checks. `manifest.json` records file hashes. The pack contains no G-code.

## Rebuild

From the repository root, run `export_cad.py` with the pinned FreeCAD Python runtime, then `prepare_skull.py`, `build_anatomy.py` and `package.py` with the CAD tools Python environment. The preparation step also uses nibabel from the retained atlas-study dependency directory. `open.FCMacro` creates the optional native review document in the existing desktop FreeCAD session. Generated outputs go to `generated/eye-tracker/mouse/print-r21`.
