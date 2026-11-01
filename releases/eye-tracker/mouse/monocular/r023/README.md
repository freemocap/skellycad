# Mouse R23 print pack with connected mandible

R23 adds both atlas mandible halves to the R22 four-color Snapmaker U1 anatomy print. It preserves the registered R22 skull, the R19 eyes, the raised baseplate and the 2.25 mm eye bridge. The selected complete eye-tracker assembly remains **ET-MOUSE-RAISED-TARGET-R19**. This is a new print derivative in millimeters; physical print strength and fit remain untested.

## Files to print

1. Open `anatomy/MOUSE-R23-Snapmaker-U1.3mf` as a project in Snapmaker Orca. Keep the four regions in one assembled object at **100% scale**. The baseplate is already embedded.
2. Assign the four regions to the actual rigid filaments loaded in the U1. The inherited project uses a 0.4 mm nozzle and four PLA profiles. Colors describe the model, not the loaded spool material.
3. Inspect the sliced layer preview and choose supports for the jaw, cheek arches and other overhangs. The three jaw connections are permanent model geometry; do not remove them as supports. Use care when removing support around the thin jaw.
4. If printing the eye-tracker hardware, use `hardware/MOUSE-R23-carrier-and-holder.stl` and `hardware/MOUSE-R23-camera-clip.stl`. Keep the carrier and holder shells together in their shared print-in-place pose. Keep supports out of their approximately 0.333 mm joint gap.

| U1 slot | Region | Display color |
| --- | --- | --- |
| 1 | Skull, eye bridge, both mandibles and jaw connections | Red |
| 2 | Corneas | Black |
| 3 | Sclerae | White |
| 4 | Baseplate | Yellow |

The portable four-color 3MF and individual STLs are alternatives. The `mouse-eyes-embedded-baseplate.stl` file is the monochrome union, including the jaw. Do not print the alternatives on top of the multipart project. The separate reference mandible meshes are provenance assets, not additional parts to print. As in R22, hardware exports exclude electronics, ribbon and camera case/cap. This pack contains no G-code.

## Anatomical source and print connections

The retained mouse CT atlas supplies both hemi-mandibles in the same image grid as the skull: right label 2 and left label 21, as identified by the retained upstream `main.R` [@magaMouseCTAtlasRepository]. Both use the exact NIfTI affine, RAS-to-LPS conversion and atlas-to-assembly similarity transform already used for R22. No independent translation, rotation, mirroring or rescaling of either jaw is applied. The inherited registration includes a uniform scale of approximately 1.07344. Its residuals are surface discrepancies, not demonstrated landmark accuracy.

This preserves the atlas jaw pose. It does not establish individual-animal fit, natural bite mechanics or a universally correct jaw posture. The original atlas, accepted checkpoints and R22 pack remain intact. Review scope: retained label definitions, segmentation contents, registration matrix, three-view mesh inspection and exported-volume checks. No new biological measurements or external anatomical estimates were introduced.

Each jaw print derivative retains its largest segmented component, closes one source voxel, fills enclosed holes, smooths at one source voxel (approximately 0.0353 mm before the inherited scale), and simplifies at 0.015 mm in source coordinates. Small disconnected surfaces and enclosed cavities are removed. The extraction report records their volumes. These operations produce printable surfaces rather than preserving microscopic internal anatomy.

Three rounded **1.2 mm diameter** connections join the two posterior superior jaw regions to the skull and join the jaw halves at the anterior midline. Their surface gaps are approximately 0.073, 0.080 and 0.044 mm. These are engineering connections, not anatomical tissue. Their exact endpoints and Boolean engagement volumes are in `jaw-connections.json`. Together they add approximately 0.750 mm³ outside the skull and jaw volumes. They fix the jaw in place; the model does not articulate.

## Validation and review

The skull-and-jaw region is one closed connected volume, including after export and reload. The full monochrome anatomy is also one connected volume. The four material regions have no positive-volume overlap above the 0.00001 mm³ check tolerance. The eyes and baseplate preserve their R22 geometry and relative placement; a common translation puts the lower jaw on the print bed. Hardware meshes remain byte-identical to R22, apart from filenames.

`anatomy-preview.png`, `jaw-side-view.png` and `jaw-front-view.png` show the exported print meshes. `jaw-registration-review.png` shows the separately colored jaw halves against the skull before connections. Reports and `manifest.json` accompany the pack. Closed geometry and a connected mesh do not establish successful printing, support removal or physical strength.

## Rebuild

From the repository root, run these scripts with `tools/cad/.venv/Scripts/python.exe` in order:

1. `designs/eye-tracker/mouse/print-r23/prepare_inputs.py` verifies the selected R19 checkpoint and R22 pack hashes, then copies the preserved eye/baseplate exports and matched hardware.
2. `designs/eye-tracker/mouse/print-r23/extract_mandibles.py` extracts the two jaw halves. It uses nibabel from the retained atlas-study dependency directory.
3. `designs/eye-tracker/mouse/print-r23/inspect_jaw.py` writes the registration comparison.
4. `designs/eye-tracker/mouse/print-r23/connect_jaw.py` creates and validates the connected skull-and-jaw solid.
5. `designs/eye-tracker/mouse/print-r23/build_anatomy.py` writes the four-color U1 project and checks exported geometry.
6. Run `designs/eye-tracker/mouse/print-r23/render.py` with Blender's background Python to produce the three review images.
7. `designs/eye-tracker/mouse/print-r23/package.py` verifies preservation, material assignments and hashes, then writes the ZIP.

Outputs go to `generated/eye-tracker/mouse/print-r23`. Stop if a verification fails. The rebuild does not change the selected assembly or overwrite R22.
