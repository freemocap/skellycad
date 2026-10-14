# Monocular rat targeted R03

This complete assembly restores the inherited mouse mounting relationship: the
unchanged tapered baseplate overlaps the rat skull as stock for a later Boolean
cut. R02's 3.6 mm dorsal lift is removed. The skull has not yet been cut from the
baseplate. Physical mounting fit remains provisional.

The camera is re-aimed at the same right-eye center, with its cradle, socket,
rectangular arms and fixed-length ribbon regenerated together. Source anatomy,
mouse R08 hardware and selected rat R01 remain unchanged. `recipe.json` records
those verified inputs and the explicit baseplate contact exception.

Run `open.FCMacro` through the existing FreeCAD window workflow in
[development.md](../../../../docs/development.md). It shows one dense skull and
one finished carrier. Alternative skull meshes, overlapping construction solids
and the nominal lens reference remain hidden. The colored eyes are retained.

Rebuild with the command in [the targeting workflow](../../../../docs/eye-tracker-targeting.md),
then inspect `validation.json` and `anatomy-containment.json` in the generated
R03 directory. Only baseplate/skull overlap is intentional; ribbon, camera,
carrier and holder must clear the anatomy. Review the uncut baseplate before
making a specimen-specific cut or claiming physical fit.
