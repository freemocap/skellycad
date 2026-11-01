# Reinforced four-color rat skull: EB02

Open `generated/eye-tracker/rat/print-eye-bridge-r02/anatomy/RAT-R32-EB02-Snapmaker-U1.3mf`
as a project in the U1 slicer. The file is unsliced and retains the existing U1
0.4 mm nozzle, 0.2 mm layer, and four PLA material profiles.

The eye-support beam diameter increases from 2.25 to 3.375 mm (50%). This is
53.65% of the conservative 6.291 mm eye dimension, below the requested 70–80%
limit. Both sclera meshes are united with a continuous 2.4 mm white core.
Red skull material surrounds this core with a nominal 0.4875 mm radial sleeve
where the beam is outside the skull and eyes. The white core extends into both
eyes and through the skull, replacing the previous separate white eye bodies.

Material slots remain red skull (1), black cornea (2), white sclera and connecting
core (3), and yellow baseplate (4). The skull derivative, eye positions, corneas,
and lowered baseplate placement are retained. The previous print pack is preserved.

All exported meshes pass closed-mesh and self-intersection checks. The white
sclera is one connected volume; the four regions have no material overlap above
0.01 cubic millimetres. Tiny seam edges were collapsed with recorded, negligible
volume changes. These checks establish geometry validity, not measured print
strength or inter-material adhesion; those need the next physical trial.

Rebuild with the CAD tooling Python by running `build_anatomy.py`, then
`repair_edges.py`, then `finalize.py`, then `validate_u1.py`. Run `check_meshes.py`
and `repair_native.py` with the pinned FreeCAD Python. Each command must succeed
before using the regenerated project. Input hashes and complete-assembly lineage
are recorded in `lineage.json`; output hashes are in `final-files.json`.

Retain `LICENSE-source.txt` with the skull derivative: scienceminer's supplied
rat skull, Thingiverse 469391, Creative Commons Attribution Share Alike as supplied.
