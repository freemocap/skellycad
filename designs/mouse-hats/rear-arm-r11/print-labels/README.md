# R11 permanent print labels

A-E are embossed on the exterior back of the matching PCB tray, centered at
Y14.1/Z0 mm on backing plane X3.706774245. Arial Bold, normalized3.5mm glyph
height, relief0.4mm, embed0.05mm. Font path/hash and units saved in settings.json.
The letters avoid the PCB side, ventilation holes, stem, and accessories.

build.py reads the five validated R11 assembly snapshots, creates font wires,
faces with counters, extrudes outwards, fuses each letter into its carrier and
exports a carrier+holder STL. Source assemblies remain intact. Labeled FCStd files
are snapshots reproducible by the script, not separate editable font features.

Each labeled carrier passes deep solid checks; label material has zero overlap
with holder, clip, cap or baseplate. Joint gap remains0.331721863mm. Added volume
agrees with letter area*relief within0.002mm3 integration tolerance. Each STL has
two watertight consistently wound shells; hashes and reports accompany the ZIP.
Exterior-back review visually confirms letters A-E read correctly, not mirrored.

package.py (analysis Python) creates R11-A-E-labeled-STLs.zip under
 generated/mouse-hats/rear-arm-r11/labeled/ relative to playground. It contains
five individual STL units and print notes. Import as five separate objects and
use slicer arrange; preserve carrier/holder relative placement within each file.
No slicing, supports or print orientation imposed. Existing accessories unchanged.
show.py previews labels in FreeCAD; its offsets are display-only.
